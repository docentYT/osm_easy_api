import unittest

from src import Node

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
        node = Node(123)
        node.tags.add("building", "yes")
        node.tags.add("building:levels", "3")
        self.assertEqual(node.tags, {"building": "yes", "building:levels": "3"})
        node.tags.add("roof:levels", "1")
        self.assertEqual(node.tags, {"building": "yes", "building:levels": "3", "roof:levels": "1"})
        node.tags.remove("building:levels")
        self.assertEqual(node.id, 123)
        self.assertEqual(node.tags, {"building": "yes", "roof:levels": "1"})