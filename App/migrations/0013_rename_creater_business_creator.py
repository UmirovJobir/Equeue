# Generated by Django 5.0.6 on 2024-06-06 06:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0012_employeerole_business_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='business',
            old_name='creater',
            new_name='creator',
        ),
    ]
