# Generated by Django 4.2.11 on 2024-09-11 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jonomotApp', '0017_reaction_ip_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='alldata',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
    ]
