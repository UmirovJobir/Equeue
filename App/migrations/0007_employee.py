# Generated by Django 5.0.6 on 2024-06-04 07:23

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0006_employeerole'),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('patronymic', models.CharField(max_length=100)),
                ('duration', models.DurationField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='employees/images')),
                ('phone', models.CharField(max_length=17, unique=True, validators=[django.core.validators.RegexValidator(regex='^998[0-9]{2}[0-9]{7}$')])),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='App.business')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='role', to='App.employeerole')),
                ('service', models.ManyToManyField(related_name='employees', to='App.service')),
            ],
        ),
    ]