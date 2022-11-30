import unittest

from src import Node, Way, OsmChange, Action

class TestOsmChange(unittest.TestCase):
    def test_basic_initalization(self):
        osmChange = OsmChange("0.1", "unittest", "123")
        self.assertEqual(osmChange.meta.version, "0.1")
        self.assertEqual(osmChange.meta.generator, "unittest")
        self.assertEqual(osmChange.meta.sequence_number, "123")
        should_print = "OsmChange(version=0.1, generator=unittest, sequence_number=123. Node: Create(0), Modify(0), Delete(0), None(0). Way: Create(0), Modify(0), Delete(0), None(0). Relation: Create(0), Modify(0), Delete(0), None(0)."
        self.assertEqual(str(osmChange), should_print)

    def test_add(self):
        osmChange = OsmChange("0.1", "unittest", "123")
        osmChange.add(Node(id=123))
        should_print = "OsmChange(version=0.1, generator=unittest, sequence_number=123. Node: Create(0), Modify(0), Delete(0), None(1). Way: Create(0), Modify(0), Delete(0), None(0). Relation: Create(0), Modify(0), Delete(0), None(0)."
        self.assertEqual(str(osmChange), should_print)
        osmChange.add(Node(id=321), Action.MODIFY)
        osmChange.add(Way(id=234), Action.MODIFY)
        should_print = "OsmChange(version=0.1, generator=unittest, sequence_number=123. Node: Create(0), Modify(1), Delete(0), None(1). Way: Create(0), Modify(1), Delete(0), None(0). Relation: Create(0), Modify(0), Delete(0), None(0)."
        self.assertEqual(str(osmChange), should_print)

    def test_get(self):
        osmChange = OsmChange("0.1", "unittest", "123")
        osmChange.add(Node(id=123))
        osmChange.add(Node(id=321), Action.MODIFY)
        osmChange.add(Way(id=234), Action.MODIFY)
        self.assertEqual(osmChange.get(Node), [Node(id=123)])
        self.assertEqual(osmChange.get(Node, Action.MODIFY), [Node(id=321)])
        self.assertEqual(osmChange.get(Node, Action.DELETE), [])
        self.assertEqual(osmChange.get(Way), [])
        self.assertEqual(osmChange.get(Way, Action.MODIFY), [Way(id=234)])
        self.assertEqual(osmChange.get(Way, Action.DELETE), [])
        

    def test_remove(self):
        osmChange = OsmChange("0.1", "unittest", "123")
        node_one = Node(id=123)
        node_two = Node(id=321)
        way_one = Way(id=234)
        osmChange.add(node_one)
        osmChange.add(node_two, Action.MODIFY)
        self.assertEqual(osmChange.get(Node), [node_one])
        osmChange.remove(node_one)
        self.assertEqual(osmChange.get(Node), [])

        self.assertEqual(osmChange.get(Node, Action.MODIFY), [node_two])
        osmChange.remove(node_two, Action.MODIFY)
        self.assertEqual(osmChange.get(Node, Action.MODIFY), [])

        osmChange.add(way_one)
        self.assertEqual(osmChange.get(Way), [way_one])
        osmChange.remove(way_one)
        self.assertEqual(osmChange.get(Way), [])