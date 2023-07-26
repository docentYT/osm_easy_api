import unittest

from osm_easy_api import Api

class TestApi(unittest.TestCase):
    def test_initialize(self):
        Api("https://test.pl")

    def test_credintials(self):
        api = Api(username="abc", password="cba")
        self.assertIsNotNone(api._auth)
        self.assertEqual(api._auth.username.decode(), "abc")
        self.assertEqual(api._auth.password.decode(), "cba")

        api = Api(username="ęśąćź", password="ąęźż")
        self.assertIsNotNone(api._auth)
        self.assertEqual(api._auth.username.decode(), "ęśąćź")
        self.assertEqual(api._auth.password.decode(), "ąęźż")