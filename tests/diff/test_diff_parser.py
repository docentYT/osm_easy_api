import unittest
import gzip
import os

from osm_easy_api.diff.diff_parser import OsmChange_parser
from osm_easy_api import Node, Way, Relation, Action, Tags
from osm_easy_api.data_classes.relation import Member

class TestDiffParser(unittest.TestCase):
    def test_OsmChange_parser_basic(self):
        file_path = os.path.join("tests", "fixtures", "hour.xml.gz")
        file = gzip.open(file_path, "r")

        osmChange = OsmChange_parser(file, "-1")
        # print(osmChange)
        self.assertEqual(len(osmChange.get(Node, Action.CREATE  )), 2   )
        self.assertEqual(len(osmChange.get(Node, Action.MODIFY  )), 14  )
        self.assertEqual(len(osmChange.get(Node, Action.DELETE  )), 1   )
        self.assertEqual(len(osmChange.get(Node, Action.NONE    )), 0   )
        
        self.assertEqual(len(osmChange.get(Way, Action.CREATE  )), 0   )
        self.assertEqual(len(osmChange.get(Way, Action.MODIFY  )), 1   )
        self.assertEqual(len(osmChange.get(Way, Action.DELETE  )), 0   )
        self.assertEqual(len(osmChange.get(Way, Action.NONE    )), 0   )

        self.assertEqual(len(osmChange.get(Relation, Action.CREATE  )), 1   )
        self.assertEqual(len(osmChange.get(Relation, Action.MODIFY  )), 0   )
        self.assertEqual(len(osmChange.get(Relation, Action.DELETE  )), 0   )
        self.assertEqual(len(osmChange.get(Relation, Action.NONE    )), 0   )

        file.close()

    def test_OsmChange_parser_node(self):
        file_path = os.path.join("tests", "fixtures", "hour.xml.gz")
        file = gzip.open(file_path, "r")

        osmChange = OsmChange_parser(file, "-1")
        should_be = Node(id=10288507, version=8, timestamp="2022-11-12T12:08:55Z", user_id=24119, changeset_id=128810121, latitude="55.7573298", longitude="-3.8807238", tags=Tags({"railway": "switch"}))
        self.assertEqual(osmChange.get(Node, Action.MODIFY)[1], should_be)

        file.close() 

    def test_OsmChange_parser_way(self):
        file_path = os.path.join("tests", "fixtures", "hour.xml.gz")
        file = gzip.open(file_path, "r")

        osmChange = OsmChange_parser(file, "-1")
        should_be = Way(id=1112379431, version=1, timestamp="2022-11-11T21:15:26Z", user_id=10420541, changeset_id=128793616, nodes=[Node(10176911691), Node(10176911692), Node(10176911693)])
        self.assertEqual(osmChange.get(Way, Action.MODIFY)[0], should_be)

        file.close()

    def test_OsmChange_parser_relation(self):
        file_path = os.path.join("tests", "fixtures", "hour.xml.gz")
        file = gzip.open(file_path, "r")

        osmChange = OsmChange_parser(file, "-1")
        should_be = Relation(id=13013122, version=2, timestamp="2022-11-11T21:15:50Z", user_id=17287177, changeset_id=128793623, tags=Tags({"type": "route", "route": "bus"}), members=[Member(Node(34819782), "stop"), Member(Way(88452897), ""), Member(Way(536004622), "")])
        self.assertEqual(osmChange.get(Relation, Action.CREATE)[0], should_be)
        self.assertEqual(osmChange.get(Relation, Action.CREATE)[0].members[0].role, "stop")

        file.close()

    def test_OsmChange_parser_tags(self):
        file_path = os.path.join("tests", "fixtures", "hour.xml.gz")
        file = gzip.open(file_path, "r")

        osmChange = OsmChange_parser(file, "-1", Tags({"highway": "crossing"}))
        # print(osmChange)
        self.assertEqual(len(osmChange.get(Node, Action.CREATE  )), 2   )
        self.assertEqual(len(osmChange.get(Node, Action.MODIFY  )), 2   )
        self.assertEqual(len(osmChange.get(Node, Action.DELETE  )), 0   )
        self.assertEqual(len(osmChange.get(Node, Action.NONE    )), 0   )

        osmChange = OsmChange_parser(file, "-1", Tags({"highway": "crossing", "ahfuiowegwe": "afhuiweew"}))
        # print(osmChange)
        self.assertEqual(len(osmChange.get(Node, Action.CREATE  )), 0   )
        self.assertEqual(len(osmChange.get(Node, Action.MODIFY  )), 0   )
        self.assertEqual(len(osmChange.get(Node, Action.DELETE  )), 0   )
        self.assertEqual(len(osmChange.get(Node, Action.NONE    )), 0   )

        file.close()

    def test_OsmChange_parser_str_tag(self):
        file_path = os.path.join("tests", "fixtures", "hour.xml.gz")
        file = gzip.open(file_path, "r")

        osmChange = OsmChange_parser(file, "-1", "crossing")
        # print(osmChange)
        self.assertEqual(len(osmChange.get(Node, Action.CREATE  )), 1   )
        self.assertEqual(len(osmChange.get(Node, Action.MODIFY  )), 2   )
        self.assertEqual(len(osmChange.get(Node, Action.DELETE  )), 0   )
        self.assertEqual(len(osmChange.get(Node, Action.NONE    )), 0   )

        file.close()