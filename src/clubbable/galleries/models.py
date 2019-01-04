import datetime
import os
import posixpath
from itertools import chain
from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit, Thumbnail
from club.models import Meeting, Member, Guest


def _get_upload_path(instance, filename):
    upload_to = 'img/{gallery}/%Y/%m/'.format(gallery=instance.gallery)
    dirname = datetime.datetime.now().strftime(upload_to)
    return posixpath.join(dirname, filename)


class Gallery(models.Model):
    name = models.CharField(max_length=255)
    # poster_image is the image for this gallery in the list of galleries
    poster_image = models.ForeignKey(
        'Image', models.SET_NULL,
        related_name='poster_gallery', null=True, blank=True
    )

    class Meta:
        verbose_name_plural = 'galleries'

    def __str__(self):
        return '%s' % self.name


class Image(models.Model):
    gallery = models.ForeignKey(Gallery, models.PROTECT)
    description = models.CharField(max_length=255, blank=True)
    dropbox_file_id = models.CharField(max_length=255, blank=True)
    meeting = models.ForeignKey(
        Meeting, models.SET_NULL,
        null=True, blank=True,
    )
    members = models.ManyToManyField(Member, blank=True)
    guests = models.ManyToManyField(Guest, blank=True)
    creator = models.ForeignKey(
        Member, models.SET_NULL,
        related_name='creator_image', null=True, blank=True,
    )

    original = models.ImageField(upload_to=_get_upload_path)
    display = ImageSpecField(source='original',
                             processors=[ResizeToFit(1024, 768)],
                             format='JPEG',
                             options={'quality': 90})
    thumbnail = ImageSpecField(source='original',
                               processors=[Thumbnail(200, 100)],
                               format='JPEG',
                               options={'quality': 60})

    class Meta:
        ordering = ('description',)

    def __str__(self):
        return self.name

    @property
    def name(self):
        if self.description:
            return '%s' % self.description
        people = ', '.join(('%s' % p
                            for p in chain(self.members, self.guests)))
        if self.meeting:
            return '%s: %s' % (self.meeting, people)
        return people

    @property
    def filename(self):
        return self.original.name.split(os.sep)[-1]
