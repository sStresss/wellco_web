# Generated by Django 3.2.4 on 2021-10-21 15:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='well',
            name='comment',
        ),
    ]
