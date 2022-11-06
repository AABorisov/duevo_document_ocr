import os, io, json, requests
from doc.ocr import GoogleOCR
from doc.api import Classifier
from doc.parser import Parser
from config import ConfigProcessor
from amqp_processor import AmqpProcessor
#from pgdb import PostgreSqlDatabase
from mysqldb import MySqlDatabase
import pandas as pd


STORAGE_PATH = None
parser = None


def generate_general_attributes_dict(text_attributes_dict, ocr_ids_dict):
    res = dict() # {"attr_name": {"text": text, "ocr_ids": [ocr ids]}}
    for attr_name, attr_text in text_attributes_dict.items():
        print(type(attr_text))

        if type(attr_text)==str and attr_text != '':
            if attr_name not in res:
                res[attr_name] = dict()
            res[attr_name]['text'] = attr_text
        elif type(attr_text)==tuple and len(attr_text) == 2:
            if attr_name not in res:
                res[attr_name] = dict()
            res[attr_name]['text'] = attr_text[0]
            res[attr_name]['ocr_ids'] = attr_text[1]

    for attr_name, ocr_ids_list in ocr_ids_dict.items():
        if type(ocr_ids_list)==list and len(ocr_ids_list) > 0:
            if attr_name not in res:
                res[attr_name] = dict()
            res[attr_name]['ocr_ids'] = ocr_ids_list

    for attr_name in res:
        if 'ocr_ids' not in res[attr_name]:
            res[attr_name]['ocr_ids'] = None
        if 'text' not in res[attr_name]:
            res[attr_name]['text'] = None

    return res


def nlp_status(nlp_defined_attrs_count, doc_class_id):
    max_counts = { # doc_class_id => max count of nlp attributes
        1: 8,
        2: 13,
        5: 4
    }
    if doc_class_id not in max_counts:
        return None
    if nlp_defined_attrs_count > max_counts[doc_class_id]:
        # Error! Maybe, you have to redefine @max_counts!
        return None

    defined_attr_percentage = int((nlp_defined_attrs_count / max_counts[doc_class_id]) * 100.0)
    if defined_attr_percentage < 70:
        return 5
    elif 70 <= defined_attr_percentage <= 95:
        return 6
    else:
        return 7


def create_callback(ocr, classifier, mysql_db):

    def callback(channel, method, properties, body):
        in_msg_dict = json.loads(body.decode())
        print('msg_dict =', in_msg_dict)

        doc_id = in_msg_dict['doc_id']
        doc_pages = in_msg_dict['pages']

        # I. OCR
        ocr_dfs = []
        for page in doc_pages:
            page_id = page['page_id']
            img_link = page['link']
            filename = img_link.split('/')[-1]

            # 1. Download image to local storage
            local_img_path = os.path.join(STORAGE_PATH, filename)
            with open(local_img_path, 'wb') as handle:
                response = requests.get(img_link, stream=True)

                if not response.ok:
                    print('NOT RESPONSE OK! Failed to download image by link=', img_link)
                    #channel.basic_ack(delivery_tag=method.delivery_tag)
                    raise RuntimeError('Failed to download image by link=', img_link)
                    return

                for block in response.iter_content(1024):
                    if not block:
                        break

                    handle.write(block)

            # 2. OCR
            with io.open(local_img_path, 'rb') as image_file:
                content = image_file.read()
                resp = ocr.detect(content)
            ocr_data_df = ocr.postprocess(resp)
            if len(ocr_data_df) == 0:
                continue
            # Write to db
            ocr_ids = mysql_db.write_ocr_result(doc_id, page_id, ocr_data_df)
            ocr_data_df = ocr_data_df.assign(ocr_id=pd.Series(ocr_ids))

            ocr_dfs.append(ocr_data_df)

        # II. Classifier
        ocr_csv_paths = []
        for idx in range(len(ocr_dfs)):
            ocr_df = ocr_dfs[idx]
            ocr_csv_path = os.path.join(STORAGE_PATH, "{}.csv".format(idx))
            ocr_df.to_csv(ocr_csv_path)
            ocr_csv_paths.append(ocr_csv_path)
        doc_class_id = int(classifier.classify_document(files=ocr_csv_paths))
        print('doc_class_id=', doc_class_id)
        if doc_class_id is None:
            mysql_db.write_doc_classification_result(doc_id, 6)
        else:
            mysql_db.write_doc_classification_result(doc_id, doc_class_id)

        # III. parse attributes
        try:
            # 1. identify nlp attrs
            text_attributes_dict, ocr_ids_dict = parser.parse(ocr_csv_paths, doc_class_id)
            print('text_attributes_dict:', text_attributes_dict)
            print('ocr_ids_dict:', ocr_ids_dict)
            general_attrs_dict = generate_general_attributes_dict(text_attributes_dict, ocr_ids_dict)
            print('general_attrs_dict=', general_attrs_dict)

            # 2. Update document table
            status = nlp_status(len(general_attrs_dict), doc_class_id)
            if status is not None:
                mysql_db.update_status_in_document_table(doc_id, status)
            else:
                print("ERROR: status is NONE for doc_class_id=", doc_class_id, ", defined attrs count=", len(general_attrs_dict))

            # 3. write to db
            mysql_db.write_nlp_attributes(doc_id, doc_class_id, general_attrs_dict)

        except NotImplementedError:
            print('parse does not works for type:', doc_class_id)

        # Deliver message ack
        channel.basic_ack(delivery_tag=method.delivery_tag)
        print('finished')

    return callback


if __name__ == '__main__':
    cfg_path = './config/dev.json'
    # 1.
    config_processor = ConfigProcessor(cfg_path)
    cfg = config_processor.get_configs()
    print(cfg)

    STORAGE_PATH = cfg['local_storage_path']

    # 2. RabbitMq
    amqp_processor = AmqpProcessor(cfg['rabbit_mq'])

    # 3. DB
    mysql_db = MySqlDatabase(cfg['mysql'])

    # 4. Ocr
    ocr = GoogleOCR(key_json_path='./config/utm-06942e453718.json')
    classifier = Classifier()

    # parser
    parser = Parser()

    # 5. Start to listen incoming messages
    try:
        channel = amqp_processor.establish_connection(create_callback(ocr, classifier, mysql_db))
        channel.start_consuming()
    except:
        mysql_db.close()
        amqp_processor.close_connection()
        # re-raise the last exception (maybe useful for Docker container!)
        raise

    print('END')

