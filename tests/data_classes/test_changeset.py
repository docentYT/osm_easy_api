import unittest

from osm_easy_api.data_classes import Changeset, Tags

class TestNote(unittest.TestCase):
    def test_basic_initalization(self):
        changeset = Changeset(1, "-1", False, "-1", "-1", "-1", Tags(), None)
        self.assertEqual(changeset.id, 1)
        self.assertEqual(changeset.timestamp, "-1")

    def test__str__(self):
        should_print = """Changeset(id = 1, timestamp = -1, open = False, user_id = -1, comments_count = -1, changes_count = -1, tags = {}, discussion = None, )""" 
        changeset = Changeset(1, "-1", False, "-1", "-1", "-1", Tags(), None)
        self.assertEqual(changeset.__str__(), should_print)

    def test_to_from_dict(self):
        changeset = Changeset(1, "-1", False, "-1", "-1", "-1", Tags(), None)
        changeset_dict = changeset.to_dict()
        changeset_from_dict = Changeset.from_dict(changeset_dict)

        self.assertEqual(changeset.id, changeset_from_dict.id)
        self.assertEqual(changeset, changeset_from_dict)

        def from_empty_dict():
            return Changeset.from_dict({})
        self.assertRaises(ValueError, from_empty_dict)

        def from_type_dict():
            return Changeset.from_dict({"type": "way"})
        self.assertRaises(ValueError, from_type_dict)