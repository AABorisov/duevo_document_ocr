import pika
import json


class RabbitmqClient:

    def __init__(self, rabbitmq_cfg):
        self.rabbitmq_config = rabbitmq_cfg
        self.connection = self._get_connection()

        # NOTE: we use only one channel for everything
        # Interesting link: https://stackoverflow.com/questions/18418936/rabbitmq-and-relationship-between-channel-and-connection
        self.channel = self.connection.channel()

    def _get_connection(self, heartbeat=0):
        user = self.rabbitmq_config["user"]
        host = self.rabbitmq_config["host"]
        port = self.rabbitmq_config["port"]
        password = self.rabbitmq_config["password"]
        credentials = pika.PlainCredentials(user, password)

        # Maybe you want to set 'heartbeat' parameter to 0 (== disable heartbeat)
        # The default heartbeat=None to accept broker's value, which is usually 60 seconds.

        # UPD: disable heartbeat (default value of heartbeat parameter == 0)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, heartbeat=heartbeat, port=port, credentials=credentials)
        )
        return connection

    def send_msg(self, msg):
        #routing_key = self.rabbitmq_config['routing_key']
        exchange = self.rabbitmq_config['exchange']

        self.channel.basic_publish(exchange=exchange,
                                   routing_key='', # у нашего exchange тип fanout, так что routing key is ignored
                                   body=msg,
                                   properties=pika.BasicProperties(
                                       delivery_mode=2,  # make message persistent
                                   )
                                   )

    def close_connection(self):
        self.connection.close()


if __name__ == '__main__':
    rabbitmq_cfg = {
        "host": "89.223.95.49",
        "port": 5672,
        "user": "dueva",
        "password": "n3dF8dfXpweZv",
        "exchange": "doc-analysis"
    }
    # создаем клиента
    rabbitmq_client = RabbitmqClient(rabbitmq_cfg)

    # Например, у нас есть такой документ для обработки:
    doc = {
        "doc_id": 1,
        "pages": [
            {
                "page_id": 1,
                "link": "<link of the first page.jpg>"
            },
            {
                "page_id": 2,
                "link": "<link of the second page.jpg>"
            }
        ]
    }
    # скорее всего, удобно будет отправлять сообщения в формате JSON, так что
    rabbitmq_client.send_msg(json.dumps(doc))
    # после этого по адресу http://89.223.95.49:15672/#/queues (dueva / n3dF8dfXpweZv)
    # можно увидеть, что сообщения дошли в очереди image-analysis-queue (обработка всяких схем, картинок, чертежей)
    # и text-analysis-queue (текстовый анализ). Наш exchange "doc-analysis" типа 'fanout',
    # так что автоматически шлет сразу в две подключенные очереди.

    # в конце работы закроем соединение
    rabbitmq_client.close_connection()
