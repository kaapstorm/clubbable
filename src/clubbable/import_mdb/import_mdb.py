"""
Import members, guests and meetings from a Microsoft Access database.

Check table names, and columns to customise for your database.
"""
import csv
from datetime import datetime
import re
from subprocess import check_output
from club.models import Member, Meeting, Guest


MDB_EXPORT_CMD = '/usr/bin/mdb-export'
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
        ('email', 'EmailAddress', False, None),
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

    output = check_output((MDB_EXPORT_CMD, filename, table))
    rows = output.decode('utf-8').split('\n')
    reader = csv.DictReader(rows)

    lines = 0
    for row in reader:
        lines += 1
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
    if (
        delete and
        1 < lines == class_.objects.filter(updated_at__gte=start).count()
    ):
        # Delete all records not found in import
        class_.objects.filter(updated_at__lt=start).delete()


def import_members(filename):
    import_table(filename, Member, 'OwlsPersonalDetails', 'OwlID')


def import_guests(filename):
    import_table(filename, Guest, 'Guests', 'GuestID')


def import_meetings(filename):
    import_table(filename, Meeting, 'Events', 'EventNum')


def import_mdb(filename):
    import_members(filename)
    import_guests(filename)
    import_meetings(filename)
