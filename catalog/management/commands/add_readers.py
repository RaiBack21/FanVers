from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Add all users to the Читач group'

    def handle(self, *args, **options):
        # Получаем группу 'Читач'
        reader_group = Group.objects.get(name='Читач')

        # Получаем всех пользователей
        users = User.objects.all()

        # Добавляем каждого пользователя в группу 'Читач'
        for user in users:
            user.groups.add(reader_group)
