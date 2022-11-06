#!/bin/sh
sleep 50
cd /var/www/document_processing
source venv/bin/activate
python manage.py synchronize_nlp
