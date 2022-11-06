#!/bin/sh
sleep 25
cd /var/www/document_processing
source venv/bin/activate
python manage.py send_to_rabbitmq 
