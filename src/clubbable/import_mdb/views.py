from contextlib import closing
from tempfile import NamedTemporaryFile

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.files.storage import DefaultStorage
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from import_mdb.forms import UploadMdbForm
from import_mdb.tasks import import_mdb, delete_storage_file
from club.views import get_context_data


@user_passes_test(lambda u: u.is_staff)
def upload_mdb(request):
    if request.method == 'POST':
        form = UploadMdbForm(request.POST, request.FILES)
        if form.is_valid():
            filename = save_file_to_storage(request.FILES['access_db'])
            (import_mdb.si(filename) | delete_storage_file.si(filename))()

            messages.info(request, 'Access database queued for importing.')
            return HttpResponseRedirect(reverse('dashboard'))
    else:
        form = UploadMdbForm()
    context_data = get_context_data(request)
    context_data['form'] = form
    return render(request, 'import_mdb/upload_mdb.html', context_data)


def save_file_to_storage(uploaded_file):
    """
    Saves an uploaded file to default storage and returns its filename.
    """
    storage = DefaultStorage()
    filename = storage.get_valid_name(uploaded_file.name)
    with storage.open(filename, 'wb') as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)
    return filename
