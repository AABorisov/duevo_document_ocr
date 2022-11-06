import os
from document_processing import settings
from django.core.management.base import BaseCommand, CommandError
from document.models import *
from document.utils import *


class Command(BaseCommand):
    args = ''
    help = 'Export data to remote server'

    def handle(self, *args, **options):
        """Конвертируем nlp таблицу в nlp_result"""
        print('Start nlp table synchronizing...')
        nlp_result_rows = generate_fields_for_ocr_result()
        # Synchronize with nlp_result table
        synchronize_nlp_to_nlp_result(nlp_result_rows)
        print('Finish synchronizing...')
