from django.core.management.base import BaseCommand, CommandError
from pdf2image import convert_from_path
from document.models import *
from document_processing import settings
import os
import time
import datetime
import magic
import requests
import json
from document.utils import *
from document.tesseract_services import *
from document.ocr_module.main import get_result
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
        # Create cron lock
        create_cron_lock_file(path_to_cron_lock_file)

        # RUN PROGRAM
        print("Program is running")
        
        files = File.objects.filter(is_active=True, is_processed=False)
        if files:
            print('===========================================')
            print(datetime.datetime.now())
            print('Start uploading pages ...')

        for file in files:

            file_result = get_result(file.file_path.path, file.id)

            print(file_result)

            file.is_processed = True
            file.save()

        # END SCRIPT Remove lock file
        remove_cron_lock_file(path_to_cron_lock_file)
