import hashlib
import hmac
import json
import logging
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import (
    HttpResponseRedirect,
    HttpResponseForbidden,
    HttpResponseBadRequest,
    HttpResponse,
)
from django.http.request import split_domain_port
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from dropbox import DropboxOAuth2Flow
from dropbox.oauth import (
    BadRequestException,
    BadStateException,
    CsrfException,
    NotApprovedException,
    ProviderException,
)

from dropboxer.models import DropboxUser
from dropboxer.tasks import process_changes


logger = logging.getLogger(__name__)


def _get_dropbox_auth_flow(request):
    redirect_uri = request.build_absolute_uri(reverse('dropbox_auth_finish'))
    domain, port = split_domain_port(request.get_host())
    local_domains = ('localhost', '127.0.0.1', '[::1]')
    if (request.scheme == 'http' and domain not in local_domains):
        # Force redirect_uri to use https, even if scheme is http
        redirect_uri = 'https://' + redirect_uri[7:]
    return DropboxOAuth2Flow(
        settings.DROPBOX_APP_KEY,
        settings.DROPBOX_APP_SECRET,
        redirect_uri,
        request.session,
        'dropbox-auth-csrf-token'
    )


def dropbox_required(view_func):

    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        dropbox_user = DropboxUser.objects.get_or_none(user=request.user)
        if dropbox_user and dropbox_user.access_token:
            return view_func(request, *args, **kwargs)
        if not dropbox_user or not dropbox_user.access_token:
            authorize_url = _get_dropbox_auth_flow(request).start()
            return HttpResponseRedirect(authorize_url)

    return wrapped


@user_passes_test(lambda u: u.is_staff)
def dropbox_auth_start(request):
    authorize_url = _get_dropbox_auth_flow(request).start()
    return HttpResponseRedirect(authorize_url)


@user_passes_test(lambda u: u.is_staff)
def dropbox_auth_finish(request):
    try:
        oauth_result = (
            _get_dropbox_auth_flow(request).finish(request.GET)
        )
    except BadRequestException:
        return HttpResponseBadRequest()
    except BadStateException:
        # Start the auth flow again.
        return HttpResponseRedirect(reverse('dropbox_auth_start'))
    except CsrfException:
        return HttpResponseForbidden()
    except NotApprovedException:
        messages.warning(request, 'Dropbox authentication was not approved.')
        return HttpResponseRedirect(reverse('dashboard'))
    except ProviderException as err:
        logger.exception('Error authenticating Dropbox', err)
        return HttpResponseForbidden()
    DropboxUser.objects.update_or_create(
        user=request.user,
        defaults={
            'account': oauth_result.account_id,
            'access_token': oauth_result.access_token
        }
    )
    messages.success(request, 'Dropbox authentication successful.')
    return HttpResponseRedirect(reverse('dashboard'))


@user_passes_test(lambda u: u.is_staff)
def dropbox_logout(request):
    dropbox_user = DropboxUser.objects.get(user=request.user)
    dropbox_user.access_token = ''
    dropbox_user.save()
    messages.info(request, 'You have disconnected your Dropbox account.')
    return HttpResponseRedirect(reverse('dashboard'))


@user_passes_test(lambda u: u.is_staff)
@dropbox_required
def check_dropbox(request):
    """
    Schedule Dropbox to be checked, and return to dashboard.
    """
    process_changes.delay(request.user.get_username())
    messages.info(request, 'Checking Dropbox for changes.')
    return HttpResponseRedirect(reverse('dashboard'))


@csrf_exempt
def webhook(request):
    """
    Dropbox notifies this view when files have changed
    """
    def get_challenge_response(request_):
        challenge = request_.GET.get('challenge', '')
        response = HttpResponse(challenge, content_type='text/plain')
        response['X-Content-Type-Options'] = 'nosniff'
        return response

    def verify_signature(request_):
        if 'X-Dropbox-Signature' not in request_.headers:
            return False
        signature = request_.headers['X-Dropbox-Signature']
        secret = settings.DROPBOX_APP_SECRET.encode('ascii')
        request_hash = hmac.new(secret, request_.body, hashlib.sha256)
        hash_digest = request_hash.hexdigest()
        return hmac.compare_digest(signature, hash_digest)

    if request.method == 'GET':
        logger.info('Dropbox webhook: Challenge request')
        return get_challenge_response(request)

    if request.method == 'POST':
        logger.info('Dropbox webhook: Notification')
        if not verify_signature(request):
            logger.info('Dropbox webhook: Verification failed')
            return HttpResponseForbidden()

        logger.debug(f'Dropbox webhook: Request body: \n{request.body}')
        notification = json.loads(request.body)
        for account in notification['list_folder']['accounts']:
            dropbox_user = DropboxUser.objects.get_or_none(account=account)
            if dropbox_user:
                process_changes.delay(dropbox_user.user.get_username())
        return HttpResponse('Accepted', content_type='text/plain', status=202)
