# Generated by Django 3.1.7 on 2021-03-29 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webauth', '0002_auto_20210329_1453'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webauthncredential',
            name='credential_id',
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name='webauthncredential',
            name='public_key',
            field=models.TextField(),
        ),
    ]
