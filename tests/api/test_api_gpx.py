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
    def test_get_gps_points(self):
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

    @responses.activate
    def test_get_file(self):
        URL = "https://test.pl/api/0.6/gpx/2418/data"
        F_FROM_PATH = os.path.join("tests", "fixtures", "gps_points.gpx")
        F_TO_PATH = os.path.join("tests", "fixtures", "write_gps_points.gpx")

        with open(F_FROM_PATH, "rb") as BODY:
            responses.add(**{
                "method": responses.GET,
                "url": URL,
                "body": BODY,
                "status": 200
            })
            self.API.gpx.get_file(F_TO_PATH, 2418)
            self.assertTrue(responses.assert_call_count(URL, 1))
            self.assertTrue(filecmp.cmp(F_FROM_PATH, F_TO_PATH, shallow=False))
            os.remove(F_TO_PATH)

    @responses.activate
    def test_list_details(self):
        URL = "https://test.pl/api/0.6/user/gpx_files"
        BODY = """<?xml version="1.0" encoding="UTF-8"?>
<osm version="0.6" generator="OpenStreetMap server" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
	<gpx_file id="2418" name="aa.gpx" uid="18179" user="kwiatek_123 bot" visibility="trackable" pending="false" timestamp="2024-03-17T18:48:06Z" lat="52.238983" lon="21.040647">
		<description>HELLO WORLD</description>
		<tag>C</tag>
		<tag>B</tag>
		<tag>A</tag>
	</gpx_file>
	<gpx_file id="2417" name="aa.gpx" uid="18179" user="kwiatek_123 bot" visibility="trackable" pending="false" timestamp="2024-03-17T18:44:07Z" lat="52.238983" lon="21.040647">
		<description>ęśąćź#$%!#@$%ęśąćź</description>
		<tag>ęśąćź!@$*()</tag>
		<tag>ęśąćź!@</tag>
	</gpx_file>
</osm>
"""
        responses.add(**{
            "method": responses.GET,
            "url": URL,
            "body": BODY,
            "status": 200,
        })
        gpxFiles = self.API.gpx.list_details()
        self.assertTrue(responses.assert_call_count(URL, 1))
        self.assertEqual(gpxFiles[0].id, 2418)
        self.assertEqual(gpxFiles[0].name, "aa.gpx")
        self.assertEqual(gpxFiles[0].user_id, 18179)
        self.assertEqual(gpxFiles[0].visibility, Visibility.TRACKABLE)
        self.assertEqual(gpxFiles[0].pending, False)
        self.assertEqual(gpxFiles[0].timestamp, "2024-03-17T18:48:06Z")
        self.assertEqual(gpxFiles[0].latitude, "52.238983")
        self.assertEqual(gpxFiles[0].longitude, "21.040647")
        self.assertEqual(gpxFiles[0].description, "HELLO WORLD")
        self.assertEqual(gpxFiles[0].tags, ["C", "B", "A"])

        self.assertEqual(gpxFiles[1].id, 2417)
        self.assertEqual(gpxFiles[1].name, "aa.gpx")
        self.assertEqual(gpxFiles[1].user_id, 18179)
        self.assertEqual(gpxFiles[1].visibility, Visibility.TRACKABLE)
        self.assertEqual(gpxFiles[1].pending, False)
        self.assertEqual(gpxFiles[1].timestamp, "2024-03-17T18:44:07Z")
        self.assertEqual(gpxFiles[1].latitude, "52.238983")
        self.assertEqual(gpxFiles[1].longitude, "21.040647")
        self.assertEqual(gpxFiles[1].description, "ęśąćź#$%!#@$%ęśąćź")
        #                                   ęśąćź!@$^&*()
        self.assertEqual(gpxFiles[1].tags, ["ęśąćź!@$*()", "ęśąćź!@"])