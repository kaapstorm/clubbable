import datetime
import os
import posixpath
from django.db import models


def _get_upload_path(instance, filename):
    upload_to = f'doc/{instance.folder}/%Y/%m/'
    dirname = datetime.datetime.now().strftime(upload_to)
    return posixpath.join(dirname, filename)


class Folder(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Document(models.Model):
    folder = models.ForeignKey(Folder, models.PROTECT)
    description = models.CharField(max_length=255, blank=True)
    dropbox_file_id = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to=_get_upload_path)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('description',)

    def __str__(self):
        return self.description or self.filename

    @property
    def filename(self):
        return self.file.name.split(os.sep)[-1]

    @property
    def doc_type(self):
        """
        Returns a doc type that can be used for selecting an icon based
        on file extension.
        """
        doc_types = {
            'pdf': 'pdf',
            'doc': 'word',
            'docx': 'word',
            'xls': 'excel',
            'xlsx': 'excel',
            'ppt': 'powerpoint',
            'pptx': 'powerpoint',
            'zip': 'archive',
        }
        ext = self.file.name.split('.')[-1]
        return doc_types.get(ext, 'pdf')
