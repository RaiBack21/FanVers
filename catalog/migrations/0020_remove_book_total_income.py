# Generated by Django 4.2.5 on 2023-11-12 14:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0019_alter_book_total_income'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='total_income',
        ),
    ]