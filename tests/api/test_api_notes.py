import unittest
import responses

from ..fixtures.default_variables import TOKEN
from ..fixtures.stubs import note_stub

from osm_easy_api.api import Api
from osm_easy_api.data_classes import Note
from osm_easy_api.api import exceptions as ApiExceptions

def _are_notes_equal(first: Note, second: Note):
    return first.to_dict() == second.to_dict()

class TestApiNotes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.API = Api(url="https://test.pl", access_token=TOKEN)
        cls.BODY = note_stub.XML_RESPONSE_BODY

    @responses.activate
    def test_get(self):
        URL = "https://test.pl/api/0.6/notes/37970"
        def get():
            return self.API.notes.get(note_stub.OBJECT.id or False)
        
        responses.add(**{
            "method": responses.GET,
            "url": URL,
            "body": self.BODY,
            "status": 200
        })
        note = get()
        self.assertTrue(responses.assert_call_count(URL, 1))
        self.assertTrue(_are_notes_equal(note, note_stub.OBJECT))

        responses.add(**{
            "method": responses.GET,
            "url": URL,
            "body": self.BODY,
            "status": 404
        })
        self.assertRaises(ApiExceptions.IdNotFoundError, get)

        responses.add(**{
            "method": responses.GET,
            "url": URL,
            "body": self.BODY,
            "status": 410
        })
        self.assertRaises(ApiExceptions.ElementDeleted, get)

    @responses.activate
    def test_get_bbox(self):
        body = """<osm version="0.6" generator="OpenStreetMap server" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
<note lon="20.4660000" lat="52.2722000">
<id>37970</id>
<url>https://master.apis.dev.openstreetmap.org/api/0.6/notes/37970</url>
<comment_url>https://master.apis.dev.openstreetmap.org/api/0.6/notes/37970/comment</comment_url>
<close_url>https://master.apis.dev.openstreetmap.org/api/0.6/notes/37970/close</close_url>
<date_created>2023-02-26 13:37:26 UTC</date_created>
<status>open</status>
<comments>
<comment>
<date>2023-02-26 13:37:26 UTC</date>
<uid>18179</uid>
<user>kwiatek_123 bot</user>
<user_url>https://master.apis.dev.openstreetmap.org/user/kwiatek_123%20bot</user_url>
<action>opened</action>
<text>test</text>
<html><p>test</p></html>
</comment>
</comments>
</note>
<note lon="20.4685700" lat="52.2738101">
<id>13742</id>
<url>https://master.apis.dev.openstreetmap.org/api/0.6/notes/13742</url>
<comment_url>https://master.apis.dev.openstreetmap.org/api/0.6/notes/13742/comment</comment_url>
<close_url>https://master.apis.dev.openstreetmap.org/api/0.6/notes/13742/close</close_url>
<date_created>2018-11-14 15:56:53 UTC</date_created>
<status>open</status>
<comments>
<comment>
<date>2018-11-14 15:56:53 UTC</date>
<uid>7122</uid>
<user>keith</user>
<user_url>https://master.apis.dev.openstreetmap.org/user/keith</user_url>
<action>opened</action>
<text>#OSMyBiz Address: Spółdzielców 8, 05-085 Kampinos, Poland Category: sdf Name: sdfs Wheelchair accessible: Note: BUSINESS DONT EXST </text>
<html><p>#OSMyBiz <br /> <br />Address: Spółdzielców 8, 05-085 Kampinos, Poland <br />Category: sdf <br />Name: sdfs <br />Wheelchair accessible: <br />Note: BUSINESS DONT EXST </p></html>
</comment>
</comments>
</note>
</osm>"""
        URL = "https://test.pl/api/0.6/notes?bbox=20.4345,52.2620,20.5608,52.2946&limit=100&closed=7"
        responses.add(**{
            "method": responses.GET,
            "url": URL,
            "body": body,
            "status": 200
        })

        notes = self.API.notes.get_bbox("20.4345", "52.2620", "20.5608", "52.2946")
        self.assertTrue(responses.assert_call_count(URL, 1))
        self.assertEqual(notes[0].id, 37970)
        self.assertEqual(notes[1].id, 13742)
        self.assertEqual(notes[0].comments[0].text, "test")
        self.assertEqual(notes[1].comments[0].text, "#OSMyBiz Address: Spółdzielców 8, 05-085 Kampinos, Poland Category: sdf Name: sdfs Wheelchair accessible: Note: BUSINESS DONT EXST ")
        assert notes[0].comments[0].user, "User1 not exist"
        self.assertEqual(notes[0].comments[0].user.id, 18179)
        assert notes[1].comments[0].user, "User2 not exist"
        self.assertEqual(notes[1].comments[0].user.id, 7122)

        responses.add(**{
            "method": responses.GET,
            "url": URL,
            "body": body,
            "status": 400
        })

        def get_bbox():
            return self.API.notes.get_bbox("20.4345", "52.2620", "20.5608", "52.2946")
        
        self.assertRaises(ValueError, get_bbox)
        self.assertTrue(responses.assert_call_count(URL, 2))

    @responses.activate
    def test_create(self):
        URL = "https://test.pl/api/0.6/notes?lat=20.4345&lon=52.2620&text=test"
        responses.add(**{
            "method": responses.POST,
            "url": URL,
            "body": self.BODY,
            "status": 200
        })
        note = self.API.notes.create("20.4345", "52.2620", "test")
        self.assertTrue(responses.assert_call_count(URL, 1))
        self.assertTrue(_are_notes_equal(note, note_stub.OBJECT))

    @responses.activate
    def test_comment(self):
        URL = "https://test.pl/api/0.6/notes/37970/comment?text=test"

        def comment():
            return self.API.notes.comment(37970, "test")
        
        responses.add(**{
            "method": responses.POST,
            "url": URL,
            "body": self.BODY,
            "status": 200
        })
        note = comment()
        self.assertTrue(responses.assert_call_count(URL, 1))
        self.assertTrue(_are_notes_equal(note, note_stub.OBJECT))

        responses.add(**{
            "method": responses.POST,
            "url": URL,
            "body": self.BODY,
            "status": 404
        })
        self.assertRaises(ApiExceptions.IdNotFoundError, comment)

        responses.add(**{
            "method": responses.POST,
            "url": URL,
            "body": self.BODY,
            "status": 409
        })
        self.assertRaises(ApiExceptions.NoteAlreadyClosed, comment)

        responses.add(**{
            "method": responses.POST,
            "url": URL,
            "body": self.BODY,
            "status": 410
        })
        self.assertRaises(ApiExceptions.ElementDeleted, comment)

    @responses.activate
    def test_close(self):
        URL = "https://test.pl/api/0.6/notes/37970/close?text=test"

        def close():
            return self.API.notes.close(37970, "test")
        
        responses.add(**{
            "method": responses.POST,
            "url": URL,
            "body": self.BODY,
            "status": 200
        })
        note = close()
        self.assertTrue(responses.assert_call_count(URL, 1))
        self.assertTrue(_are_notes_equal(note, note_stub.OBJECT))

        responses.add(**{
            "method": responses.POST,
            "url": URL,
            "body": self.BODY,
            "status": 409
        })
        self.assertRaises(ApiExceptions.NoteAlreadyClosed, close)

    @responses.activate
    def test_open(self):
        URL = "https://test.pl/api/0.6/notes/37970/reopen?text=test"

        def reopen():
            return self.API.notes.reopen(37970, "test")
        
        responses.add(**{
            "method": responses.POST,
            "url": URL,
            "body": self.BODY,
            "status": 200
        })
        note = reopen()
        self.assertTrue(responses.assert_call_count(URL, 1))
        self.assertTrue(_are_notes_equal(note, note_stub.OBJECT))

        responses.add(**{
            "method": responses.POST,
            "url": URL,
            "body": self.BODY,
            "status": 409
        })
        self.assertRaises(ApiExceptions.NoteAlreadyOpen, reopen)

    @responses.activate
    def test_hide(self):
        URL = "https://test.pl/api/0.6/notes/37970"
        responses.add(**{
            "method": responses.DELETE,
            "url": URL,
            "status": 200
        })
        self.API.notes.hide(37970)
        self.assertTrue(responses.assert_call_count(URL, 1))

    @responses.activate
    def test_search(self):
        URL_1 = "https://test.pl/api/0.6/notes/search?q=test&limit=100&closed=7&sort=updated_at&order=newest"
        responses.add(**{
            "method": responses.GET,
            "url": URL_1,
            "body": self.BODY,
            "status": 200
        })
        notes = self.API.notes.search(text = "test")
        self.assertTrue(responses.assert_call_count(URL_1, 1))
        self.assertTrue(_are_notes_equal(notes[0], note_stub.OBJECT))

        URL_2 = "https://test.pl/api/0.6/notes/search?q=test&limit=9999999&closed=7&sort=updated_at&order=newest"
        responses.add(**{
            "method": responses.GET,
            "url": URL_2,
            "body": self.BODY,
            "status": 400
        })
        def search():
            return self.API.notes.search(text = "test", limit=9999999)
        self.assertRaises(ApiExceptions.LimitsExceeded, search)
        self.assertTrue(responses.assert_call_count(URL_2, 1))

        EMPTY_BODY = """<osm version="0.6" generator="OpenStreetMap server" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
        </osm>"""
        responses.add(**{
            "method": responses.GET,
            "url": URL_2,
            "body": EMPTY_BODY,
            "status": 200
        })
        notes = search()
        self.assertTrue(responses.assert_call_count(URL_2, 2))
        self.assertEqual(notes, [])
