# Generated by Django 4.2.5 on 2023-11-27 10:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0025_remove_chapter_chapter_views_viewedchapters_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='viewedchapters',
            old_name='Chapter',
            new_name='chapter',
        ),
    ]
