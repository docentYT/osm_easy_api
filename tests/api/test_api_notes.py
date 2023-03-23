import unittest
import responses

from ..fixtures.default_variables import LOGIN, PASSWORD

from osm_easy_api import Api
from osm_easy_api.api import exceptions as ApiExceptions

class TestApiNotes(unittest.TestCase):

    @responses.activate
    def test_get(self):
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
</osm>"""
        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/api/0.6/notes/37970",
            "body": body,
            "status": 200
        })

        api = Api("https://test.pl", LOGIN, PASSWORD)
        note = api.notes.get(37970)
        self.assertEqual(note.id, 37970)
        self.assertEqual(note.longitude, "20.4660000")
        self.assertEqual(note.comments[0].text, "test")
        assert note.comments[0].user, "User not exist"
        self.assertEqual(note.comments[0].user.id, 18179)

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
        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/api/0.6/notes?bbox=20.4345,52.2620,20.5608,52.2946?limit=100?closed=7",
            "body": body,
            "status": 200
        })

        api = Api("https://test.pl", LOGIN, PASSWORD)
        notes = api.notes.get_bbox("20.4345", "52.2620", "20.5608", "52.2946")
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
            "url": "https://test.pl/api/0.6/notes?bbox=20.4345,52.2620,20.5608,52.2946?limit=100?closed=7",
            "body": body,
            "status": 400
        })

        def get_bbox():
            return api.notes.get_bbox("20.4345", "52.2620", "20.5608", "52.2946")
        
        self.assertRaises(ValueError, get_bbox)

    @responses.activate
    def test_create(self):
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
</osm>"""
        responses.add(**{
            "method": responses.POST,
            "url": "https://test.pl/api/0.6/notes?lat=20.4345&lon=52.2620&text=abc",
            "body": body,
            "status": 200
        })

        api = Api("https://test.pl", LOGIN, PASSWORD)
        note = api.notes.create("20.4345", "52.2620", "abc")
        self.assertEqual(note.id, 37970)

    @responses.activate
    def test_create(self):
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
</osm>"""
        responses.add(**{
            "method": responses.POST,
            "url": "https://test.pl/api/0.6/notes/37970/comment?text=abc",
            "body": body,
            "status": 200
        })

        api = Api("https://test.pl", LOGIN, PASSWORD)
        note = api.notes.comment(37970, "abc")
        self.assertEqual(note.id, 37970)

        responses.add(**{
            "method": responses.POST,
            "url": "https://test.pl/api/0.6/notes/37970/comment?text=abc",
            "body": body,
            "status": 404
        })

        def comment():
            return api.notes.comment(37970, "abc")
        
        self.assertRaises(ApiExceptions.IdNotFoundError, comment)

        responses.add(**{
            "method": responses.POST,
            "url": "https://test.pl/api/0.6/notes/37970/comment?text=abc",
            "body": body,
            "status": 409
        })
        self.assertRaises(ApiExceptions.NoteAlreadyClosed, comment)