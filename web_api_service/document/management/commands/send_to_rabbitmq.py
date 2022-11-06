import os
import datetime
import time
import requests
import json

from django.db.models import Q

from document_processing import settings
from django.core.management.base import BaseCommand, CommandError
from document.models import *
from document.utils import *
from document.rabbitmq_client import RabbitmqClient
from document.management.commands.services import remove_cron_lock_file, \
    create_cron_lock_file, check_if_exists_cron_lock_file


class Command(BaseCommand):
    args = ''
    help = 'Export data to remote server'

    def handle(self, *args, **options):

        # Lock filename
        lock_filename = 'tesseract_ocr.lock'
        # Folder cron_lock
        cron_lock_folder = os.path.join(settings.BASE_DIR, 'cron_lock')
        if not os.path.exists(cron_lock_folder):
            os.mkdir(cron_lock_folder)

        # Path to lock file
        path_to_cron_lock_file = os.path.join(cron_lock_folder, lock_filename)
        # Check lock file
        check_if_exists_cron_lock_file(path_to_cron_lock_file)

        # RUN PROGRAM
        print("Program is running")

        documents = Document.objects.filter(Q(is_active=True, is_processed=False, status_id=8) | Q(is_active=True, is_processed=False, status_id=9))

        if documents:
            print('===========================================')
            print(datetime.datetime.now())
            print('Start sending pages to Adygzhy...')

        # Config for RabbitMQ
        rabbitmq_cfg = {
            "host": "89.223.95.49",
            "port": 5672,
            "user": "dueva",
            "password": "n3dF8dfXpweZv",
            "exchange": "doc-analysis"
        }
        url = 'http://89.223.95.49:8887/upload'


        print('Try to connect to RabbitmqClient...')
        # создаем клиента
        rabbitmq_client = RabbitmqClient(rabbitmq_cfg)

        for document in documents:

            # Get pages for specific document
            pages = Page.objects.filter(document_id=document.id, is_sent_to_server=False)

            cnt = 0
            pages_array = []

            for page in pages:
                cnt += 1
                # Full path to image
                jpeg_path = page.page_image.path
                print(jpeg_path)

                # Send to Adygzhy
                files = {'media': open(jpeg_path, 'rb')}
                response = requests.post(url, files=files)
                json_string = response.text
                print('Adygzhy json:')
                print(json_string)
                json_data = json.loads(json_string)
                page_link = json_data[0]['link']
                page_id = json_data[0]['page_id']
                doc_id = json_data[0]['doc_id']
                
                # Update DB
                page.page_link = page_link
                page.page_id = page_id
                page.doc_id = doc_id

                page.is_sent_to_server = True
                
                page.save()

                pages_array.append({
                    "page_id": page.id,
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
