dnf install poppler*

django-admin makemessages -l ru --ignore venv
django-admin compilemessages --locale ru --ignore venv

./manage.py inspectdb --database ocr

SFTP account:
sftp_admin
Admin2022###


dnf install poppler*

django-admin makemessages -l ru --ignore venv
django-admin compilemessages --locale ru --ignore venv

./manage.py inspectdb --database ocr

SFTP account:
sftp_admin
Admin2022### (для теста)

### Для запуска проекта необходимо выполнить следующие действия:
Web интерфейс и API
1. Создать Схему в MySQL, PostgreSQL или MariaDB
2. Выполнить команду для установки все библиотек pip install -r requirements.txt
2. добавить в файл (document_processing/settings_local.py) данные о подключении 
3. Выполнить миграции python manage.py migrate
4. Добавить супер пользователя python manage.py createsuperuser

5. Необходимо запустить следующую службу
```bin
#!/bin/sh
cd /var/www/document_processing // путь до корня проекта
source venv/bin/activate
python manage.py send_pages
```

ML модуль:
Находится в папке ML_module

// CELERY
```
celery -A document_processing worker -B -l INFO
```