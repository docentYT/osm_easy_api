import unittest

from osm_easy_api.data_classes import User

class TestUser(unittest.TestCase):
    def test_basic_initalization(self):
        user = User(
            id=123,
            display_name="abc",
            account_created_at="11:22",
            description="desc",
            contributor_terms_agreed=True,
            img_url= "test.pl",
            roles=["moderator"],
            changesets_count=4,
            traces_count=1,
            blocks={
            "received": {
            "count": 3,
            "active": 0
            },
            "issued": {
            "count": 2,
            "active": 1
            }
            }
        )

        self.assertEqual(user.id, 123)
        self.assertEqual(user.display_name, "abc")
        self.assertEqual(user.account_created_at, "11:22")
        self.assertEqual(user.description, "desc")
        self.assertEqual(user.contributor_terms_agreed, True)
        self.assertEqual(user.img_url, "test.pl")
        self.assertEqual(user.roles, ["moderator"])
        self.assertEqual(user.changesets_count, 4)
        self.assertEqual(user.traces_count, 1)
        self.assertEqual(user.blocks, {
            "received": {
            "count": 3,
            "active": 0
            },
            "issued": {
            "count": 2,
            "active": 1
            }
            })
        
    def test_to_from_dict(self):
        user = User(
            id = 123,
            display_name="abc",
            account_created_at="221133",
            description="desc",
            contributor_terms_agreed=True,
            img_url="test.pl",
            roles = ["a", "b"],
            changesets_count=3,
            traces_count=4,
            blocks=None
        )

        dict = user.to_dict()
        user_from_dict = User.from_dict(dict)
        self.assertEqual(user, user_from_dict)
        self.assertNotEqual(id(user), id(user_from_dict))

        user_none = User(
            id = 123,
            display_name="abc",
            account_created_at="221133",
            description="desc",
            contributor_terms_agreed=None,
            img_url=None,
            roles = None,
            changesets_count=3,
            traces_count=4,
            blocks=None
        )

        dict = user_none.to_dict()
        user_from_dict = User.from_dict(dict)
        self.assertEqual(user_none, user_from_dict)
        self.assertNotEqual(id(user_none), id(user_from_dict))

        def from_empty_dict():
            return User.from_dict({})
        self.assertRaises(ValueError, from_empty_dict)

        def from_type_dict():
            return User.from_dict({"type": "changeset"})
        self.assertRaises(ValueError, from_type_dict)