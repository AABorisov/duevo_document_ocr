import os
import time
import magic
import requests
import datetime
import json

from document.management.commands.services import check_if_exists_cron_lock_file
from document.models import *
from document_processing import settings
from document.utils import *
from document.tesseract_services import *
from document.ocr_module.main import *
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    args = ''
    help = 'Export data to remote server'

    def handle(self, *args, **options):
        """ documents = Document.objects.filter(
            Q(is_active=True, is_processed=False, status_id=8) | Q(is_active=True, status_id=10))
        """

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

        documents = Document.objects.filter(is_active=True, is_processed=False, status_id=11)

        for document in documents:

            document_type_id = get_document_type_id_by_document_id(document.id)

            # If document type BTI use my parser
            if document_type_id == 1:
                fin_dict = {'file_name': document.file.original_name,
                            'doc_type': document_type_id,
                            # Свид__АГР
                            'object_code': None,
                            'reg_number': None,
                            'district': None,
                            # Разр__на_ввод
                            'to_whom': None,
                            'expluatation': None,
                            # БТИ
                            'quart': None,
                            'square': None,
                            'owner': None,
                            # ЗУ
                            'scale': None,
                            'cadastr': None,
                            'doc_number': None,
                            'area': None,
                            'term': None,
                            'account': None,
                            # Разр__на_стр
                            'deal_number': None,
                            'doc_number': None,
                            'client': None,
                            'issuing_authority': None,
                            'date': None,
                            }

                add_dict = {}
                dictionary = get_document_dictionary_by_document_id(document.id)
                add_dict = parsing_of_bti(dictionary, document.id)
                fin_dict.update(add_dict)

                print('-------------TEXT-----------')
                print(dictionary)
                print('=============DICT===========')
                print(fin_dict)
            else:
                answer = create_nlp_tesseract_table(document.id)
                print(answer)

            document.status_id = 8
            document.save()


