from collections import namedtuple
from itertools import chain

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect, FileResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import ListView

from club.views import get_context_data, ClubbableContextMixin
from docs.models import Document, Folder
from mailer.tasks import send_doc


class DocList(LoginRequiredMixin, ListView, ClubbableContextMixin):
    context_object_name = 'docs'
    paginate_by = 100
    allow_empty = False

    def get_folder(self):
        return get_object_or_404(Folder, pk=self.kwargs['folder_id'])

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['folder'] = self.get_folder()
        return context_data

    def get_queryset(self):
        return self.get_folder().document_set.all()


@user_passes_test(lambda u: u.is_staff)
def send(request, folder_id, pk):
    doc = get_object_or_404(Document, folder__id=folder_id, pk=pk)
    if request.method == 'POST':
        to = request.POST['to']
        send_doc.delay(
            to=request.user.email if to == 'myself' else to,
            subject=request.POST['subject'],
            message=request.POST['text'],
            doc_id=doc.id,
        )
        messages.info(request, 'Your message is queued for sending.')
        return HttpResponseRedirect(
            reverse('doc_list', kwargs={'folder_id': folder_id})
        )
    context_data = get_context_data(request)
    context_data['doc'] = doc
    context_data['groups'] = get_email_groups()
    return render(request, 'docs/send_doc.html', context_data)


def get_email_groups():
    SpecialGroup = namedtuple('SpecialGroup', 'id name')
    return chain(
        [SpecialGroup('myself', 'Myself')],
        Group.objects.all(),
        [SpecialGroup('everyone', 'Everyone')],
    )


@login_required
def download(request, folder_id, pk, filename):
    """
    Return doc as an attachment.

    (`filename` is just to make the URL look nice.)
    """
    doc = get_object_or_404(Document, folder__id=folder_id, pk=pk)
    return FileResponse(doc.file, as_attachment=True)
