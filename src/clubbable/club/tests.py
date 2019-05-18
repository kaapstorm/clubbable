from contextlib import contextmanager
from datetime import date
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from club.models import Member, Guest, Meeting, User


@contextmanager
def user_context():
    details = {'email': 'testy@example.com', 'password': 's3cr3t'}
    user = User(email=details['email'])
    user.set_password(details['password'])
    user.save()
    details['id'] = user.id
    try:
        yield details
    finally:
        user.delete()


class TestMember(TestCase):

    def setUp(self):
        self.orig_member_title = settings.MEMBER_TITLE
        self.member = Member(
            title='Sir',
            initials='M.E.',
            last_name='Palin',
            post_title='CBE FRGS',
            familiar_name='Michael'
        )

    def tearDown(self):
        settings.MEMBER_TITLE = self.orig_member_title

    def test_unicode_with_member_title(self):
        settings.MEMBER_TITLE = 'Rotarian'
        self.assertEqual(str(self.member), 'Rotarian Michael Palin')

    def test_unicode_without_member_title(self):
        settings.MEMBER_TITLE = None
        self.assertEqual(str(self.member), 'Michael Palin')

    def test_get_formal_name(self):
        self.assertEqual(self.member.get_formal_name(),
                         'Sir M.E. Palin CBE FRGS')

    # TODO: Test sync_email
    # def test_sync_email(self):
    #     ...


class TestGuest(TestCase):

    def test_unicode(self):
        guest = Guest(
            title='Mr',
            first_name='Eric',
            last_name='Idle'
        )
        self.assertEqual(str(guest), 'Mr Eric Idle')


class TestMeeting(TestCase):

    def test_unicode(self):
        meeting = Meeting(
            year=2013,
            month=2,
            date=date(2014, 3, 22),
            name='Meeting'
        )
        self.assertEqual(str(meeting), 'Meeting (March 2014)')


class TestUser(TestCase):

    def test_create_superuser(self):
        user_data = {'email': 'testy@example.com', 'password': 's3cr3t'}
        UserModel = get_user_model()
        try:
            user = UserModel.objects.create_superuser(**user_data)
        except Exception as err:
            assert False, str(err)
        else:
            user.delete()


class DashboardViewTests(TestCase):

    def test_dashboard_unauthenticated(self):
        """
        The dashboard view should redirect if the user isn't authenticated
        """
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_authenticated(self):
        """
        The dashboard view should return status 200 if user is authenticated
        """
        with user_context() as user:
            self.client.login(email=user['email'], password=user['password'])
            # Check login was successful
            self.assertIn('_auth_user_id', self.client.session)
            self.assertEqual(int(self.client.session['_auth_user_id']),
                             user['id'])

            response = self.client.get(reverse('dashboard'))
            self.assertEqual(response.status_code, 200)
