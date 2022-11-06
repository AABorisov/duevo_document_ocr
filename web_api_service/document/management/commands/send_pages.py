from django.core.management.base import BaseCommand, CommandError
from pdf2image import convert_from_path
from document.models import *
from document_processing import settings
import os
import datetime
import magic
import requests
import json
from document.utils import *
from document.rabbitmq_client import RabbitmqClient


class Command(BaseCommand):
    args = ''
    help = 'Export data to remote server'

    def handle(self, *args, **options):
        
        documents = Document.objects.filter(is_active=True, is_processed=False)
        if documents:
            print('===========================================')
            print(datetime.datetime.now())
            print('Start uploading pages ...')
        page_short_path = 'pages/'
        # Creates pages dir
        pages_path = os.path.join(settings.MEDIA_ROOT, 'pages')
        # Config for RabbitMQ
        rabbitmq_cfg = {
            "host": "89.223.95.49",
            "port": 5672,
            "user": "dueva",
            "password": "n3dF8dfXpweZv",
            "exchange": "doc-analysis"
        }
        print('RabbitmqClient connect')        
        # создаем клиента
        rabbitmq_client = RabbitmqClient(rabbitmq_cfg)
        print('RabbitmqClient connect')
        if not os.path.exists(pages_path):
            os.mkdir(pages_path)

        for document in documents:
            document_id = str(document.id)
            # Work with PDF
            print('Start PDF convert')
            pages = convert_from_path(document.document_path.path, 150)
            print(pages)
            # Initiate vars
            cnt = 0
            pages_array = []
            doc = {}
            for page in pages:
                cnt += 1
                last_page_id = str(get_nextautoincrement(Page))
                print('LAST PAGE ID: ' + last_page_id)
                print('DOC ID: ' + document_id)
                new_page_name = document_id + '_' + last_page_id + '.jpeg'
                jpeg_path = os.path.join(pages_path, new_page_name)
                page.save(jpeg_path, 'JPEG')
                print('NEW PAGE NAME: ' + new_page_name)

                # Send to Adygzhy
                url = 'http://89.223.95.49:8887/upload'
                files = {'media': open(jpeg_path, 'rb')}
                response = requests.post(url, files=files)
                json_string = response.text
                print('Adygzhy json:')
                print(json_string)
                json_data = json.loads(json_string)
                page_link = json_data[0]['link']
                page_id = json_data[0]['page_id']
                doc_id = json_data[0]['doc_id']

                # Save page to DB
                page_db = Page.objects.create(

                    document_id=document.id,
                    status_id=1,
                    original_name=new_page_name,
                    page_number=cnt,
                    page_image=page_short_path + new_page_name,
                    # response info
                    page_link=page_link,
                    page_id=page_id,
                    doc_id=doc_id,
                    is_sent_to_server=True

                )
                page_db.save()

                pages_array.append({
                    "page_id": page_db.id,
                    "link": page_link
                })

            # Например, у нас есть такой документ для обработки:
            doc = {
                "doc_id": document.id,
                "pages": pages_array
            }
            print(doc)
            # скорее всего, удобно будет отправлять сообщения в формате JSON, так что
            rabbitmq_client.send_msg(json.dumps(doc))

            document.is_processed = True
            document.status_id = 2
            document.save()

        # в конце работы закроем соединение
        rabbitmq_client.close_connection()
