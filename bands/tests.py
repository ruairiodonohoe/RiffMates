import tempfile
from base64 import b64decode
from datetime import date

from bands.models import Musician, Venue
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings


def raises_an_error():
    raise ValueError


# Create your tests here.
class TestBands(TestCase):
    def setUp(self):
        self.musician = Musician.objects.create(
            first_name="First", last_name="Last", birth=date(1900, 1, 1)
        )
        self.PASSWORD = "notsecure"
        self.owner = User.objects.create_user("owner", password=self.PASSWORD)
        self.member = User.objects.create_user("member", password=self.PASSWORD)
        self.staff = User.objects.create_user(
            "staff", password=self.PASSWORD, is_staff=True
        )
        self.superuser = User.objects.create_superuser("admin", password=self.PASSWORD)
        self.image = "R0lGODdhAQABAIABAP///wAAACwAAAAAAQABAAACAkQBADs="
        self.image = b64decode(self.image)

        self.owner.userprofile.musician_profiles.add(self.musician)

    def test_musician_view(self):
        url = f"/bands/musician/{self.musician.id}/"
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.context["musician"].id, self.musician.id)
        self.assertIn(self.musician.first_name, str(response.content))

    def test_musician_404(self):
        url = "/bands/musician/10/"
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)

    def test_raises_an_error(self):
        with self.assertRaises(ValueError):
            raises_an_error()

    def test_edit_musician(self):
        # Can access page
        self.client.login(username="owner", password=self.PASSWORD)
        url = f"/bands/edit_musician/{self.musician.id}/"
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        # Submit form
        file = SimpleUploadedFile("test.gif", self.image)
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "birth": "1980-01-01",
            "picture": file,
        }
        response = self.client.post(url, data)
        self.assertEqual(302, response.status_code)

        musician = Musician.objects.get(id=self.musician.id)
        self.assertEqual(musician.first_name, "Updated")
        self.assertEqual(musician.last_name, "Name")
        self.assertTrue(musician.picture)

        # Staff can edit
        self.client.login(username="staff", password=self.PASSWORD)
        response = self.client.post(url, data)
        self.assertEqual(302, response.status_code)

        # Superuser can edit
        self.client.login(username="admin", password=self.PASSWORD)
        response = self.client.post(url, data)
        self.assertEqual(302, response.status_code)

        # Non-owner cannot edit
        self.client.login(username="member", password=self.PASSWORD)
        response = self.client.post(url, data)
        self.assertEqual(404, response.status_code)

    def test_edit_venue(self):
        self.client.login(username="owner", password=self.PASSWORD)
        url = "/bands/edit_venue/0/"
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        # create a venue
        data = {"name": "Name", "description": "Description"}
        response = self.client.post(url, data)
        self.assertEqual(302, response.status_code)

        # validate venue was created
        venue = Venue.objects.first()
        self.assertEqual(data["name"], venue.name)
        self.assertEqual(data["description"], venue.description)
        self.assertTrue(
            self.owner.userprofile.venues_controlled.filter(id=venue.id).exists()
        )
        # Edit Venue
        url = f"/bands/edit_venue/{venue.id}/"
        data["name"] = "Edited Name"
        response = self.client.post(url, data)

        self.assertEqual(302, response.status_code)
        venue = Venue.objects.first()
        self.assertEqual(data["name"], venue.name)

        # Verify that non-owner can't edit
        self.client.login(username="member", password=self.PASSWORD)
        response = self.client.post(url, data)
        self.assertEqual(404, response.status_code)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_edit_venue_picture(self):
        file = SimpleUploadedFile("test.gif", self.image)
        data = {"name": "Name", "description": "Description", "picture": file}

        self.client.login(username="owner", password=self.PASSWORD)
        url = "/bands/edit_venue/0/"
        response = self.client.post(url, data)

        self.assertEqual(302, response.status_code)
        venue = Venue.objects.first()
        self.assertIsNotNone(venue.picture)
