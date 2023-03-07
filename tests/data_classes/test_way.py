import unittest

from osm_easy_api import Way, Node, Tags

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
        way = Way(123)
        way.tags.add("building", "yes")
        way.tags.add("building:levels", "3")
        self.assertEqual(way.tags, {"building": "yes", "building:levels": "3"})
        way.tags.add("roof:levels", "1")
        self.assertEqual(way.tags, {"building": "yes", "building:levels": "3", "roof:levels": "1"})
        way.tags.remove("building:levels")
        self.assertEqual(way.id, 123)
        self.assertEqual(way.tags, {"building": "yes", "roof:levels": "1"})

    def test_nodes(self):
        way_one = Way(123)
        way_two = Way(321)
        node_one = Node(1)
        node_two = Node(2)

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
        way = Way(
            id=123,
            version=1, 
            changeset_id=321,
            timestamp="2022-11-11T21:15:26Z", 
            user_id=111,
            tags=Tags({"ABC": "CBA"})
        )
        node_one = Node(1)
        node_two = Node(2)

        way.nodes.append(node_one)
        way.nodes.append(node_two)

        element = way._to_xml(999)
        self.assertEqual(element.tagName, "way")
        self.assertEqual(element.getAttribute("id"),          str(123))
        self.assertEqual(element.getAttribute("version"),     str(1))
        self.assertEqual(element.getAttribute("changeset"),   str(999))

        self.assertEqual(element.childNodes[0].tagName, "nd")
        self.assertEqual(element.childNodes[0].getAttribute("ref"), str(1))

        self.assertEqual(element.childNodes[1].tagName, "nd")
        self.assertEqual(element.childNodes[1].getAttribute("ref"), str(2))
        
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
        way = Way(
            id=123,
            version=1, 
            changeset_id=321,
            timestamp="2022-11-11T21:15:26Z", 
            user_id=111,
            tags=Tags({"ABC": "CBA"})
        )
        node_one = Node(1)
        node_two = Node(2)

        way.nodes.append(node_one)
        way.nodes.append(node_two)

        dict = way.to_dict()
        way_from_dict = Way.from_dict(dict)
        self.assertEqual(way, way_from_dict)
        self.assertEqual(way.tags, way_from_dict.tags)
        self.assertEqual(type(way_from_dict.tags), Tags)
        self.assertNotEqual(id(way), id(way_from_dict))
        
        def node_from_dict():
            return Node.from_dict(dict)
        self.assertRaises(ValueError, node_from_dict)