import unittest

from osm_easy_api.data_classes import Relation, Way, Node, Tags
from osm_easy_api.data_classes.relation import Member as RelationMember
from ..fixtures import sample_dataclasses

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
        relation = sample_dataclasses.relation("simple_1")
        relation.tags.add("building", "yes")
        relation.tags.add("building:levels", "3")
        self.assertEqual(relation.tags, {"building": "yes", "building:levels": "3"})
        relation.tags.add("roof:levels", "1")
        self.assertEqual(relation.tags, {"building": "yes", "building:levels": "3", "roof:levels": "1"})
        relation.tags.remove("building:levels")
        self.assertEqual(relation.id, 123)
        self.assertEqual(relation.tags, {"building": "yes", "roof:levels": "1"})

    def test_members(self):
        node_one = sample_dataclasses.node("simple_1")
        node_two = sample_dataclasses.node("simple_2")

        relation_one = Relation(1)
        relation_two = Relation(2)

        self.assertEqual(relation_one.members, [])
        self.assertEqual(relation_two.members, [])
        relation_one.members.append(RelationMember(node_one, "MemberOne"))
        self.assertEqual(relation_one.members, [RelationMember(node_one, "MemberOne")])
        self.assertEqual(relation_two.members, [])
        relation_one.members.append(RelationMember(node_two, "MemberTwo"))
        self.assertEqual(relation_one.members, [RelationMember(node_one, "MemberOne"), RelationMember(node_two, "MemberTwo")])
        self.assertEqual(relation_two.members, [])
        relation_two.members.append(RelationMember(node_one, "MemberOne"))
        self.assertEqual(relation_one.members, [RelationMember(node_one, "MemberOne"), RelationMember(node_two, "MemberTwo")])
        self.assertEqual(relation_two.members, [RelationMember(node_one, "MemberOne")])
        relation_one.members.remove(RelationMember(node_one, "MemberOne"))
        self.assertEqual(relation_one.members, [RelationMember(node_two, "MemberTwo")])
        self.assertEqual(relation_two.members, [RelationMember(node_one, "MemberOne")])

    def test__to_xml(self):
        relation = sample_dataclasses.relation("full_with_members")

        element = relation._to_xml(999, member_version=True)
        self.assertEqual(element.tagName, "member")
        self.assertEqual(element.getAttribute("type"), "relation")
        self.assertEqual(element.getAttribute("ref"), str(123))
        self.assertEqual(element.getAttribute("role"), "")

        element = relation._to_xml(999, member_version=True, role="ABC")
        self.assertEqual(element.tagName, "member")
        self.assertEqual(element.getAttribute("type"), "relation")
        self.assertEqual(element.getAttribute("ref"), str(123))
        self.assertEqual(element.getAttribute("role"), "ABC")

        element = relation._to_xml(999)
        self.assertEqual(element.tagName, "relation")
        self.assertEqual(element.getAttribute("id"), str(123))
        self.assertEqual(element.getAttribute("version"), str(1))
        self.assertEqual(element.getAttribute("changeset"), str(999))
        
        tag = element.childNodes[0]
        self.assertIsNotNone(tag)
        self.assertEqual(tag.tagName, "tag") # type: ignore (checked above)
        self.assertEqual(tag.getAttribute("k"), "type") # type: ignore (checked above)
        self.assertEqual(tag.getAttribute("v"), "multipolygon") # type: ignore (checked above)

        node_1 = element.childNodes[1]
        self.assertEqual(node_1.tagName, "member")
        self.assertEqual(node_1.getAttribute("type"), "node")
        self.assertEqual(node_1.getAttribute("role"), "role_1")
        self.assertIsNone(node_1.firstChild)

        node_2 = element.childNodes[2]
        self.assertEqual(node_2.tagName, "member")
        self.assertEqual(node_2.getAttribute("type"), "node")
        self.assertEqual(node_2.getAttribute("role"), "role_2")
        self.assertIsNone(node_2.firstChild)

        way = element.childNodes[3]
        self.assertEqual(way.tagName, "member")
        self.assertEqual(way.getAttribute("type"), "way")
        self.assertEqual(way.getAttribute("role"), "role_3")
        self.assertIsNone(way.firstChild)

    def test_to_from_dict(self):
        relation = sample_dataclasses.relation("full_with_members")
        relation2 = sample_dataclasses.relation("full_with_members")
        relation2.members.pop()

        dict = relation.to_dict()
        dict2 = relation2.to_dict()
        relation_from_dict = Relation.from_dict(dict)
        relation2_from_dict = Relation.from_dict(dict2)
        self.assertEqual(relation, relation_from_dict)
        self.assertEqual(relation2, relation2_from_dict)
        self.assertEqual(type(relation_from_dict.tags), Tags)
        self.assertEqual(type(relation2_from_dict.tags), Tags)
        self.assertNotEqual(id(relation), id(relation_from_dict))
        self.assertNotEqual(id(relation2), id(relation2_from_dict))
        self.assertNotEqual(id(relation_from_dict), id(relation2_from_dict))

        def from_empty_dict():
            return Relation.from_dict({})
        self.assertRaises(ValueError, from_empty_dict)

        def from_type_dict():
            return Relation.from_dict({"type": "changeset"})
        self.assertRaises(ValueError, from_type_dict)