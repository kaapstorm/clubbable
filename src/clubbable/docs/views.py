from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, FileResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import ListView
import magic
from docs.models import Document, Folder
from mailer.tasks import send_doc
from club.views import get_context_data, ClubbableContextMixin


class DocList(LoginRequiredMixin, ListView, ClubbableContextMixin):
    context_object_name = 'docs'

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
    if request.method == 'POST':
        to = request.POST['to']
        send_doc.delay(
            to=request.user.email if to == 'Myself' else to,
            subject=request.POST['subject'],
            message=request.POST['text'],
            doc_id=pk,
        )
        messages.info(request, 'Your message is queued for sending.')
        return HttpResponseRedirect(
            reverse('doc_list', kwargs={'folder_id': folder_id})
        )
    context_data = get_context_data(request)
    context_data['doc'] = get_object_or_404(Document, pk=pk)
    return render(request, 'docs/send_doc.html', context_data)


@login_required
def download(request, folder_id, pk, filename):
    """
    Return doc as an HTTP response attachment

    :param request: HTTP Request
    :param folder_id: Keeps the URLs logical, but not used
    :param pk: The primary key of the document
    :param filename: Makes the URL to look nice, but not used
    """
    doc = get_object_or_404(Document, pk=pk)
    return FileResponse(doc.file, as_attachment=True)
