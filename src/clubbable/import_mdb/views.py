from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from import_mdb.forms import UploadMdbForm
from import_mdb.tasks import import_uploaded_mdb
from website.views import get_context_data


def upload_mdb(request):
    if request.method == 'POST':
        form = UploadMdbForm(request.POST, request.FILES)
        if form.is_valid():
            import_uploaded_mdb.delay(request.FILES['access_db'])
            messages.info(request, 'Access database queued for importing.')
            return HttpResponseRedirect(reverse('dashboard'))
    else:
        form = UploadMdbForm()
    context_data = get_context_data(request)
    context_data['form'] = form
    return render(request, 'import_mdb/upload_mdb.html', context_data)
