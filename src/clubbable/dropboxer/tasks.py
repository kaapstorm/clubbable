from contextlib import contextmanager, closing
from tempfile import NamedTemporaryFile
from celery import shared_task
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from dropbox import Dropbox
from dropbox.files import FileMetadata
from club.models import User
from clubbable.utils import quickcache
from docs.models import Folder, Document
from galleries.models import Gallery, Image
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


@quickcache([])
def get_galleries():
    """
    Returns a dictionary of lower-case gallery names to gallery instances
    """
    return {g.name.lower(): g for g in Gallery.objects.all()}


@quickcache(['folder_name'])
def get_doc_file_ids(folder_name):
    """
    Returns a set of the Dropbox file IDs of the documents in a given
    folder
    """
    folder = get_folders()[folder_name]
    return {
        d.dropbox_file_id
        for d in folder.document_set.all()
        if d.dropbox_file_id
    }


@quickcache(['gallery_name'])
def get_img_file_ids(gallery_name):
    """
    Returns a set of the Dropbox file IDs of the images in a given
    gallery
    """
    gallery = get_galleries()[gallery_name]
    return {
        i.dropbox_file_id
        for i in gallery.image_set.all()
        if i.dropbox_file_id
    }


def get_directory(path):
    """
    Returns the folder of a file specified by a path

    >>> get_directory('/foo/bar/baz.txt')
    'bar'

    """
    try:
        return path.split('/')[-2]
    except IndexError:
        return None


def is_new_document(entry):
    directory = get_directory(entry.path_lower)
    return (
            isinstance(entry, FileMetadata) and
            directory and
            directory in get_folders() and
            entry.id not in get_doc_file_ids(directory)
    )


def is_new_image(entry):
    directory = get_directory(entry.path_lower)
    return (
            isinstance(entry, FileMetadata) and
            directory and
            directory in get_galleries() and
            entry.id not in get_img_file_ids(directory)
    )


def import_document(dbx, entry):
    directory = get_directory(entry.path_lower)
    folder = get_folders()[directory]
    _, response = dbx.files_download(entry.path_lower)
    content_file = ContentFile(content=response.content, name=entry.name)
    document = Document(
        folder=folder,
        description=entry.name,
        dropbox_file_id=entry.id,
        file=UploadedFile(content_file),
    )
    document.save()


def import_image(dbx, entry):
    directory = get_directory(entry.path_lower)
    gallery = get_galleries()[directory]
    _, response = dbx.files_download(entry.path_lower)
    content_file = ContentFile(content=response.content, name=entry.name)
    image = Image(
        gallery=gallery,
        description=entry.name,
        dropbox_file_id=entry.id,
        original=UploadedFile(content_file),
    )
    image.save()


@shared_task
def process_changes(username):
    """
    Call /files/list_folder for the given user and process any changes.
    """
    dropbox_user = User.objects.get(email=username).dropboxuser

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
                        for chunk in response.iter_content(chunk_size=512):
                            tmp_file.write(chunk)
                        import_mdb(tmp_file.name)
                elif is_new_document(entry):
                    import_document(dbx, entry)
                elif is_new_image(entry):
                    import_image(dbx, entry)

            cursor = result.cursor
            has_more = result.has_more

        dropbox_user.cursor = cursor
        dropbox_user.save()
