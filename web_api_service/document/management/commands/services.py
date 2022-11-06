import os
from pathlib import Path


def check_if_exists_cron_lock_file(path_to_cron_lock_file: str) -> None:
    """Проверяем есть ли файл крона в папке , если да то выходим из скрипта"""
    if os.path.isfile(path_to_cron_lock_file):
        exit('Cron instance is already running')


def create_cron_lock_file(path_to_cron_lock_file: str) -> None:
    """Создаем cron lock файл"""
    Path(path_to_cron_lock_file).touch()


def remove_cron_lock_file(path_to_cron_lock_file: str) -> None:
    """Удаляет cron lock файл"""
    os.unlink(path_to_cron_lock_file)
