import unittest

from src import Way, Node

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


