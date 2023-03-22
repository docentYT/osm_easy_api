import unittest

from osm_easy_api.data_classes import Note, Comment, User

class TestComment(unittest.TestCase):
    def test_basic_initalization(self):
        user = User(id=123, display_name="abc")
        comment = Comment("123", user, action="opened", text="ABC", html="ABC")

        self.assertEqual(comment.comment_created_at, "123")
        self.assertEqual(comment.user, user)
        self.assertEqual(comment.action, "opened")
        self.assertEqual(comment.text, "ABC")
        self.assertEqual(comment.html, "ABC")

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

        comment = Comment("123", user, action="opened", text="ABC", html="ABC")

        dict = comment.to_dict()
        comment_from_dict = Comment.from_dict(dict)
        self.assertEqual(comment, comment_from_dict)
        self.assertNotEqual(id(comment), id(comment_from_dict))

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

        comment_none = Comment("123", user_none, action="opened", text="ABC", html="ABC")


        dict = comment_none.to_dict()
        comment_none_from_dict = Comment.from_dict(dict)
        self.assertEqual(comment_none, comment_none_from_dict)
        self.assertNotEqual(id(comment_none), id(comment_none_from_dict))

        def from_empty_dict():
            return User.from_dict({})
        self.assertRaises(ValueError, from_empty_dict)

        def from_type_dict():
            return User.from_dict({"type": "changeset"})
        self.assertRaises(ValueError, from_type_dict)
        
class TestNote(unittest.TestCase):
    def test_basic_initalization(self):
        user = User(id=123, display_name="abc")
        comment = Comment("123", user, action="opened", text="ABC", html="ABC")
        note = Note(123, "11.11", "22.22", "123", True, [comment])
        self.assertEqual(note.id, 123)
        self.assertEqual(note.latitude, "11.11")
        self.assertEqual(note.longitude, "22.22")
        self.assertEqual(note.note_created_at, "123")
        self.assertEqual(note.open, True)
        self.assertEqual(note.comments[0], comment)

    def test_comment__str__(self):
        user = User(id=123, display_name="abc")
        comment = Comment("123", user, action="opened", text="ABC", html="ABC")

        should_print = """Comment(comment_created_at = 123, user = User(id = 123, display_name = abc, account_created_at = None, description = None, contributor_terms_agreed = None, img_url = None, roles = None, changesets_count = None, traces_count = None, blocks = None, ), action = opened, text = ABC, html = ABC, )"""
        self.assertEqual(comment.__str__(), should_print)

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

        comment = Comment("123", user, action="opened", text="ABC", html="ABC")
        note = Note(123, "11.11", "22.22", "123", True, [comment])

        dict = note.to_dict()
        note_from_dict = Note.from_dict(dict)
        self.assertEqual(note, note_from_dict)
        self.assertNotEqual(id(note), id(note_from_dict))

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

        comment_user_none = Comment("123", user_none, action="opened", text="ABC", html="ABC")
        note_user_none = Note(123, "11.11", "22.22", "123", True, [comment_user_none])

        dict = note_user_none.to_dict()
        note_user_none_from_dict = Note.from_dict(dict)
        self.assertEqual(note_user_none, note_user_none_from_dict)
        self.assertNotEqual(id(note_user_none), id(note_user_none_from_dict))

        note_comment_none = Note(123, "11.11", "22.22", "123", True, [comment_user_none])

        dict = note_comment_none.to_dict()
        note_comment_none_from_dict = Note.from_dict(dict)
        self.assertEqual(note_comment_none, note_comment_none_from_dict)
        self.assertNotEqual(id(note_comment_none), id(note_comment_none_from_dict))

        def from_empty_dict():
            return User.from_dict({})
        self.assertRaises(ValueError, from_empty_dict)

        def from_type_dict():
            return User.from_dict({"type": "changeset"})
        self.assertRaises(ValueError, from_type_dict)