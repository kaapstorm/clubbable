# Generated by Django 2.1.4 on 2018-12-26 18:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0002_auto_20181226_1625'),
    ]

    operations = [
        migrations.RenameField(
            model_name='member',
            old_name='send_emails',
            new_name='receives_emails',
        ),
    ]