# Generated by Django 5.0.1 on 2024-01-29 07:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jonomotApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alldata',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]