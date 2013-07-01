from django.test import TestCase
from django.conf import settings


class HomeViewTestCase(TestCase):
    settings.GEOIP_DEBUG = False

    def test_wrong_city(self):

        resp = self.client.get('/', REMOTE_ADDR="217.12.211.117")
        self.assertFalse('city' in resp.context)

    def test_correct_city(self):

        resp = self.client.get('/', REMOTE_ADDR="108.160.163.28")
        self.assertTrue('city' in resp.context)
        resp = self.client.get('/', REMOTE_ADDR="96.43.148.26")
        self.assertTrue('city' in resp.context)