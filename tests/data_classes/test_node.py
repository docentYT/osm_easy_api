import unittest

from osm_easy_api.data_classes import Node, Tags
from ..fixtures import sample_dataclasses

class TestNode(unittest.TestCase):
    def test_basic_initalization(self):
        node = Node(
            id=123,
            visible=True, 
            version=1, 
            changeset_id=321,
            timestamp="2022-11-11T21:15:26Z", 
            user_id=111,
            latitude="50.54321",
            longitude="20.12345"
        )
        should_print = "Node(id = 123, visible = True, version = 1, changeset_id = 321, timestamp = 2022-11-11T21:15:26Z, user_id = 111, tags = {}, latitude = 50.54321, longitude = 20.12345, )"
        self.assertEqual(str(node), should_print)

    def test_tags(self):
        node = sample_dataclasses.node("simple_1")
        node.tags.add("building", "yes")
        node.tags.add("building:levels", "3")
        self.assertEqual(node.tags, {"building": "yes", "building:levels": "3"})
        node.tags.add("roof:levels", "1")
        self.assertEqual(node.tags, {"building": "yes", "building:levels": "3", "roof:levels": "1"})
        node.tags.remove("building:levels")
        self.assertEqual(node.id, 123)
        self.assertEqual(node.tags, {"building": "yes", "roof:levels": "1"})

    def test__to_xml(self):
        node = sample_dataclasses.node("full_1")

        element = node._to_xml(999)
        self.assertEqual(element.tagName, "node")
        self.assertEqual(element.getAttribute("id"),          str(123))
        self.assertEqual(element.getAttribute("version"),     str(1))
        self.assertEqual(element.getAttribute("changeset"),   str(999))
        self.assertEqual(element.getAttribute("lat"),    str("50.54321"))
        self.assertEqual(element.getAttribute("lon"),   str("20.12345"))

        firstTag = element.firstChild
        self.assertIsNotNone(firstTag)
        self.assertEqual(firstTag.tagName, "tag") # type: ignore (checked above)
        self.assertEqual(firstTag.getAttribute("k"), "natural") # type: ignore (checked above)
        self.assertEqual(firstTag.getAttribute("v"), "tree") # type: ignore (checked above)

        element = node._to_xml(999, way_version=True)
        self.assertEqual(element.tagName, "nd")
        self.assertEqual(element.getAttribute("ref"), str(123))

        element = node._to_xml(999, member_version=True)
        self.assertEqual(element.tagName, "member")
        self.assertEqual(element.getAttribute("ref"), str(123))
        self.assertEqual(element.getAttribute("role"), "")

        element = node._to_xml(999, member_version=True, role="ABC")
        self.assertEqual(element.tagName, "member")
        self.assertEqual(element.getAttribute("ref"), str(123))
        self.assertEqual(element.getAttribute("role"), "ABC")

    def test_to_from_dict(self):
        node = sample_dataclasses.node("full_1")

        dict = node.to_dict()
        node_from_dict = Node.from_dict(dict)
        self.assertEqual(node, node_from_dict)
        self.assertEqual(node.tags, node_from_dict.tags)
        self.assertEqual(type(node_from_dict.tags), Tags)
        self.assertNotEqual(id(node), id(node_from_dict))

        def from_empty_dict():
            return Node.from_dict({})
        self.assertRaises(ValueError, from_empty_dict)

        def from_type_dict():
            return Node.from_dict({"type": "changeset"})
        self.assertRaises(ValueError, from_type_dict)