"""
These models help to migrate the legacy club database schema to the current
"""
import re
from django.db import models


def strip_non_alphanumeric(string):
    """
    Strips non-alphanumeric characters
    """
    return re.sub(r'\W', '', string)


class SetField(models.Field):
    """
    Subclass of Field to accommodate MySQL SET field type. 
    
    We are really only concerned with reading the value, because we will not 
    be writing to this database, but the db_type method is nice to have.
    """
    def __init__(self, choices, *args, **kwargs):
        self.max_length = len(','.join([strip_non_alphanumeric(c[0]) 
                                        for c in choices]))
        # self.choices = choices
        super(SetField, self).__init__(*args, **kwargs)
    
    def to_python(self, value):
        return set([x for x in value.split(',')]) 
    
    def db_type(self, connection):
        if connection.settings_dict['ENGINE'] == 'django.db.backends.mysql':
            return 'SET(%s)' % (','.join(
                ["'%s'" % (strip_non_alphanumeric(c[0]),) 
                 for c in self.choices]), )
        else:
            return 'VARCHAR(%d)' % (self.max_length, )


class Office(models.Model):
    office = models.CharField(max_length=50)
    
    def __str__(self):
        return '%s' % self.office

    class Meta:
        db_table = 'owl_offices'
        

class Member(models.Model):
    INTEREST_CHOICES = (('Art', 'Art'),
                        ('Drama', 'Drama'),
                        ('Literature', 'Literature'), 
                        ('Music', 'Music'), 
                        ('Science', 'Science'))
    LOCATION_CHOICES = (('Town', 'Town'), 
                        ('Country (Africa)', 'Country (Africa)'), 
                        ('Country (Overseas)', 'Country (Overseas)'))
    MEMBERSHIP_CATEGORY_CHOICES = (('Ordinary', 'Ordinary'), 
                                   ('Suspended', 'Suspended'), 
                                   ('No longer an Owl', 'No longer an Owl'))
    id = models.PositiveIntegerField(primary_key=True)
    surname = models.CharField(max_length=50)
    title = models.CharField(max_length=20)
    initials = models.CharField(max_length=10)
    common_name = models.CharField(max_length=50)
    election_year = models.CharField(max_length=4)
    interests = SetField(choices=INTEREST_CHOICES)
    location = models.CharField(max_length=18,
                                choices=LOCATION_CHOICES)
    honorary_life_member = models.BooleanField(default=False)
    past_president = models.BooleanField(default=False)
    office = models.ForeignKey(
        Office, models.SET_NULL, null=True, db_column='office',
    )
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=32, null=True)
    street_address = models.TextField(null=True)
    membership_category = models.CharField(
        max_length=16, choices=MEMBERSHIP_CATEGORY_CHOICES,
    )
    notes = models.TextField(null=True)
    updated = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return 'Owl %s %s' % (self.common_name, self.surname)

    class Meta:
        db_table = 'owl_members'


class Cartoon(models.Model):
    date = models.DateField()
    title = models.CharField(max_length=255)
    member = models.ForeignKey(
        Member, models.SET_NULL, null=True, db_column='memberID',
    )
    artist_name = models.CharField(max_length=255, db_column='artist')
    artist = models.ForeignKey(
        Member, models.SET_NULL,
        null=True, db_column='artistID', related_name='cartoons_by',
    )
    filename = models.CharField(max_length=255)
    filetype = models.CharField(max_length=50)
    filesize = models.PositiveIntegerField()
    
    def __str__(self):
        return '%s' % self.title

    class Meta:
        db_table = 'cartoons'
    

class Photograph(models.Model):
    date = models.DateField()
    title = models.CharField(max_length=255)
    members = models.ManyToManyField(Member, db_table='photographs_members')
    photographer_name = models.CharField(
        max_length=255, db_column='photographer'
    )
    photographer = models.ForeignKey(
        Member, models.SET_NULL,
        null=True, db_column='photographerID', related_name='photographs_by',
    )
    filename = models.CharField(max_length=255)
    filetype = models.CharField(max_length=50)
    filesize = models.PositiveIntegerField()
    
    def __str__(self):
        return '%s' % self.title

    class Meta:
        db_table = 'photographs'
    

class User(models.Model):
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=32)
    fullname = models.CharField(max_length=128)
    email = models.CharField(max_length=255)
    is_login_enabled = models.BooleanField(db_column='isLoginEnabled', 
                                           default=True)
    notify_by_email = models.BooleanField(db_column='notifyByEmail', 
                                          default=True)
    email_as_attachment = models.BooleanField(db_column='emailAsAttachment',
                                              default=False)
    last_login = models.DateTimeField(db_column='lastLogin')
    member = models.ForeignKey(
        Member, models.SET_NULL, null=True, db_column='memberID',
    )
    
    def __str__(self):
        return '(User) %s' % self.fullname

    class Meta:
        db_table = 'users'


class Group(models.Model):
    name = models.CharField(max_length=50)
    users = models.ManyToManyField(User, db_table='group_users')
    
    def __str__(self):
        return '%s' % self.name

    class Meta:
        db_table = 'groups'
        

class Notice(models.Model):
    date = models.DateField()
    description = models.CharField(max_length=50)
    filename = models.CharField(max_length=255)
    read_by = models.ManyToManyField(User, through='NoticeReadBy')
    
    def __str__(self):
        return '%s' % self.description

    class Meta:
        db_table = 'notices'


class NoticeReadBy(models.Model):
    notice = models.ForeignKey(Notice, models.CASCADE)
    user = models.ForeignKey(User, models.CASCADE)
    last_read_on = models.DateTimeField()
    
    class Meta: 
        db_table = 'notices_readby'


class Document(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    filename = models.CharField(max_length=50)
    filetype = models.CharField(max_length=50)
    filesize = models.PositiveIntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return '%s (%s)' % (self.name, self.description)

    class Meta:
        db_table = 'documents'


# New site does not support legacy quicklinks
