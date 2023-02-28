import unittest

from osm_easy_api import Tags

class TestTags(unittest.TestCase):
    def test_add_method(self):
        tags = Tags()
        self.assertEqual(tags, {})
        tags.add("building", "yes")
        self.assertEqual(tags, {"building": "yes"})
        tags.add("building:levels", "3")
        self.assertEqual(tags, {"building": "yes", "building:levels": "3"})
        tags.add("roof:levels", "1")
        self.assertEqual(tags, {"building": "yes", "building:levels": "3", "roof:levels": "1"})
    
    def test_set_method(self):
        tags = Tags({"building": "yes", "building:levels": "3", "roof:levels": "1"})
        tags.set("building:levels", "2")
        self.assertEqual(tags, {"building": "yes", "building:levels": "2", "roof:levels": "1"})
        tags.set("roof:shape", "flat")
        self.assertEqual(tags, {"building": "yes", "building:levels": "2", "roof:levels": "1", "roof:shape": "flat"})
        self.assertRaises(ValueError, tags.add, "building", "detached")
        self.assertEqual(tags, {"building": "yes", "building:levels": "2", "roof:levels": "1", "roof:shape": "flat"})

    def test_remove_method(self):
        tags = Tags({"building": "yes", "building:levels": "3", "roof:levels": "1"})
        tags.remove("building:levels")
        self.assertEqual(tags, {"building": "yes", "roof:levels": "1"})

    def test_get(self):
        tags = Tags({"building": "yes", "building:levels": "3", "roof:levels": "1"})
        self.assertEqual(tags.get("building"), "yes")
        self.assertEqual(tags.get("roof:levels"), "1")
        self.assertEqual(tags.get("natural"), None)

    def test__to_xml(self):
        tags = Tags({"building": "yes", "building:levels": "3", "roof:levels": "1"})
        xml = tags._to_xml()
        
        nxt = next(xml)
        self.assertEqual(nxt.getAttribute("k"), "building")
        self.assertEqual(nxt.getAttribute("v"), "yes")
        nxt = next(xml)
        self.assertEqual(nxt.getAttribute("k"), "building:levels")
        self.assertEqual(nxt.getAttribute("v"), "3")
        nxt = next(xml)
        self.assertEqual(nxt.getAttribute("k"), "roof:levels")
        self.assertEqual(nxt.getAttribute("v"), "1")