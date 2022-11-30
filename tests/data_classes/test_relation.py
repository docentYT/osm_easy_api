import unittest

from src import Relation, Way, Node

class TestRelation(unittest.TestCase):
    def test_basic_initalization(self):
        relation = Relation(
            id=123,
            version=1, 
            changeset_id=321,
            timestamp="2022-11-11T21:15:26Z", 
            user_id=111
        )
        should_print = "Relation(id = 123, visible = None, version = 1, changeset_id = 321, timestamp = 2022-11-11T21:15:26Z, user_id = 111, tags = {}, members = [], )"
        self.assertEqual(str(relation), should_print)

    def test_tags(self):
        relation = Relation(123)
        relation.tags.add("building", "yes")
        relation.tags.add("building:levels", "3")
        self.assertEqual(relation.tags, {"building": "yes", "building:levels": "3"})
        relation.tags.add("roof:levels", "1")
        self.assertEqual(relation.tags, {"building": "yes", "building:levels": "3", "roof:levels": "1"})
        relation.tags.remove("building:levels")
        self.assertEqual(relation.id, 123)
        self.assertEqual(relation.tags, {"building": "yes", "roof:levels": "1"})

    def test_members(self):
        way_one = Way(123)
        way_two = Way(321)
        node_one = Node(1)
        node_two = Node(2)

        relation_one = Relation(1)
        relation_two = Relation(2)

        self.assertEqual(relation_one.members, [])
        self.assertEqual(relation_two.members, [])
        relation_one.members.append(node_one)
        self.assertEqual(relation_one.members, [node_one])
        self.assertEqual(relation_two.members, [])
        relation_one.members.append(node_two)
        self.assertEqual(relation_one.members, [node_one, node_two])
        self.assertEqual(relation_two.members, [])
        relation_two.members.append(node_one)
        self.assertEqual(relation_one.members, [node_one, node_two])
        self.assertEqual(relation_two.members, [node_one])
        relation_one.members.remove(node_one)
        self.assertEqual(relation_one.members, [node_two])
        self.assertEqual(relation_two.members, [node_one])


