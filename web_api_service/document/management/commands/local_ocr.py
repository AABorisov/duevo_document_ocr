from django.core.management.base import BaseCommand, CommandError
import time
import os

from document.management.commands.services import remove_cron_lock_file, \
    create_cron_lock_file, check_if_exists_cron_lock_file
from document_processing import settings


class Command(BaseCommand):
    args = ''
    help = 'Export data to remote server'

    def handle(self, *args, **options):
        # Lock filename
        lock_filename = 'local_ocr.lock'
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
        time.sleep(30)
        print("Printed after 30 seconds.")

        # Remove lock file
        remove_cron_lock_file(path_to_cron_lock_file)
