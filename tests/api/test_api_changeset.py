import unittest
import responses
from copy import copy

from ..fixtures.default_variables import TOKEN

from osm_easy_api.api import Api
from osm_easy_api.data_classes import Changeset, Tags, Node, OsmChange, Action
from osm_easy_api.api import exceptions as ApiExceptions
from ..fixtures import sample_dataclasses 
from ..fixtures.stubs import changeset_stub 

def _are_changesets_equal(first: Changeset, second: Changeset):
    return first.to_dict() == second.to_dict()

class TestApiChangeset(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.API = Api(url="https://test.pl", access_token=TOKEN)

    @responses.activate
    def test_create(self):
        responses.add(**{
            "method": responses.PUT,
            "url": "https://test.pl/api/0.6/changeset/create",
            "body": "111",
            "status": 200
        })

        self.assertEqual(self.API.changeset.create("ABC"), 111)
        self.assertEqual(self.API.changeset.create("ABC", tags=Tags({"alfa": "beta"})), 111)

    @responses.activate
    def test_get(self):
        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/api/0.6/changeset/111?include_discussion=true",
            "body": changeset_stub.XML_RESPONSE_BODY,
            "status": 200
        })

        testing_changeset = self.API.changeset.get(111, True)
        self.assertTrue(_are_changesets_equal(testing_changeset, changeset_stub.OBJECT))

        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/api/0.6/changeset/111?include_discussion=true",
            "status": 404
        })

        def get():
            return self.API.changeset.get(111, True)
        
        self.assertRaises(ApiExceptions.IdNotFoundError, get)

    @responses.activate
    def test_get_query(self):
        body = """<osm version="0.6" generator="OpenStreetMap server" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
    <changeset id="111" created_at="2023-01-10T16:49:30Z" open="false" comments_count="0" changes_count="3" closed_at="2023-01-10T16:52:52Z" min_lat="52.2423700" min_lon="21.1171000" max_lat="52.2423700" max_lon="21.1171000" uid="18179" user="kwiatek_123 bot">
        <tag k="comment" v="Upload relation test"/>
    </changeset>
    <changeset id="222" created_at="2023-01-10T16:48:58Z" open="false" comments_count="0" changes_count="0" closed_at="2023-01-10T17:48:58Z" uid="18179" user="kwiatek_123 bot">
        <tag k="comment" v="Upload relation test"/>
    </changeset>
</osm>
        """
        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/api/0.6/changesets/?user=18179&changesets=111,222&order=newest&limit=100",
            "body": body,
            "status": 200
        })

        changeset = Changeset(
            222,
            "2023-01-10T16:48:58Z",
            False,
            "18179",
            "0",
            "0",
            Tags({"comment": "Upload relation test"})
        )

        testing_changeset = self.API.changeset.get_query(user_id=18179, changesets_id=[111, 222])[1]
        self.assertTrue(_are_changesets_equal(testing_changeset, changeset))

        body = changeset_stub.XML_RESPONSE_BODY

        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/api/0.6/changesets/?user=18179&order=newest&limit=1",
            "body": body,
            "status": 200
        })
        changeset_list = self.API.changeset.get_query(user_id=18179, limit=1)
        self.assertEqual(changeset_list.__len__(), 1)

    @responses.activate
    def test_update(self):
        responses.add(**{
            "method": responses.PUT,
            "url": "https://test.pl/api/0.6/changeset/111",
            "body": changeset_stub.XML_RESPONSE_BODY,
            "status": 200
        })

        testing_changeset = self.API.changeset.update(111, "BBB")
        self.assertTrue(_are_changesets_equal(testing_changeset, changeset_stub.OBJECT))

        testing_changeset = self.API.changeset.update(111, "BBB" , Tags({"testing": "yes"}))
        self.assertTrue(_are_changesets_equal(testing_changeset, changeset_stub.OBJECT))

        def update():
            return self.API.changeset.update(111, "BBB")
        responses.add(**{
            "method": responses.PUT,
            "url": "https://test.pl/api/0.6/changeset/111",
            "status": 404
        })
        self.assertRaises(ApiExceptions.IdNotFoundError, update)

        responses.add(**{
            "method": responses.PUT,
            "url": "https://test.pl/api/0.6/changeset/111",
            "status": 409
        })
        self.assertRaises(ApiExceptions.ChangesetAlreadyClosedOrUserIsNotAnAuthor, update)
    
    @responses.activate
    def test_close(self):
        def close():
            return self.API.changeset.close(111)
        
        responses.add(**{
            "method": responses.PUT,
            "url": "https://test.pl/api/0.6/changeset/111/close",
            "body": "111",
            "status": 200
        })
        close()

        responses.add(**{
            "method": responses.PUT,
            "url": "https://test.pl/api/0.6/changeset/111/close",
            "status": 404
        })
        self.assertRaises(ApiExceptions.IdNotFoundError, close)

        responses.add(**{
            "method": responses.PUT,
            "url": "https://test.pl/api/0.6/changeset/111/close",
            "body": "111",
            "status": 409
        })
        self.assertRaises(ApiExceptions.ChangesetAlreadyClosedOrUserIsNotAnAuthor, close)

    @responses.activate
    def test_download(self):
        def download():
            return self.API.changeset.download(111)

        body = """<?xml version="1.0" encoding="UTF-8"?>
        <osmChange version="0.6" generator="CGImap 0.8.8 (3619883 faffy.openstreetmap.org)" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
            <create>
                <node id="4332425832" visible="true" version="1" changeset="250415" timestamp="2022-12-26T13:47:51Z" user="OrganicMapsTestUser" uid="14235" lat="52.5357228" lon="-69.7005038">
                    <tag k="testkey" v="firstnode"/>
                </node>
            </create>
            <modify>
                <node id="4332425832" visible="true" version="2" changeset="250415" timestamp="2022-12-26T13:47:51Z" user="OrganicMapsTestUser" uid="14235" lat="-22.5610561" lon="-3.3450657">
                    <tag k="testkey" v="secondnode"/>
                </node>
            </modify>
        </osmChange>
        """
        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/api/0.6/changeset/111/download",
            "body": body,
            "status": 200
        })
        generator = download()
        
        second_node = None
        for action, element in generator:
            if "testkey" in element.tags and element.tags.get("testkey") == "secondnode":
                second_node = copy(element)

        self.assertIsInstance(second_node, Node)


        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/api/0.6/changeset/111/download",
            "status": 404
        })
        self.assertRaises(ApiExceptions.IdNotFoundError, download)

    @responses.activate
    def test_upload(self):
        URL = "https://test.pl/api/0.6/changeset/123/upload"

        osmChange = OsmChange("0.1", "unittest", "123")
        osmChange.add(sample_dataclasses.node("simple_1"))
        should_print = "OsmChange(version=0.1, generator=unittest, sequence_number=123. Node: Create(0), Modify(0), Delete(0), None(1). Way: Create(0), Modify(0), Delete(0), None(0). Relation: Create(0), Modify(0), Delete(0), None(0)."
        self.assertEqual(str(osmChange), should_print)
        osmChange.add(sample_dataclasses.node("simple_2"), Action.MODIFY)
        osmChange.add(sample_dataclasses.way("simple_1"), Action.MODIFY)

        def upload():
            return self.API.changeset.upload(123, osmChange)
        
        responses.add(**{
            "method": responses.POST,
            "url": URL,
            "body": None, # TODO: To be supported
            "status": 200
        })
        upload()
        self.assertTrue(responses.assert_call_count(URL, 1))

        responses.add(**{
            "method": responses.POST,
            "url": URL,
            "status": 400
        })
        self.assertRaises(ApiExceptions.ErrorWhenParsingXML, upload)
        self.assertTrue(responses.assert_call_count(URL, 2))

        responses.add(**{
            "method": responses.POST,
            "url": URL,
            "status": 404
        })
        self.assertRaises(ApiExceptions.IdNotFoundError, upload)
        self.assertTrue(responses.assert_call_count(URL, 3))

        responses.add(**{
            "method": responses.POST,
            "url": URL,
            "status": 409
        })
        self.assertRaises(ApiExceptions.ChangesetAlreadyClosedOrUserIsNotAnAuthor, upload)
        self.assertTrue(responses.assert_call_count(URL, 4))

        responses.add(**{
            "method": responses.POST,
            "url": URL,
            "status": 999
        })
        self.assertRaises(ValueError, upload)
        self.assertTrue(responses.assert_call_count(URL, 5))