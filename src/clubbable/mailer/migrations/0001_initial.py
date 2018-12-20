# Generated by Django 2.1.4 on 2018-12-20 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('docs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255)),
                ('text', models.TextField()),
                ('html', models.TextField(blank=True)),
                ('docs', models.ManyToManyField(to='docs.Document')),
            ],
        ),
    ]