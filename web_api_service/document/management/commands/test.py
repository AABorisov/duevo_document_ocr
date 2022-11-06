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
        test = OcrResults.objects.using('ocr').filter(user_text__exact='77777777')
        for doc in test:
            print(doc)