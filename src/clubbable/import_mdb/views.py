from contextlib import closing
from tempfile import NamedTemporaryFile

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from import_mdb.forms import UploadMdbForm
from import_mdb.tasks import import_mdb, unlink
from club.views import get_context_data


@user_passes_test(lambda u: u.is_staff)
def upload_mdb(request):
    if request.method == 'POST':
        form = UploadMdbForm(request.POST, request.FILES)
        if form.is_valid():
            tmp_filename = save_tmp_file(request.FILES['access_db'])
            (import_mdb.si(tmp_filename) | unlink.si(tmp_filename))()

            messages.info(request, 'Access database queued for importing.')
            return HttpResponseRedirect(reverse('dashboard'))
    else:
        form = UploadMdbForm()
    context_data = get_context_data(request)
    context_data['form'] = form
    return render(request, 'import_mdb/upload_mdb.html', context_data)


def save_tmp_file(uploaded_file):
    """
    Saves the contents of an uploaded file into a temporary file and
    returns its filename.

    The temporary file needs to be deleted when it is no longer needed.
    """
    with closing(NamedTemporaryFile(delete=False)) as tmp_file:
        for chunk in uploaded_file.chunks():
            tmp_file.write(chunk)
    return tmp_file.name
