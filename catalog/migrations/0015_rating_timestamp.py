# Generated by Django 4.2.5 on 2023-11-06 20:00

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0014_book_viewed_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='rating',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]