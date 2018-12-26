"""
Celery tasks.

Start the Celery worker with ::
    $ celery -A clubbable worker -l info

"""
import os
from contextlib import contextmanager
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from inspect import cleandoc
import magic
from celery import shared_task
import requests
from markdown import markdown
from club.models import Member, User
from django.conf import settings
from django.template import loader
from django.template.context import Context
from docs.models import Document
from mailer.models import MessageTemplate


def _render_string(string, context):
    return loader.get_template_from_string(string).render(context)


def _attach_doc(message, doc):
    attachment = MIMEApplication(doc.data)
    attachment.add_header(
        'Content-Disposition', 'attachment', filename=doc.filename)
    message.attach(attachment)


def _attach_text_template(message, template, context, subtype='plain'):
    text = _render_string(template, context)
    part = MIMEText(text, subtype)
    message.attach(part)


def _build_message(template, member):
    context = Context({
        'full_name': member.get_full_name(),
        'formal_name': member.get_formal_name(),
        'docs': ['%s' % a for a in template.docs]
    })
    if template.html:
        message = MIMEMultipart('alternative')
        _attach_text_template(message, template.text, context)
        _attach_text_template(message, template.html, context, 'html')
        for doc in template.docs:
            _attach_doc(message, doc)
    elif template.docs:
        message = MIMEMultipart()
        _attach_text_template(message, template.text, context)
        for doc in template.docs:
            _attach_doc(message, doc)
    else:
        text = _render_string(template.text, context)
        message = MIMEText(text)
    message['To'] = member.email
    message['From'] = settings.FROM_ADDRESS
    message['Subject'] = _render_string(template.subject, context)
    if settings.REPLY_TO_ADDRESS:
        message['Reply-To'] = settings.REPLY_TO_ADDRESS
    if settings.BOUNCE_ADDRESS:
        message['Return-Path'] = settings.BOUNCE_ADDRESS
    return message


@shared_task
def send_message(template_id, user_id):
    template = MessageTemplate.objects.get(template_id)
    user = Member.objects.get(user_id)
    message = _build_message(template, user)
    smtp = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
    smtp.sendmail(settings.FROM_ADDRESS, [user.email], message.as_string())
    smtp.quit()


def _create_members_list():

    # TODO: First check if it exists, and if so delete it.
    response = requests.post(
        'https://api.mailgun.net/v3/%s/lists/' % settings.MAILGUN_DOMAIN,
        data={'address': 'members@' + settings.CLUB_DOMAIN}
    )
    members = [u.email for u in User.objects.all() if u.receives_emails()]
    response = requests.post(
        'https://api.mailgun.net/v3/%s/lists/members@%s/members.json',
        data={'members': members}
    )
    return 200 <= response.status_code < 300


def _delete_members_list():
    response = requests.delete(
        'https://api.mailgun.net/v3/%s/lists/members@%s' % (
            settings.MAILGUN_DOMAIN,
            settings.CLUB_DOMAIN,
        )
    )


@contextmanager
def get_members_list():
    _create_members_list()
    try:
        yield 'members@' + settings.CLUB_DOMAIN
    finally:
        _delete_members_list()


@shared_task
def send_doc(to, subject, message, doc_id):

    def post_mailgun(data_, files_):
        # Sample response:
        #     {
        #       "message": "Queued. Thank you.",
        #       "id": "<20111114174239.25659.5817@samples.mailgun.org>"
        #     }
        return requests.post(
            'https://api.mailgun.net/v3/%s/messages' % settings.MAILGUN_DOMAIN,
            auth=('api', settings.MAILGUN_API_KEY),
            data=data_,
            files=files_,
        )

    text = cleandoc(message)
    html = markdown(text)
    data = {
        'from': settings.FROM_ADDRESS,
        'to': to,
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

    if to == 'Everyone':
        with get_members_list() as address:
            data['to'] = address
            response = post_mailgun(data, files)
    else:
        response = post_mailgun(data, files)
    return response
