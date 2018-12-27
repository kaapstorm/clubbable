"""
Import members, users, photographs, cartoons, notices and documents from the
legacy database. This should be done after members, guests and meetings have
been imported using import_mdb.
"""
from datetime import date
import os
import re
from django.core.files import File
from django.core.files.images import ImageFile
from django.db import IntegrityError
import magic
from club.models import Member, Meeting, Profile, User
from docs.models import Document, Folder
from galleries.models import Gallery, Image
from import_legacy.models import (
    User as OriginalUser,
    Member as OriginalMember,
    Cartoon as OriginalCartoon,
    Photograph as OriginalPhotograph,
    Notice as OriginalNotice,
    Document as OriginalDocument,
)


def alt_slugify(string):
    """An alternative slugify that uses underscores.
    """
    string = re.sub('\s+', '_', string)
    string = re.sub('[^\w.-]', '', string)
    return string.strip('_.- ').lower()


def import_members():
    for original in OriginalMember.objects.all():
        # Check whether Member has already been imported
        if Member.objects.filter(pk=original.id).count():
            continue
        # Create Member
        Member.objects.create(
            id=original.id,
            title=original.title,
            initials=original.initials,
            last_name=original.surname,
            post_title='',
            familiar_name=original.common_name,
            year=original.election_year,
            email=original.email,
            receives_emails=False,
            qualification_art=('Art' in original.interests),
            qualification_drama=('Drama' in original.interests),
            qualification_literature=('Literature' in original.interests),
            qualification_music=('Music' in original.interests),
            qualification_science=('Science' in original.interests),
            hon_life_member=original.honorary_life_member,
            canonisation_date=None,
        )


def import_users():
    for original in OriginalUser.objects.all():
        # Split fullname into first_name and last_name
        try:
            first_name, last_name = original.fullname.split(' ', 1)
        except ValueError:
            first_name = ''
            last_name = original.fullname
        # Determine last_login, or set to 1 Jan 1970
        if original.last_login is None:
            last_login = date(1970, 1, 1)
        else:
            last_login = original.last_login
        # Create user
        user = User.objects.create(
            email=original.email,
            first_name=first_name,
            last_name=last_name,
            password='md5$$%s' % (original.password,),
            is_staff=False,
            is_active=original.is_login_enabled,
            is_superuser=False,
            last_login=last_login,
            date_joined=last_login,
        )
        # Create profile if Member is not yet associated with a user
        profile = Profile.objects.create(user=user)
        try:
            member = Member.objects.get(pk=original.member.id)
            # Set Member.send_emails
            member.receives_emails = original.notify_by_email
            member.save()
        except OriginalMember.DoesNotExist:
            # Happens when memberID == 0
            pass
        else:
            try:
                profile.member = member
                profile.save()
            except IntegrityError:
                # Old database allowed a Member to have multiple users
                pass


def import_cartoons(files_path):
    """Migrate data, and copy the original image to its new location.
    """
    pattern = re.compile(r'^(\d{4})\-(\d{2})\-(\d{2}) ')
    gallery = Gallery.objects.get(name='Cartoons')
    for original in OriginalCartoon.objects.all():
        matches = pattern.match(original.filename)
        year, month, day = matches.groups()
        meeting = Meeting.objects.get_or_none(date=date(year, month, day))
        member = Member.objects.get_or_none(pk=original.member.id)
        artist = Member.objects.get_or_none(pk=original.artist.id)
        cartoon = Image.objects.create(
            gallery=gallery,
            description=original.title,
            creator=artist,
            meeting=meeting,
            # original=image_file, # Not a nice filename
        )
        if member:
            cartoon.members.add(member)
        # Give the file a nice filename
        filepath = '{path}/cartoons/full/{filename}'.format(
            path=files_path,
            filename=original.filename
        )
        image_file = ImageFile(open(filepath, 'rb'))
        cartoon.original.save(alt_slugify(cartoon.description)+'.jpg',
                              image_file)
        cartoon.save()


def import_photographs(files_path):
    gallery = Gallery.objects.get(name='Photographs')
    for original in OriginalPhotograph.objects.all():
        photographer = Member.objects.get_or_none(pk=original.photographer.id)
        meeting = Meeting.objects.get_or_none(date=original.date)
        photo = Image.objects.create(
            gallery=gallery,
            description=original.title,
            creator=photographer,
            meeting=meeting,
        )
        for member in original.members.all():
            member = Member.objects.get(pk=member.id)
            photo.members.add(member)
        filepath = '{path}/photographs/full/{filename}'.format(
            path=files_path,
            filename=original.filename
        )
        image_file = ImageFile(open(filepath, 'rb'))
        photo.original.save(alt_slugify(photo.description)+'.jpg', image_file)
        photo.save()


def import_notices(files_path):
    mime = magic.Magic(mime=True)
    folder = Folder.objects.get(name='Notices')
    for original in OriginalNotice.objects.all():
        filepath = '{path}/notices/{filename}'.format(
            path=files_path,
            filename=original.filename
        )
        file_ = File(open(filepath, 'rb'))
        meeting = Meeting.objects.get_or_none(date=original.date)
        notice = Document.objects.create(
            folder=folder,
            description='%s (%s)' % (original.description, str(original.date)),
            meeting=meeting,
            content_type=mime.from_file(filepath),
        )
        notice.file.save(alt_slugify(notice.description) + '.pdf', file_)
        notice.save()


def import_documents(files_path):
    mime = magic.Magic(mime=True)
    folder = Folder.objects.get(name='Documents')
    for original in OriginalDocument.objects.all():
        filepath = '{path}/documents/{filename}'.format(
            path=files_path,
            filename=original.filename
        )
        file_ = File(open(filepath, 'rb'))
        if original.description:
            description = '%s (%s)' % (original.name, original.description)
        else:
            description = original.name
        document = Document.objects.create(
            folder=folder,
            description=description,
            content_type=mime.from_file(filepath),
        )
        # Give the file a nice filename. Use original extension, in lowercase.
        ext = os.path.splitext(original.filename)[1].lower()
        if len(ext) < 0:
            ext = '.pdf'  # Use ".pdf" if no extension found
        document.file.save(alt_slugify(document.description) + ext, file_)
        document.save()


def import_legacy(incl_files=True, files_path=None):
    """
    Import from a legacy database

    Connection details are configured in settings.DATABASES['legacy']

    :param incl_files: Whether to include documents and images
    :param files_path: Path to files.
    """
    # First migrate users, before things that link to them
    import_members()
    import_users()

    if incl_files:
        import_cartoons(files_path)
        import_photographs(files_path)
        import_notices(files_path)
        import_documents(files_path)
