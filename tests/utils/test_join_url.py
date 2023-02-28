import unittest

from osm_easy_api.utils import join_url

class TestMiscJoinUrl(unittest.TestCase):
    def test_join(self):
        self.assertEqual(join_url(), "")
        self.assertEqual(join_url("google.com", "photos"), "google.com/photos")
        self.assertEqual(join_url("google.com", 45), "google.com/45")