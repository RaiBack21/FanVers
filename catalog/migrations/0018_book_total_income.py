# Generated by Django 4.2.5 on 2023-11-12 12:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0017_income'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='total_income',
            field=models.DecimalField(decimal_places=2, default=0.00, max_digits=10),
            preserve_default=False,
        ),
    ]
