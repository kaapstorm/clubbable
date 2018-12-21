import hashlib
import hmac
import json
import logging
from django.conf import settings
from django.contrib import messages
from django.http import (
    HttpResponseRedirect,
    HttpResponseForbidden,
    HttpResponseBadRequest,
    HttpResponse,
)
from django.urls import reverse
import dropbox.oauth
from dropboxer.decorators import dropbox_required
from dropboxer.models import DropboxUser
from dropboxer.tasks import process_changes
from dropboxer.utils import get_auth_flow


logger = logging.getLogger(__name__)


def connect(request):
    flow = get_auth_flow(request)
    auth_url = flow.start()
    return HttpResponseRedirect(auth_url)


def auth(request):
    try:
        flow = get_auth_flow(request)
        access_token, user_id, url_state = flow.finish(request.GET)
    except dropbox.oauth.BadRequestException:
        return HttpResponseBadRequest()
    except dropbox.oauth.BadStateException:
        # Start the auth flow again.
        return connect(request)
    except dropbox.oauth.CsrfException:
        return HttpResponseForbidden()
    except dropbox.oauth.NotApprovedException:
        messages.warning(request, 'Dropbox authentication was not approved.')
        return HttpResponseRedirect(reverse('dashboard'))
    except dropbox.oauth.ProviderException as err:
        logger.exception('Error authenticating Dropbox', err)
        return HttpResponseForbidden()
    DropboxUser.objects.update_or_create(
        user=request.user,
        defaults={
            'account': user_id,
            'access_token': access_token
        }
    )
    messages.success(request, 'Dropbox authentication successful.')
    return HttpResponseRedirect(reverse('dashboard'))


def dropbox_logout(request):
    dropbox_user = DropboxUser.objects.get(user=request.user)
    dropbox_user.access_token = ''
    dropbox_user.save()
    messages.info(request, 'You have disconnected your Dropbox account.')
    return HttpResponseRedirect(reverse('dashboard'))


@dropbox_required
def check_dropbox(request):
    """
    Schedule Dropbox to be checked, and return to dashboard.
    """
    dropbox_user = DropboxUser.objects.get(user=request.user)
    process_changes.delay(dropbox_user)
    messages.info(request, 'Checking Dropbox for changes.')
    return HttpResponseRedirect(reverse('dashboard'))


def webhook(request):
    """
    Dropbox notifies this view when files have changed
    """
    def get_challenge_response(request_):
        challenge = request_.GET.get('challenge', '')
        return HttpResponse(challenge, headers={
            'Content-Type': 'text/plain',
            'X-Content-Type-Options': 'nosniff',
        })

    def verify_signature(request_):
        signature = request_.headers.get('X-Dropbox-Signature')
        request_hash = hmac.new(
            settings.DROPBOX_APP_SECRET, request_.body, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, request_hash)

    if request.method == 'GET':
        return get_challenge_response(request)

    if request.method == 'POST':
        if not verify_signature(request):
            return HttpResponseForbidden()

        # Sample value of request.body:
        #
        #     {
        #         "list_folder": {
        #             "accounts": [
        #                 "dbid:AAH4f99T0taONIb-OurWxbNQ6ywGRopQngc",
        #                 ...
        #             ]
        #         },
        #         "delta": {
        #             "users": [
        #                 12345678,
        #                 23456789,
        #                 ...
        #             ]
        #         }
        #     }
        notification = json.loads(request.body)
        for account in notification['list_folder']['accounts']:
            dropbox_user = DropboxUser.objects.get_or_none(account=account)
            if dropbox_user:
                process_changes(dropbox_user).delay()
        return HttpResponse('Accepted', content_type='text/plain', status=202)
