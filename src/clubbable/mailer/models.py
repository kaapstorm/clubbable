from django.db import models
from docs.models import Document


class MessageTemplate(models.Model):
    """
    A MessageTemplate is used to send e-mails to members.

    It may have one or more Notices attached. Subject and body are templates
    that are populated at send time from a context with the member's name, and
    the notice's description.
    """
    subject = models.CharField(max_length=255)
    text = models.TextField()
    html = models.TextField(blank=True)
    docs = models.ManyToManyField(Document)

    def __str__(self):
        return self.subject

    def get_subject_or_docs(self):
        if self.docs:
            return ', '.join([str(n) for n in self.docs])
        return self.subject
