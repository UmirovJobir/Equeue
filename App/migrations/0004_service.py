# Generated by Django 5.0.6 on 2024-06-03 13:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0003_businessimage'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('duration', models.DurationField()),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='App.business')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subservices', to='App.service')),
            ],
        ),
    ]
