# Generated by Django 5.0.6 on 2024-06-07 11:27

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0013_rename_creater_business_creator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='phone',
            field=models.CharField(blank=True, max_length=17, null=True, unique=True, validators=[django.core.validators.RegexValidator(regex='^998[0-9]{2}[0-9]{7}$')]),
        ),
    ]
