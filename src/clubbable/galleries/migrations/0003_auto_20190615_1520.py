# Generated by Django 2.2 on 2019-06-15 13:20

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('galleries', '0002_image_dropbox_file_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='image',
            options={'ordering': ('description',)},
        ),
        migrations.AddField(
            model_name='image',
            name='added_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
