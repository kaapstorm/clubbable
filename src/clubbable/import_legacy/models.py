"""
These models help to migrate the legacy club database schema to the current
"""
from django.db import models


class Office(models.Model):
    office = models.CharField(max_length=50)
    
    def __str__(self):
        return self.office

    class Meta:
        db_table = 'owl_offices'
        managed = False
        

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
    interests = models.CharField(
        max_length=len(','.join((c[0] for c in INTEREST_CHOICES)))
    )
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
        return f'Owl {self.common_name} {self.surname}'

    class Meta:
        db_table = 'owl_members'
        managed = False


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
        return self.title

    class Meta:
        db_table = 'cartoons'
        managed = False


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
        return self.title

    class Meta:
        db_table = 'photographs'
        managed = False


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
        return f'(User) {self.fullname}'

    class Meta:
        db_table = 'users'
        managed = False


class Group(models.Model):
    name = models.CharField(max_length=50)
    users = models.ManyToManyField(User, db_table='group_users')
    
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'groups'
        managed = False


class Notice(models.Model):
    date = models.DateField()
    description = models.CharField(max_length=50)
    filename = models.CharField(max_length=255)
    read_by = models.ManyToManyField(User, through='NoticeReadBy')
    
    def __str__(self):
        return self.description

    class Meta:
        db_table = 'notices'
        managed = False


class NoticeReadBy(models.Model):
    notice = models.ForeignKey(Notice, models.CASCADE)
    user = models.ForeignKey(User, models.CASCADE)
    last_read_on = models.DateTimeField()
    
    class Meta: 
        db_table = 'notices_readby'
        managed = False


class Document(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    filename = models.CharField(max_length=50)
    filetype = models.CharField(max_length=50)
    filesize = models.PositiveIntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.name} ({self.description})'

    class Meta:
        db_table = 'documents'
        managed = False


# New site does not support legacy quicklinks
