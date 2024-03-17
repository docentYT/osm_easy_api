import unittest
import responses
from responses.matchers import multipart_matcher
import os
import filecmp

from ..fixtures.default_variables import TOKEN

from osm_easy_api import Api
from osm_easy_api.api import exceptions as ApiExceptions


class TestApiGpx(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.API = Api(url="https://test.pl", access_token=TOKEN)

    @responses.activate
    def test_get(self):
        URL = "https://test.pl/api/0.6/trackpoints?bbox=10,20,30,40&page=1"
        F_FROM_PATH = os.path.join("tests", "fixtures", "gps_points.gpx")
        F_TO_PATH = os.path.join("tests", "fixtures", "write_gps_points.gpx")

        with open(F_FROM_PATH, "rb") as BODY:
            responses.add(**{
                "method": responses.GET,
                "url": URL,
                "body": BODY,
                "status": 200
            })
            self.API.gpx.get(F_TO_PATH, "10", "20", "30", "40", 1)
            self.assertTrue(responses.assert_call_count(URL, 1))
            self.assertTrue(filecmp.cmp(F_FROM_PATH, F_TO_PATH, shallow=False))
            os.remove(F_TO_PATH)

    @responses.activate
    def test_create(self):
        URL = "https://test.pl/api/0.6/gpx/create"
        F_FROM_PATH = os.path.join("tests", "fixtures", "gps_points.gpx")
        
        with open(F_FROM_PATH, "rb") as f:
            matcher = multipart_matcher(
                {"file": f,
                "description": (None, "desc"),
                "tags": (None, "a,b"),
                "visibility": (None, "visib")
                },
                )
            
            responses.add(**{
                "method": responses.POST,
                "url": URL,
                "body": "1234",
                "status": 200,
                "match": [matcher]
            })
            ID = self.API.gpx.create(F_FROM_PATH, "desc", "visib", ["a", "b"])
            self.assertTrue(responses.assert_call_count(URL, 1))
            self.assertEqual(ID, 1234)