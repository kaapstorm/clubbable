from contextlib import contextmanager
from tempfile import NamedTemporaryFile
from celery import shared_task
from django.conf import settings
from dropbox import Dropbox
from dropbox.files import DeletedMetadata, FileMetadata
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

            cursor = result.cursor
            has_more = result.has_more
