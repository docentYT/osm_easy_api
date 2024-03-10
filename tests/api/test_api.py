import unittest

from osm_easy_api import Api

class TestApi(unittest.TestCase):
    def test_initialize(self):
        Api("https://test.pl")

    def test_empty_headers(self):
        api = Api()
        self.assertEqual(api._headers, {})

    def test_authorization_header(self):
        api = Api(access_token="TOKEN")
        self.assertEqual(api._headers, {"Authorization": "Bearer TOKEN"})

    def test_user_agent_header(self):
        api = Api(user_agent="AGENT")
        self.assertEqual(api._headers, {"User-Agent": "AGENT"})

    def test_authorization_and_user_agent_header(self):
        api = Api(access_token="TOKEN", user_agent="AGENT")
        self.assertEqual(api._headers, {"Authorization": "Bearer TOKEN", "User-Agent": "AGENT"})