#!/bin/sh
sleep 15
cd /var/www/document_processing
source venv/bin/activate
python manage.py create_nlp_tesseract
