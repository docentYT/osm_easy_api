import unittest

from osm_easy_api import Way, Tags
from ..fixtures import sample_dataclasses

class TestWay(unittest.TestCase):
    def test_basic_initalization(self):
        way = Way(
            id=123,
            version=1, 
            changeset_id=321,
            timestamp="2022-11-11T21:15:26Z", 
            user_id=111
        )
        should_print = "Way(id = 123, visible = None, version = 1, changeset_id = 321, timestamp = 2022-11-11T21:15:26Z, user_id = 111, tags = {}, nodes = [], )"
        self.assertEqual(str(way), should_print)

    def test_tags(self):
        way = sample_dataclasses.way("simple_1")
        way.tags.add("building", "yes")
        way.tags.add("building:levels", "3")
        self.assertEqual(way.tags, {"building": "yes", "building:levels": "3"})
        way.tags.add("roof:levels", "1")
        self.assertEqual(way.tags, {"building": "yes", "building:levels": "3", "roof:levels": "1"})
        way.tags.remove("building:levels")
        self.assertEqual(way.id, 123)
        self.assertEqual(way.tags, {"building": "yes", "roof:levels": "1"})

    def test_nodes(self):
        way_one = sample_dataclasses.way("simple_1")
        way_two = sample_dataclasses.way("simple_2")
        node_one = sample_dataclasses.node("simple_1")
        node_two = sample_dataclasses.node("simple_2")

        self.assertEqual(way_one.nodes, [])
        self.assertEqual(way_two.nodes, [])
        way_one.nodes.append(node_one)
        self.assertEqual(way_one.nodes, [node_one])
        self.assertEqual(way_two.nodes, [])
        way_one.nodes.append(node_two)
        self.assertEqual(way_one.nodes, [node_one, node_two])
        self.assertEqual(way_two.nodes, [])
        way_two.nodes.append(node_one)
        self.assertEqual(way_one.nodes, [node_one, node_two])
        self.assertEqual(way_two.nodes, [node_one])
        way_one.nodes.remove(node_one)
        self.assertEqual(way_one.nodes, [node_two])
        self.assertEqual(way_two.nodes, [node_one])

    def test__to_xml(self):
        way = sample_dataclasses.way("full_with_nodes")

        element = way._to_xml(999)
        self.assertEqual(element.tagName, "way")
        self.assertEqual(element.getAttribute("id"),          str(123))
        self.assertEqual(element.getAttribute("version"),     str(1))
        self.assertEqual(element.getAttribute("changeset"),   str(999))

        self.assertEqual(element.childNodes[0].tagName, "nd")
        self.assertEqual(element.childNodes[0].getAttribute("ref"), str(123))

        self.assertEqual(element.childNodes[1].tagName, "nd")
        self.assertEqual(element.childNodes[1].getAttribute("ref"), str(12345))
        
        self.assertEqual(element.childNodes[2].tagName, "tag")
        self.assertEqual(element.childNodes[2].getAttribute("k"), "ABC")
        self.assertEqual(element.childNodes[2].getAttribute("v"), "CBA")

        element = way._to_xml(999, member_version=True)
        self.assertEqual(element.tagName, "member")
        self.assertEqual(element.getAttribute("ref"), str(123))
        self.assertEqual(element.getAttribute("role"), "")

        element = way._to_xml(999, member_version=True, role="ABC")
        self.assertEqual(element.tagName, "member")
        self.assertEqual(element.getAttribute("ref"), str(123))
        self.assertEqual(element.getAttribute("role"), "ABC")

    def test_to_from_dict(self):
        way1 = sample_dataclasses.way("full_with_nodes")
        way2 = sample_dataclasses.way("full_with_nodes")
        way2.nodes.pop()

        dict1 = way1.to_dict()
        dict2 = way2.to_dict()
        way1_from_dict = Way.from_dict(dict1)
        way2_from_dict = Way.from_dict(dict2)
        self.assertEqual(way1, way1_from_dict)
        self.assertEqual(way2, way2_from_dict)
        self.assertEqual(way1.tags, way1_from_dict.tags)
        self.assertEqual(way2.tags, way2_from_dict.tags)
        self.assertEqual(type(way1_from_dict.tags), Tags)
        self.assertEqual(type(way2_from_dict.tags), Tags)
        self.assertNotEqual(id(way1), id(way1_from_dict))
        self.assertNotEqual(id(way2), id(way2_from_dict))
        self.assertNotEqual(id(way1_from_dict), id(way2_from_dict))

        def from_empty_dict():
            return Way.from_dict({})
        self.assertRaises(ValueError, from_empty_dict)

        def from_type_dict():
            return Way.from_dict({"type": "changeset"})
        self.assertRaises(ValueError, from_type_dict)