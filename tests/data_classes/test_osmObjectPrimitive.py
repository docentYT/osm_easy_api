import unittest

from osm_easy_api.data_classes import Tags
from osm_easy_api.data_classes.osm_object_primitive import osm_object_primitive

class TestOsmObjectPrimitive(unittest.TestCase):
    def test_basic_initalization(self):
        obp = osm_object_primitive(
            id=123,
            visible=True, 
            version=1, 
            changeset_id=321,
            timestamp="2022-11-11T21:15:26Z", 
            user_id=111
        )

        should_print = "osm_object_primitive(id = 123, visible = True, version = 1, changeset_id = 321, timestamp = 2022-11-11T21:15:26Z, user_id = 111, tags = {}, )"
        self.assertEqual(str(obp), should_print)


    def test__to_xml(self):
        obp = osm_object_primitive(
            id=123,
            visible=True, 
            version=1, 
            changeset_id=321,
            timestamp="2022-11-11T21:15:26Z", 
            user_id=111,
            tags=Tags({"abc": "cba"})
        )

        element = obp._to_xml(999)
        self.assertEqual(element.tagName, "osm_object_primitive")
        self.assertEqual(element.getAttribute("id"),          str(123))
        self.assertEqual(element.getAttribute("version"),     str(1))
        self.assertEqual(element.getAttribute("changeset"),   str(999))

        element = obp._to_xml(999, member_version=True)
        self.assertEqual(element.tagName, "member")
        self.assertEqual(element.getAttribute("ref"), str(123))
        self.assertEqual(element.getAttribute("role"), "")

        element = obp._to_xml(999, member_version=True, role="ABC")
        self.assertEqual(element.tagName, "member")
        self.assertEqual(element.getAttribute("ref"), str(123))
        self.assertEqual(element.getAttribute("role"), "ABC")