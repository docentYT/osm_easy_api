import unittest
import responses
from responses.matchers import multipart_matcher
import os
import filecmp

from osm_easy_api.data_classes import GpxFile, Visibility

from ..fixtures.default_variables import TOKEN

from osm_easy_api.api import Api


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
            self.API.gpx.get_gps_points(F_TO_PATH, "10", "20", "30", "40", 1)
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
                "visibility": (None, Visibility.PRIVATE.value)
                },
                )
            
            responses.add(**{
                "method": responses.POST,
                "url": URL,
                "body": "1234",
                "status": 200,
                "match": [matcher]
            })
            ID = self.API.gpx.create(F_FROM_PATH, "desc", Visibility.PRIVATE, ["a", "b"])
            self.assertTrue(responses.assert_call_count(URL, 1))
            self.assertEqual(ID, 1234)

    @responses.activate
    def test_update(self):
        URL = "https://test.pl/api/0.6/gpx/123"
        GPX_FILE = GpxFile(123, "aa", 123, Visibility.PUBLIC, False, "XXX", "lat", "lon", "desc", [])

        responses.add(**{
            "method": responses.PUT,
            "url": URL,
            "status": 200,
        })
        self.API.gpx.update(GPX_FILE)
        self.assertTrue(responses.assert_call_count(URL, 1))

    @responses.activate
    def test_delete(self):
        URL = "https://test.pl/api/0.6/gpx/123"
        responses.add(**{
            "method": responses.DELETE,
            "url": URL,
            "status": 200,
        })
        self.API.gpx.delete(123)
        self.assertTrue(responses.assert_call_count(URL, 1))

    @responses.activate
    def test_get_details(self):
        URL = "https://test.pl/api/0.6/gpx/2418/details"
        BODY = """<?xml version="1.0" encoding="UTF-8"?>
<osm version="0.6" generator="OpenStreetMap server" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
	<gpx_file id="2418" name="aa.gpx" uid="18179" user="kwiatek_123 bot" visibility="trackable" pending="false" timestamp="2024-03-17T18:48:06Z" lat="52.238983" lon="21.040647">
		<description>HELLO WORLD</description>
		<tag>C</tag>
		<tag>B</tag>
		<tag>A</tag>
	</gpx_file>
</osm>
"""
        responses.add(**{
            "method": responses.GET,
            "url": URL,
            "body": BODY,
            "status": 200,
        })
        gpxFile = self.API.gpx.get_details(2418)
        self.assertTrue(responses.assert_call_count(URL, 1))
        self.assertEqual(gpxFile.id, 2418)
        self.assertEqual(gpxFile.name, "aa.gpx")
        self.assertEqual(gpxFile.user_id, 18179)
        self.assertEqual(gpxFile.visibility, Visibility.TRACKABLE)
        self.assertEqual(gpxFile.pending, False)
        self.assertEqual(gpxFile.timestamp, "2024-03-17T18:48:06Z")
        self.assertEqual(gpxFile.latitude, "52.238983")
        self.assertEqual(gpxFile.longitude, "21.040647")
        self.assertEqual(gpxFile.description, "HELLO WORLD")
        self.assertEqual(gpxFile.tags, ["C", "B", "A"])