"""
Member, Guest and Event classes form the core of *clubbable*.

The class definitions include a field name in comments after each field. This
corresponds the the field in the Microsoft Access database that is imported to
populate *clubbable*.

The import is done by import_mdb/import_mdb.py. It is specific to the club for
which *clubbable* was written, but should be easy to customise for other
clubs, or simply ignored if the club does not use a Microsoft Access database.

"""
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import mail_admins
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model where the username is the email address
    """

    username = None
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("A user with that email address already exists."),
        },
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # USERNAME_FIELD will always be prompted for

    def get_full_name(self):
        try:
            full_name = self.profile.member.get_full_name()
        except User.profile.RelatedObjectDoesNotExist:
            full_name = super().get_full_name()
        return full_name or self.get_username()

    def receives_emails(self):
        try:
            return self.profile.member.receives_emails
        except User.profile.RelatedObjectDoesNotExist:
            # Assume users without corresponding members want to receive
            # emails
            return True


class GetOrNoneManager(models.Manager):
    """
    Adds get_or_none method to objects
    """
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None
        # unlike objects.first(), preserves MultipleObjectsReturned


# Remember to update migrations file with `./manage.py makemigrations club` if
# you change these models
class Member(models.Model):
    """
    Member instances can be sent e-mails. They and Guest instances are
    associated with gallery images.
    """
    # Comments refer to the equivalent column in this club's Access database.
    # See module docstring for context.
    id = models.PositiveIntegerField(primary_key=True)  # OwlID
    title = models.CharField(max_length=100, blank=True)  # Title
    initials = models.CharField(max_length=100)  # Initials
    last_name = models.CharField(max_length=100)  # Lastname
    post_title = models.CharField(max_length=100, blank=True)  # PostTitle
    familiar_name = models.CharField(max_length=100)  # FamiliarName
    # Address Label Sheet
    # Address1
    # Address2
    # Address3
    # Address4
    # Address5
    # Address6
    year = models.PositiveIntegerField(null=True, blank=True)  # Year
    # MembershipCategory
    # Interests -- Not authoritative. Use booleans below instead.
    # PastPresident
    # RegularDiner
    # CaptureDateOfLastChange
    # EffectiveDateOfLastChange
    # Comment
    # Birthdate
    # HomeTelephone
    # WorkTelephone
    # MobileTelephone
    email = models.CharField(max_length=150, blank=True)  # EmailAddress
    receives_emails = models.BooleanField(  # ReceivesNoticesElectronically
        default=False,
    )
    # Proposer
    # Seconder
    # SpouseName
    # PreferredFax
    # AddressCategory
    qualification_art = models.BooleanField(default=False)  # Art
    qualification_drama = models.BooleanField(default=False)  # Drama
    qualification_literature = models.BooleanField(default=False)  # Literature
    qualification_music = models.BooleanField(default=False)  # Music
    qualification_science = models.BooleanField(default=False)  # Science
    hon_life_member = models.BooleanField(  # HonLifeMember
        verbose_name='Honorary life member', default=False,
    )
    canonisation_date = models.DateField(  # CanonisationDate
        null=True, blank=True,
    )
    # Category
    # ExternalRole1
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    profile_image = models.ForeignKey(
        'galleries.Image', models.SET_NULL, null=True, blank=True,
    )

    # Used by import_legacy to find foreign keys
    objects = GetOrNoneManager()

    class Meta:
        ordering = ('last_name', 'familiar_name')

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        if settings.MEMBER_TITLE:
            return ' '.join((
                settings.MEMBER_TITLE,
                self.familiar_name,
                self.last_name
            ))
        return ' '.join((self.familiar_name, self.last_name))

    def get_formal_name(self):
        return ' '.join((
            self.title,
            self.initials,
            self.last_name,
            self.post_title,
        ))

    @staticmethod
    def sync_email(sender, instance, **kwargs):
        """
        Compare e-mail address with that of corresponding user (if exists). If
        necessary, sync and notify admin.
        """
        member = instance
        try:
            user = member.profile.user
        except Member.profile.RelatedObjectDoesNotExist:
            # This member does not have an associated user
            return
        if user.email == member.email:
            # The e-mail address did not change
            return
        user.email = member.email
        user.save()
        mail_admins(
            'User address changed',
            'The e-mail address of {} has changed from {} to {}.'.format(
                member, user.email, member.email)
        )


post_save.connect(Member.sync_email, sender=Member)


class Guest(models.Model):
    """
    Guest and Member instances are associated with gallery images.
    """
    id = models.PositiveIntegerField(    # GuestID Int8
        primary_key=True, editable=False,
    )
    date_of_listing = models.DateField()  # DateOfListing Timestamp
    last_name = models.CharField(max_length=100)  # GuestLastName Char(100)
    first_name = models.CharField(max_length=100)  # GuestFirstName Char(100)
    initials = models.CharField(max_length=100)  # GuestInitials Char(100)
    title = models.CharField(max_length=100)  # GuestTitle Char(100)
    admitted_to_club = models.BooleanField(  # AdmittedToOwldom Bool
        default=False
    )
    date_admitted = models.DateField(  # DateAdmitted Timestamp
        null=True, blank=True,
    )
    member = models.ForeignKey(  # MemberNum Int8
        Member, models.SET_NULL, null=True, blank=True,
    )
    delisted = models.BooleanField(default=False)  # Delisted Bool
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = GetOrNoneManager()

    class Meta:
        ordering = ('last_name', 'first_name')

    def __str__(self):
        return ' '.join((self.title, self.first_name, self.last_name))


class Meeting(models.Model):
    """
    Gallery images may be associated with an Meeting.
    """
    id = models.PositiveIntegerField(  # EventNum Int8
        primary_key=True, editable=False,
    )
    year = models.PositiveIntegerField()  # Year Int8
    month = models.PositiveIntegerField()  # Month Int8
    date = models.DateField()  # EventDate Timestamp
    name = models.CharField(max_length=100, blank=True)  # Name Char(100)
    status = models.CharField(max_length=100, blank=True)  # Status Char(100)
    number_of_tables = models.PositiveSmallIntegerField()  # NumberOfTables
    comment = models.CharField(max_length=100, blank=True)  # Comment Char(100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = GetOrNoneManager()

    def __str__(self):
        # Note that the year and month fields are ignored. Just the date field
        # is used. This is because we import the year and month fields, if they
        # are available, for the sake of completeness
        return '{} ({})'.format(self.name, self.date.strftime('%B %Y'))


class Profile(models.Model):
    """
    Profile table links users with Members. Users need not be Members, and
    Members need not have an associated User.
    """
    user = models.OneToOneField(User, models.CASCADE)
    # Members can only be associated with one user. To allow the mailer to
    # send to other organisations and non-members, Users do not need to be
    # Members.
    member = models.OneToOneField(Member, models.CASCADE)

    def __str__(self):
        return '%s (%s)' % (self.user, self.member)

    @staticmethod
    def create_profile(sender, instance, created, **kwargs):
        if created:
            member = Member.objects.get_or_none(email=instance.email)
            if member:
                Profile.objects.create(user=instance, member=member)


post_save.connect(Profile.create_profile, sender=User)
