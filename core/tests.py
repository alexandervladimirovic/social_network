from django.test import TestCase

class BasicTestCase(TestCase):
    def test_homepage_status(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 404)
