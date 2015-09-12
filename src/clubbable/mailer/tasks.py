# -*- coding: utf-8 -*-
"""
Celery tasks.

Start the Celery worker with ::
    $ celery -A clubbable worker -l info

"""
from __future__ import unicode_literals, absolute_import
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from celery import shared_task
from django.contrib.auth.models import User
import requests
from club.models import Member
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

    def wants_email(user):
        return user.profile.member is None or user.profile.member.send_emails

    # TODO: First check if it exists, and if so delete it.
    response = requests.post(
        'https://api.mailgun.net/v3/%s/lists/' % settings.MAILGUN_DOMAIN,
        data={'address': 'members@' + settings.CLUB_DOMAIN}
    )
    members = [u.email for u in User.objects.all() if wants_email(u)]
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


@shared_task
def send_doc(to, subject, text, doc_id, address=None):
    if to == 'Everyone':
        _create_members_list()
        address = 'members@' + settings.CLUB_DOMAIN
    else:
        assert address, 'Unable to send email without an address'

    doc = Document.objects.get(pk=doc_id)
    data = {
        'from': settings.FROM_ADDRESS,
        'to': address,
        'subject': subject,
        'text': text,
    }
    if settings.REPLY_TO_ADDRESS:
        data['reply-to'] = settings.REPLY_TO_ADDRESS
    if settings.BOUNCE_ADDRESS:
        data['return-path'] = settings.BOUNCE_ADDRESS
    response = requests.post(
        'https://api.mailgun.net/v3/%s/messages' % settings.MAILGUN_DOMAIN,
        auth=('api', settings.MAILGUN_API_KEY),
        files=[('attachment', doc.data)],
        data=data
    )
    # Sample response:
    #     {
    #       "message": "Queued. Thank you.",
    #       "id": "<20111114174239.25659.5817@samples.mailgun.org>"
    #     }

    if to == 'Everyone':
        _delete_members_list()

    return 200 <= response.status_code < 300
