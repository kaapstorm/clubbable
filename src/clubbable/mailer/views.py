from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from club.views import get_context_data
from mailer.tasks import send_message, get_email_groups


@user_passes_test(lambda u: u.is_staff)
def send(request):
    if request.method == 'POST':
        to = request.POST['to']
        send_message.delay(
            to=request.user.email if to == 'myself' else to,
            subject=request.POST['subject'],
            message=request.POST['text'],
        )
        messages.info(request, 'Your message is queued for sending.')
        return HttpResponseRedirect(reverse('dashboard'))
    context_data = get_context_data(request)
    context_data['groups'] = get_email_groups()
    return render(request, 'mailer/send_message.html', context_data)
