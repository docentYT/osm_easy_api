import unittest

import responses

from osm_easy_api.api import Api


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
        self.assertEqual(
            api._headers, {"Authorization": "Bearer TOKEN", "User-Agent": "AGENT"}
        )

    @responses.activate
    def test__request_200(self):
        api = Api()

        responses.add(
            **{
                "method": responses.POST,
                "url": "http://test.pl/",
                "status": 200,
            }
        )
        response = api._request(method=Api._RequestMethods.POST, url="http://test.pl/")
        self.assertEqual(response.status_code, 200)

    @responses.activate
    def test__request_400(self):
        api = Api()

        responses.add(
            **{
                "method": responses.POST,
                "url": "http://test.pl/",
                "status": 400,
                "body": "BODY_FROM_RESPONSE",
            }
        )

        with self.assertRaises(ValueError) as context:
            api._request(method=Api._RequestMethods.POST, url="http://test.pl/")

        self.assertIn("BODY_FROM_RESPONSE", str(context.exception))
