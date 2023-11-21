from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Book

class Command(BaseCommand):
    help = 'Initialize groups'

    def handle(self, *args, **options):
        # Создаем группы
        reader_group, created = Group.objects.get_or_create(name='Читач')
        translator_group, created = Group.objects.get_or_create(name='Перекладач')
        freelancer_group, created = Group.objects.get_or_create(name='Фрілансер')

        # Добавляем разрешение на чтение книг для каждой группы
        content_type = ContentType.objects.get_for_model(Book)
        read_permission, created = Permission.objects.get_or_create(
            codename='view_book',
            content_type=content_type,
            defaults={'name': 'Can view book'},
        )

        reader_group.permissions.add(read_permission)
        translator_group.permissions.add(read_permission)
        freelancer_group.permissions.add(read_permission)

        # Добавляем разрешение на загрузку книг для переводчиков и фрилансеров
        upload_permission, created = Permission.objects.get_or_create(
            codename='add_book',
            content_type=content_type,
            defaults={'name': 'Can add book'},
        )
        translator_group.permissions.add(upload_permission)
        freelancer_group.permissions.add(upload_permission)

        # Добавляем разрешение на дополнительные действия для фрилансеров
        # Возможно, вам придется создать это разрешение
        # Допустим, у нас есть дополнительное разрешение 'extra_action'
        extra_permission, created = Permission.objects.get_or_create(
            codename='extra_action',
            content_type=content_type,
            defaults={'name': 'Can perform extra actions'},
        )
        freelancer_group.permissions.add(extra_permission)