"""
Import members, guests and meetings from a Microsoft Access database.

Check table names, and columns to customise for your database.
"""
import csv
import inspect
from datetime import datetime
import re

import requests
from django.conf import settings
from django.core.mail import mail_admins
from club.models import Member, Meeting, Guest


MDB_DATE_RE = re.compile(r'^(\d{2})/(\d{2})/(\d{2}) 00:00:00$')
ATTRIBUTES = {
    'Member': (
        # model attribute, table column, is nullable, transform
        ('title', 'Title', False, None),
        ('initials', 'Initials', False, None),
        ('last_name', 'Lastname', False, None),
        ('post_title', 'PostTitle', False, None),
        ('familiar_name', 'FamiliarName', False, None),
        ('year', 'Year', True, None),
        ('email', 'EmailAddress', False, 'none_to_blank'),
        ('receives_emails', 'ReceivesNoticesElectronically', False, None),
        ('qualification_art', 'Art', False, None),
        ('qualification_drama', 'Drama', False, None),
        ('qualification_literature', 'Literature', False, None),
        ('qualification_music', 'Music', False, None),
        ('qualification_science', 'Science', False, None),
        ('hon_life_member', 'HonLifeMember', False, None),
        ('canonisation_date', 'CanonisationDate', True, 'transform_date'),
    ),
    'Guest': (
        ('date_of_listing', 'DateOfListing', True, 'transform_date'),
        ('last_name', 'GuestLastName', False, None),
        ('first_name', 'GuestFirstName', False, None),
        ('initials', 'GuestInitials', False, None),
        ('title', 'GuestTitle', False, None),
        ('admitted_to_club', 'AdmittedToOwldom', False, None),
        ('date_admitted', 'DateAdmitted', True, 'transform_date'),
        ('member_id', 'MemberNum', True, None),
        ('delisted', 'Delisted', False, None),
    ),
    'Meeting': (
        ('year', 'Year', False, None),
        ('month', 'Month', False, None),
        ('date', 'EventDate', False, 'transform_date'),
        ('name', 'Name', False, None),
        ('status', 'Status', False, None),
        ('number_of_tables', 'NumberOfTables', False, None),
        ('comment', 'Comment', False, None),
    ),
}


def transform_date(mdb_date):
    """
    Transforms an MM/DD/YY-formatted date to an ISO-formatted date

    >>> transform_date('12/31/01 00:00:00')
    '2001-12-31'
    >>> transform_date('12/31/99 00:00:00')
    '1999-12-31'

    """

    def to_iso_date(matches):
        """
        Converts regex match object into YYYY-MM-DD string
        """
        mm, dd, yy = matches.groups()
        now = datetime.now()
        if int(yy) > (now.year % 100):
            # Must be last century
            last_c = now.year // 100 - 1
            yyyy = str(last_c) + yy
        else:
            yyyy = str(now.year // 100) + yy
        return '%s-%s-%s' % (yyyy, mm, dd)

    return MDB_DATE_RE.sub(to_iso_date, mdb_date)


def none_to_blank(value):
    """
    Convert "(none)" to empty string

    >>> none_to_blank('(none)')
    ''
    >>> none_to_blank('spam')
    'spam'

    """
    return '' if value == '(none)' else value


def fetch_mdb_dump(filename, table):
    response = requests.post(
        settings.MDB_DUMP_URL,
        auth=(settings.MDB_DUMP_USERNAME, settings.MDB_DUMP_PASSWORD),
        data={'table_name': table},
        files={'mdb_file': open(filename, 'rb')},
    )
    return response.text


def import_table(filename, class_, table, id_, delete=True):
    """
    Imports a table from an Access database.

    :param class_: The Django ORM to populate
    :param table: The Access database table name
    :param id_: The name of the primary key field
    :param attributes: A tuple of attribute-column tuples
    :param delete: Delete records not found in Access
    """
    attributes = ATTRIBUTES[class_.__name__]
    start = datetime.now()

    output = fetch_mdb_dump(filename, table)
    rows = output.split('\n')
    reader = csv.DictReader(rows)

    upserted = 0
    deleted = 0
    for row in reader:
        try:
            obj = class_.objects.get(pk=row[id_])
        except class_.DoesNotExist:
            obj = class_(id=row[id_])
        for attr, column, nullable, transform in attributes:
            if nullable and len(row[column]) == 0:
                value = None
            elif transform is not None:
                func = globals()[transform]
                value = func(row[column])
            else:
                value = row[column]
            setattr(obj, attr, value)
        obj.save()
        upserted += 1
    if (
        delete and
        0 < upserted == class_.objects.filter(updated_at__gte=start).count()
    ):
        # Delete all records not found in import
        deleted, __ = class_.objects.filter(updated_at__lt=start).delete()
    return upserted, deleted


def import_members(filename):
    return import_table(filename, Member, 'OwlsPersonalDetails', 'OwlID')


def import_guests(filename):
    return import_table(filename, Guest, 'Guests', 'GuestID')


def import_meetings(filename):
    return import_table(filename, Meeting, 'Events', 'EventNum')


def import_mdb(filename):
    member_ups, member_dels = import_members(filename)
    guest_ups, guest_dels = import_guests(filename)
    meeting_ups, meeting_dels = import_meetings(filename)
    mail_admins('Imported Access database', inspect.cleandoc("""
        Members:
          - Added/updated: {member_ups}
          - Deleted: {member_dels}

        Guests:
          - Added/updated: {guest_ups}
          - Deleted: {guest_dels}

        Meetings:
          - Added/updated: {meeting_ups}
          - Deleted: {meeting_dels}
        """.format(
            member_ups=member_ups,
            member_dels=member_dels,
            guest_ups=guest_ups,
            guest_dels=guest_dels,
            meeting_ups=meeting_ups,
            meeting_dels=meeting_dels,
        )
    ))
