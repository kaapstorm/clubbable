"""
Celery tasks.

Start the Celery worker with ::
    $ celery -A clubbable worker -l info

"""
import json
import os
from inspect import cleandoc
import magic
from celery import shared_task
import requests
from markdown import markdown
from club.models import User
from django.conf import settings
from docs.models import Document


API_BASE_URL = 'https://api.mailgun.net/v3/%s' % settings.MAILGUN_DOMAIN


class MailerError(Exception):
    pass


@shared_task
def send_doc(to, subject, message, doc_id):

    def get_recipients_vars(to_):
        if isinstance(to_, User):
            return to_.email, {to_.email: {'full_name': to_.get_full_name()}}
        elif to_ == 'Everyone':
            recipients = []
            variables = {}
            for user in User.objects.all():
                if user.receives_emails():
                    recipients.append(user.email)
                    variables[user.email] = {'full_name': user.get_full_name()}
            return recipients, variables
        else:
            raise MailerError('Unknown recipient "%s"' % to_)

    text = cleandoc(message)
    html = markdown(text)
    recipients, variables = get_recipients_vars(to)
    data = {
        'from': settings.FROM_ADDRESS,
        'to': recipients,
        'recipient-variables': json.dumps(variables),
        'subject': subject,
        'text': text,
        'html': html,
    }
    if settings.REPLY_TO_ADDRESS:
        data['reply-to'] = settings.REPLY_TO_ADDRESS
    if settings.BOUNCE_ADDRESS:
        data['return-path'] = settings.BOUNCE_ADDRESS

    doc = Document.objects.get(pk=doc_id)
    filename = doc.file.name.split(os.sep)[-1]
    mime_type = magic.from_buffer(doc.file.read(1024), mime=True)
    files = {'attachment': (filename, doc.file.open('rb'), mime_type)}

    response = requests.post(
        '%s/messages' % API_BASE_URL,
        auth=('api', settings.MAILGUN_API_KEY),
        data=data,
        files=files,
    )
    return response
