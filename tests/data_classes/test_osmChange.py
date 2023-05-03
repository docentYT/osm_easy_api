import unittest

from osm_easy_api import Node, Way, OsmChange, Action, Tags, Relation
from ..fixtures import sample_dataclasses

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
        osmChange.add(sample_dataclasses.node("simple_1"))
        should_print = "OsmChange(version=0.1, generator=unittest, sequence_number=123. Node: Create(0), Modify(0), Delete(0), None(1). Way: Create(0), Modify(0), Delete(0), None(0). Relation: Create(0), Modify(0), Delete(0), None(0)."
        self.assertEqual(str(osmChange), should_print)
        osmChange.add(sample_dataclasses.node("simple_2"), Action.MODIFY)
        osmChange.add(sample_dataclasses.way("simple_1"), Action.MODIFY)
        should_print = "OsmChange(version=0.1, generator=unittest, sequence_number=123. Node: Create(0), Modify(1), Delete(0), None(1). Way: Create(0), Modify(1), Delete(0), None(0). Relation: Create(0), Modify(0), Delete(0), None(0)."
        self.assertEqual(str(osmChange), should_print)

    def test_get(self):
        osmChange = OsmChange("0.1", "unittest", "123")
        osmChange.add(sample_dataclasses.node("simple_1"))
        osmChange.add(sample_dataclasses.node("simple_2"), Action.MODIFY)
        osmChange.add(sample_dataclasses.way("simple_1"), Action.MODIFY)
        self.assertEqual(osmChange.get(Node), [sample_dataclasses.node("simple_1")])
        self.assertEqual(osmChange.get(Node, Action.MODIFY), [sample_dataclasses.node("simple_2")])
        self.assertEqual(osmChange.get(Node, Action.DELETE), [])
        self.assertEqual(osmChange.get(Way), [])
        self.assertEqual(osmChange.get(Way, Action.MODIFY), [sample_dataclasses.way("simple_1")])
        self.assertEqual(osmChange.get(Way, Action.DELETE), [])
        

    def test_remove(self):
        osmChange = OsmChange("0.1", "unittest", "123")
        node_one = sample_dataclasses.node("simple_1")
        node_two = sample_dataclasses.node("simple_2")
        way_one = sample_dataclasses.way("simple_1")
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

    def test__to_xml(self):
        # TODO: Check if xml is well made
        osmChange = OsmChange("0.1", "unittest", "123")
        osmChange.add(sample_dataclasses.node("simple_1"))
        osmChange.add(sample_dataclasses.node("full_1"), Action.CREATE)
        osmChange.add(sample_dataclasses.way("full_with_nodes"), Action.MODIFY)
        osmChange.add(sample_dataclasses.relation("simple_1"), Action.MODIFY)
        self.maxDiff = None
        osmChange._to_xml(999)