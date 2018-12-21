from contextlib import contextmanager
from tempfile import NamedTemporaryFile
from celery import shared_task
from django.conf import settings
from dropbox import Dropbox
from dropbox.files import DeletedMetadata, FileMetadata, FolderMetadata
from clubbable.utils import quickcache
from docs.models import Folder, Document
from import_mdb.import_mdb import import_mdb


@contextmanager
def lock_dropbox_user(dropbox_user):
    dropbox_user.is_locked = True
    dropbox_user.save()
    try:
        yield
    finally:
        dropbox_user.is_locked = False
        dropbox_user.save()


def is_mdb_file(entry):
    return (
        settings.MDB_FILENAME and
        isinstance(entry, FileMetadata) and
        entry.name == settings.MDB_FILENAME
    )


@contextmanager
def get_tmp_file_name(data):
    tmp_file = NamedTemporaryFile()
    tmp_file.write(data)
    try:
        yield tmp_file.name
    finally:
        tmp_file.close()


@quickcache([])
def get_folder_names():
    return set(f.name for f in Folder.objects.all())


def is_doc_folder(entry):
    return (
        isinstance(entry, FolderMetadata) and
        entry.name in get_folder_names()
    )


@quickcache(['folder_name'])
def get_folder_doc_filenames(folder_name):
    folder = Folder.objects.get(name=folder_name)
    return set(d.filename for d in folder.document_set.all())


def add_doc_to_folder(dbx, doc_entry, folder_name):
    folder = Folder.objects.get(name=folder_name)
    _, response = dbx.files_download(doc_entry.path_lower)
    with get_tmp_file_name(response.content) as doc_filename:
        Document.objects.create(
            folder=folder,
            description=doc_entry.name,
            file=doc_filename,
        )


def process_doc_folder(dbx, folder_entry):
    cursor = None
    has_more = True

    while has_more:
        if cursor is None:
            result = dbx.files_list_folder(path=folder_entry.path_lower)
        else:
            result = dbx.files_list_folder_continue(cursor)

        for entry in result.entries:
            if (
                    isinstance(entry, DeletedMetadata) or
                    isinstance(entry, FolderMetadata)
            ):
                continue

            if entry.name not in get_folder_doc_filenames(folder_entry.name):
                add_doc_to_folder(dbx, entry, folder_entry.name)
                get_folder_doc_filenames.clear(folder_entry.name)

        cursor = result.cursor
        has_more = result.has_more


@shared_task
def process_changes(dropbox_user):
    """
    Call /files/list_folder for the given DropboxUser and process any
    changes.
    """
    if dropbox_user.is_locked:
        return

    with lock_dropbox_user(dropbox_user):
        cursor = None
        dbx = Dropbox(dropbox_user.access_token)
        has_more = True

        while has_more:
            if cursor is None:
                result = dbx.files_list_folder(path='')
            else:
                result = dbx.files_list_folder_continue(cursor)

            for entry in result.entries:
                if isinstance(entry, DeletedMetadata):
                    # Ignore deleted files
                    continue

                if is_mdb_file(entry):
                    _, response = dbx.files_download(entry.path_lower)
                    with get_tmp_file_name(response.content) as mdb_filename:
                        import_mdb(mdb_filename)
                elif is_doc_folder(entry):
                    process_doc_folder(dbx, entry)

            cursor = result.cursor
            has_more = result.has_more
