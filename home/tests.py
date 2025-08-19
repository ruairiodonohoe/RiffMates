from django.test import TestCase

# Create your tests here.


class TestHome(TestCase):
    def test_credit(self):
        response = self.client.get("/credits/")
        self.assertEqual(200, response.status_code)
