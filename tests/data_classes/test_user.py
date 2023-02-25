import unittest

from src.data_classes import User

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