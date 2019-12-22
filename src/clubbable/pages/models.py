from django.db.models import (
    CharField,
    IntegerField,
    Model,
    TextField,
)
from markdown import markdown


class Page(Model):
    index = IntegerField(unique=True)
    title = CharField(max_length=255)
    banner_img_url = CharField(max_length=255)
    content_markdown = TextField()
    content_html = TextField()

    class Meta:
        ordering = ('index',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.content_html = markdown(self.content_markdown)
        return super().save(*args, **kwargs)
