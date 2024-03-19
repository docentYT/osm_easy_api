import unittest

from osm_easy_api.data_classes import GpxFile, Visibility

class TestWay(unittest.TestCase):
    def test_basic_initalization(self):
        gpxFile = GpxFile(
            id=123,
            name="hello.gpx",
            user_id=111,
            visibility=Visibility.PRIVATE,
            pending=False, 
            timestamp="tomorrow",
            latitude="10",
            longitude="20",
            description="hello world!",
            tags=["alfa"]
        )
        should_print = "GpxFile(id = 123, name = hello.gpx, user_id = 111, visibility = Visibility.PRIVATE, pending = False, timestamp = tomorrow, latitude = 10, longitude = 20, description = hello world!, tags = ['alfa'], )"
        self.assertEqual(str(gpxFile), should_print)

    def test__to_xml(self):
        gpxFile = GpxFile(
            id=123,
            name="hello.gpx",
            user_id=111,
            visibility=Visibility.PRIVATE,
            pending=False, 
            timestamp="tomorrow",
            latitude="10",
            longitude="20",
            description="hello world!",
            tags=["alfa"]
        )

        element = gpxFile._to_xml()
        self.assertEqual(element.tagName, "gpx_file")
        self.assertEqual(element.getAttribute("id"),            str(123))
        self.assertEqual(element.getAttribute("name"),          "hello.gpx")
        self.assertEqual(element.getAttribute("uid"),           str(111))
        self.assertEqual(element.getAttribute("visibility"),    "private")
        self.assertEqual(element.getAttribute("pending"),       "false")
        self.assertEqual(element.getAttribute("timestamp"),     "tomorrow")
        self.assertEqual(element.getAttribute("lat"),           "10")
        self.assertEqual(element.getAttribute("lon"),           "20")

        self.assertEqual(element.childNodes[0].tagName, "description")
        self.assertEqual(element.childNodes[0].firstChild.nodeValue, "hello world!")
        self.assertEqual(element.childNodes[1].firstChild.nodeValue, "alfa")