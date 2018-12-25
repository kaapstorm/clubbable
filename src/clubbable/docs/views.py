from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import ListView
import magic
from docs.models import Document, Folder
from mailer.tasks import send_doc
from website.views import ClubbableContextMixin


class DocList(ListView, ClubbableContextMixin):
    context_object_name = 'docs'

    def get_queryset(self):
        folder = get_object_or_404(Folder, pk=self.args[0])
        return Document.objects.filter(folder=folder)


def send(request, folder_id, pk):
    if request.method == 'POST':
        to = request.POST['to']
        send_doc.delay(
            to=to,
            subject=request.POST['subject'],
            text=request.POST['text'],
            doc_id=pk,
            address=request.user.email if to == 'Myself' else None,
        )
        messages.info(request, 'Your message is queued for sending.')
        return HttpResponseRedirect(reverse('doc_list'))
    doc = get_object_or_404(Document, pk=pk)
    return render(request, 'docs/send_doc.html', {'doc': doc})


def download(request, folder_id, pk, filename):
    """
    Return doc as an HTTP response attachment

    :param request: HTTP Request
    :param folder_id: Keeps the URLs logical, but not used
    :param pk: The primary key of the document
    :param filename: Makes the URL to look nice, but not used
    """
    doc = get_object_or_404(Document, pk=pk)
    mime = magic.Magic(mime=True)
    file_path = settings.MEDIA_ROOT + doc.file.name
    content_type = mime.from_file(file_path)
    response = HttpResponse(doc.file.read(), content_type=content_type)
    response['Content-Length'] = doc.file.size
    response['Content-Disposition'] = ('attachment; '
                                       'filename="%s"' % doc.filename)
    return response
