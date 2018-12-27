from contextlib import closing
from tempfile import NamedTemporaryFile

from celery import shared_task

from import_mdb.import_mdb import import_mdb


@shared_task
def import_uploaded_mdb(uploaded_file):
    with closing(NamedTemporaryFile()) as tmp_file:
        for chunk in uploaded_file.chunks():
            tmp_file.write(chunk)
        import_mdb(tmp_file.name)
