# Generated by Django 5.0.1 on 2024-01-30 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jonomotApp', '0004_optionchoice'),
    ]

    operations = [
        migrations.AddField(
            model_name='alldata',
            name='post_type',
            field=models.TextField(blank=True, null=True),
        ),
    ]