import unittest

from src.data_classes import Note, Comment, User

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
        self.assertEqual(note.comments[0].comment_created_at, "123")
        assert note.comments[0].user, "No user exist"
        self.assertEqual(note.comments[0].user.id, 123)