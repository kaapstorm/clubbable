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
from django.contrib.auth.models import Group
from markdown import markdown
from club.models import User
from django.conf import settings
from docs.models import Document


API_BASE_URL = f'https://api.mailgun.net/v3/{settings.MAILGUN_DOMAIN}'


class MailerError(Exception):
    pass


@shared_task
def send_doc(to, subject, message, doc_id):
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
        f'{API_BASE_URL}/messages',
        auth=('api', settings.MAILGUN_API_KEY),
        data=data,
        files=files,
    )
    if not 200 <= response.status_code < 300:
        raise MailerError(f'Sending document failed: {response.content}')


def get_recipients_vars(to_):
    if to_.isdigit():
        group = Group.objects.get(pk=to_)
        users = group.user_set.all()
    elif to_ == 'everyone':
        users = User.objects.all()
    elif '@' in to_:
        # "myself" was passed as request.user.email
        users = [User.objects.get(email=to_)]
    else:
        raise MailerError(f'Unrecognised recipient "{to_}"')
    recipients = []
    variables = {}
    for user in users:
        if user.receives_emails():
            recipients.append(user.email)
            variables[user.email] = {'full_name': user.get_full_name()}
    return recipients, variables
