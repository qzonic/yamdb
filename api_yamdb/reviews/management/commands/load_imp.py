import csv
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from reviews.models import Title, Genre

name_file = 'genre_title.csv'


class Command(BaseCommand):
    """ Возможно загрузить в базу данных тестовые данные командой: """
    """ python manage.py load_imp (по имени файла)"""
    """ для обычного импорта испульзуется метод встроенный в панель админа """
    """ данный скрипт использутся для импорта ManyToManyField """
    """ импорт происходит из папки static/data """
    """ важно знать порядок полей в вашей таблице в БД и в том же порядке """
    """ расположить модели в коде и таблице"""

    def handle(self, *args, **options):

        files = os.path.join(settings.BASE_DIR, 'data', name_file)

        with open(files) as f:
            reader = csv.reader(f)
            first_line = 1
            for row in reader:
                if first_line:
                    first_line = 0
                    continue
                _, created = Title.objects.get(id=row[1]).genre.add(
                    Genre.objects.get(id=row[2])
                )
            f.close()
