# Generated by Django 5.0.6 on 2024-06-05 05:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0010_business_creater'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='service',
            constraint=models.UniqueConstraint(fields=('business', 'service_name'), name='unique_service_per_business'),
        ),
    ]
