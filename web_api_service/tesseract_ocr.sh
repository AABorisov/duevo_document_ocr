#!/bin/sh
cd /var/www/document_processing
source venv/bin/activate
python manage.py tesseract_ocr
