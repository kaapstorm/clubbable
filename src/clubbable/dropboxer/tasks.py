from contextlib import contextmanager, closing
from tempfile import NamedTemporaryFile
from celery import shared_task
from django.conf import settings
from dropbox import Dropbox
from dropbox.files import FileMetadata
from club.models import User
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


@quickcache([])
def get_folders():
    """
    Returns a dictionary of lower-case folder names to folder instances
    """
    return {f.name.lower(): f for f in Folder.objects.all()}


@quickcache(['folder_name'])
def get_doc_file_ids(folder_name):
    """
    Returns a set of the Dropbox file IDs of the documents in a given
    folder
    """
    folder = get_folders()[folder_name]
    return {d.dropbox_file_id for d in folder.document_set.all()}


def get_folder(path):
    """
    Returns the folder of a file specified by a path

    >>> get_folder('/foo/bar/baz.txt')
    'bar'

    """
    try:
        return path.split('/')[-2]
    except IndexError:
        return None


def is_new_document(entry):
    folder_name = get_folder(entry.path_lower)
    return (
            isinstance(entry, FileMetadata) and
            folder_name and
            folder_name in get_folders() and
            entry.id not in get_doc_file_ids(folder_name)
    )


def import_document(dbx, entry):
    folder_name = get_folder(entry.path_lower)
    folder = get_folders()[folder_name]
    _, response = dbx.files_download(entry.path_lower)
    with closing(NamedTemporaryFile()) as tmp_file:
        tmp_file.write(response.content)
        Document.objects.create(
            folder=folder,
            description=entry.name,
            dropbox_file_id=entry.id,
            file=tmp_file.name,
        )


@shared_task
def process_changes(username):
    """
    Call /files/list_folder for the given user and process any changes.
    """
    try:
        dropbox_user = User.objects.get(email=username).dropbox_user
    except User.dropbox_user.RelatedObjectDoesNotExist:
        return

    if dropbox_user.is_locked:
        return

    with lock_dropbox_user(dropbox_user):
        dbx = Dropbox(dropbox_user.access_token)
        cursor = dropbox_user.cursor
        has_more = True

        while has_more:
            if not cursor:
                result = dbx.files_list_folder(path='', recursive=True)
            else:
                result = dbx.files_list_folder_continue(cursor)

            for entry in result.entries:
                if is_mdb_file(entry):
                    _, response = dbx.files_download(entry.path_lower)
                    with closing(NamedTemporaryFile()) as tmp_file:
                        tmp_file.write(response.content)
                        import_mdb(tmp_file.name)
                elif is_new_document(entry):
                    import_document(dbx, entry)

            cursor = result.cursor
            has_more = result.has_more

        dropbox_user.cursor = cursor
        dropbox_user.save()
