import doctest

from django.test import SimpleTestCase

from club.models import Member, Guest, Meeting
import import_mdb.tasks
from import_mdb.tasks import ATTRIBUTES


class TestModelAttributes(SimpleTestCase):

    def test_member_attributes(self):
        for attribute in ATTRIBUTES['Member']:
            self.assertIn(attribute[0], dir(Member))

    def test_guest_attributes(self):
        for attribute in ATTRIBUTES['Guest']:
            self.assertIn(attribute[0], dir(Guest))

    def test_meeting_attributes(self):
        for attribute in ATTRIBUTES['Meeting']:
            self.assertIn(attribute[0], dir(Meeting))


class DocTests(SimpleTestCase):

    def test_doctests(self):
        results = doctest.testmod(import_mdb.tasks)
        self.assertEqual(results.failed, 0)
