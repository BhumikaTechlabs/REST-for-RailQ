# Generated by Django 2.0.3 on 2018-11-13 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat_api', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='isReceived',
            field=models.IntegerField(default=1),
        ),
    ]