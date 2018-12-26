"""
Celery tasks.

Start the Celery worker with ::
    $ celery -A clubbable worker -l info

"""
import json
import os
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


API_BASE_URL = 'https://api.mailgun.net/v3/%s' % settings.MAILGUN_DOMAIN


class MailerError(Exception):
    pass


class MailgunError(MailerError):
    pass


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
