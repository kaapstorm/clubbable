# Generated by Django 2.1.4 on 2018-12-20 14:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('club', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Gallery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=255)),
                ('original', models.ImageField(upload_to='img/%Y/%m/')),
                ('creator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_image', to='club.Member')),
                ('gallery', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='galleries.Gallery')),
                ('guests', models.ManyToManyField(to='club.Guest')),
                ('meeting', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='club.Meeting')),
                ('members', models.ManyToManyField(to='club.Member')),
            ],
        ),
        migrations.AddField(
            model_name='gallery',
            name='poster_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='poster_gallery', to='galleries.Image'),
        ),
    ]
