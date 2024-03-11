import unittest
import responses
from copy import copy

from ..fixtures.default_variables import LOGIN, PASSWORD

from osm_easy_api import Api
from osm_easy_api.data_classes import Changeset, Tags, Node
from osm_easy_api.api import exceptions as ApiExceptions

class TestApiChangeset(unittest.TestCase):

    @responses.activate
    def test_create(self):
        responses.add(**{
            "method": responses.PUT,
            "url": "https://test.pl/api/0.6/changeset/create",
            "body": "111",
            "status": 200
        })

        api = Api("https://test.pl", LOGIN, PASSWORD)
        self.assertEqual(api.changeset.create("ABC"), 111)

    @responses.activate
    def test_get(self):
        body = """<?xml version="1.0" encoding="UTF-8"?>
            <osm version="0.6" generator="CGImap 0.8.8 (3619885 faffy.openstreetmap.org)" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
                <changeset id="111" created_at="2022-12-26T13:33:40Z" closed_at="2022-12-26T14:22:04Z" open="false" user="kwiatek_123 bot" uid="18179" comments_count="1" changes_count="0">
                    <tag k="testing" v="yes"/>
                    <tag k="created_by" v="osm-python-api"/>
                    <tag k="comment" v="aaa"/>
                    <discussion>
                        <comment date="2022-12-26T14:22:22Z" uid="18179" user="kwiatek_123 bot">
                            <text>abc</text>
                        </comment>
                    </discussion>
                </changeset>
            </osm>
        """
        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/api/0.6/changeset/111?include_discussion=true",
            "body": body,
            "status": 200
        })

        api = Api("https://test.pl", LOGIN, PASSWORD)
        changeset = Changeset(
            111,
            "2022-12-26T13:33:40Z",
            False,
            "18179",
            "1",
            "0",
            Tags({"testing": "yes", "created_by": "osm-python-api", "comment": "aaa"}),
            [{"date": "2022-12-26T14:22:22Z", "user_id": "18179", "text": "abc"}]
        )

        testing_changeset = api.changeset.get(111, True)
        self.assertEqual(testing_changeset.id, changeset.id)
        self.assertEqual(testing_changeset.timestamp, changeset.timestamp)
        self.assertEqual(testing_changeset.open, changeset.open)
        self.assertEqual(testing_changeset.user_id, changeset.user_id)
        self.assertEqual(testing_changeset.comments_count, changeset.comments_count)
        self.assertEqual(testing_changeset.changes_count, changeset.changes_count)
        self.assertEqual(testing_changeset.tags, changeset.tags)
        self.assertEqual(testing_changeset.discussion, changeset.discussion)

        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/api/0.6/changeset/111?include_discussion=true",
            "status": 404
        })

        def get():
            return api.changeset.get(111, True)
        
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
            "url": "https://test.pl/api/0.6/changesets/?user=18179&limit=100",
            "body": body,
            "status": 200
        })

        api = Api("https://test.pl", LOGIN, PASSWORD)
        changeset = Changeset(
            222,
            "2023-01-10T16:48:58Z",
            False,
            "18179",
            "0",
            "0",
            Tags({"comment": "Upload relation test"})
        )

        testing_changeset = api.changeset.get_query(user_id="18179")[1]
        self.assertEqual(testing_changeset.id, changeset.id)
        self.assertEqual(testing_changeset.timestamp, changeset.timestamp)
        self.assertEqual(testing_changeset.open, changeset.open)
        self.assertEqual(testing_changeset.user_id, changeset.user_id)
        self.assertEqual(testing_changeset.comments_count, changeset.comments_count)
        self.assertEqual(testing_changeset.changes_count, changeset.changes_count)
        self.assertEqual(testing_changeset.tags, changeset.tags)

        body = """<osm version="0.6" generator="OpenStreetMap server" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
    <changeset id="111" created_at="2023-01-10T16:49:30Z" open="false" comments_count="0" changes_count="3" closed_at="2023-01-10T16:52:52Z" min_lat="52.2423700" min_lon="21.1171000" max_lat="52.2423700" max_lon="21.1171000" uid="18179" user="kwiatek_123 bot">
        <tag k="comment" v="Upload relation test"/>
    </changeset>
</osm>
        """

        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/api/0.6/changesets/?user=18179&limit=1",
            "body": body,
            "status": 200
        })
        changeset_list = api.changeset.get_query(user_id="18179", limit=1)
        self.assertEqual(changeset_list.__len__(), 1)

        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/api/0.6/changeset/111?include_discussion=true",
            "status": 404
        })

        def get():
            return api.changeset.get(111, True)
        
        self.assertRaises(ApiExceptions.IdNotFoundError, get)

    @responses.activate
    def test_update(self):
        body = """<?xml version="1.0" encoding="UTF-8"?>
            <osm version="0.6" generator="CGImap 0.8.8 (3619885 faffy.openstreetmap.org)" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
                <changeset id="111" created_at="2022-12-26T13:33:40Z" closed_at="2022-12-26T14:22:04Z" open="false" user="kwiatek_123 bot" uid="18179" comments_count="1" changes_count="0">
                    <tag k="testing" v="yes"/>
                    <tag k="created_by" v="osm-python-api"/>
                    <tag k="comment" v="aaa"/>
                    <discussion>
                        <comment date="2022-12-26T14:22:22Z" uid="18179" user="kwiatek_123 bot">
                            <text>abc</text>
                        </comment>
                    </discussion>
                </changeset>
            </osm>
        """
        responses.add(**{
            "method": responses.PUT,
            "url": "https://test.pl/api/0.6/changeset/111",
            "body": body,
            "status": 200
        })

        changeset = Changeset(
            111,
            "2022-12-26T13:33:40Z",
            False,
            "18179",
            "1",
            "0",
            Tags({"testing": "yes", "created_by": "osm-python-api", "comment": "aaa"}),
            [{"date": "2022-12-26T14:22:22Z", "user_id": "18179", "text": "abc"}]
        )

        api = Api("https://test.pl", LOGIN, PASSWORD)

        testing_changeset = api.changeset.update(111, "BBB")
        self.assertEqual(testing_changeset.id, changeset.id)
        self.assertEqual(testing_changeset.timestamp, changeset.timestamp)
        self.assertEqual(testing_changeset.open, changeset.open)
        self.assertEqual(testing_changeset.user_id, changeset.user_id)
        self.assertEqual(testing_changeset.comments_count, changeset.comments_count)
        self.assertEqual(testing_changeset.changes_count, changeset.changes_count)
        self.assertEqual(testing_changeset.tags, changeset.tags)
        self.assertEqual(testing_changeset.discussion, changeset.discussion)

        body = """<?xml version="1.0" encoding="UTF-8"?>
            <osm version="0.6" generator="CGImap 0.8.8 (3619885 faffy.openstreetmap.org)" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
                <changeset id="111" created_at="2022-12-26T13:33:40Z" closed_at="2022-12-26T14:22:04Z" open="false" user="kwiatek_123 bot" uid="18179" comments_count="1" changes_count="0">
                    <tag k="testing" v="no"/>
                    <tag k="created_by" v="osm-python-api"/>
                    <tag k="comment" v="aaa"/>
                    <discussion>
                        <comment date="2022-12-26T14:22:22Z" uid="18179" user="kwiatek_123 bot">
                            <text>abc</text>
                        </comment>
                    </discussion>
                </changeset>
            </osm>
        """
        responses.add(**{
            "method": responses.PUT,
            "url": "https://test.pl/api/0.6/changeset/111",
            "body": body,
            "status": 200
        })
        testing_changeset = api.changeset.update(111, "BBB" , Tags({"testing": "no"}))
        new_tags = copy(changeset.tags)
        new_tags.update({"testing": "no"})
        self.assertEqual(testing_changeset.id, changeset.id)
        self.assertEqual(testing_changeset.timestamp, changeset.timestamp)
        self.assertEqual(testing_changeset.open, changeset.open)
        self.assertEqual(testing_changeset.user_id, changeset.user_id)
        self.assertEqual(testing_changeset.comments_count, changeset.comments_count)
        self.assertEqual(testing_changeset.changes_count, changeset.changes_count)
        self.assertEqual(testing_changeset.tags, new_tags)
        self.assertEqual(testing_changeset.discussion, changeset.discussion)

        def update():
            return api.changeset.update(111, "BBB")
        responses.add(**{
            "method": responses.PUT,
            "url": "https://test.pl/api/0.6/changeset/111",
            "body": body,
            "status": 404
        })
        self.assertRaises(ApiExceptions.IdNotFoundError, update)

        responses.add(**{
            "method": responses.PUT,
            "url": "https://test.pl/api/0.6/changeset/111",
            "body": body,
            "status": 409
        })
        self.assertRaises(ApiExceptions.ChangesetAlreadyClosedOrUserIsNotAnAuthor, update)
    
    @responses.activate
    def test_close(self):
        responses.add(**{
            "method": responses.PUT,
            "url": "https://test.pl/api/0.6/changeset/create",
            "body": "111",
            "status": 200
        })

        responses.add(**{
            "method": responses.PUT,
            "url": "https://test.pl/api/0.6/changeset/111/close",
            "body": "111",
            "status": 200
        })

        api = Api("https://test.pl", LOGIN, PASSWORD)
        changeset_id = api.changeset.create("ABC")
        def close():
            return api.changeset.close(changeset_id)

        close()

        responses.add(**{
            "method": responses.PUT,
            "url": "https://test.pl/api/0.6/changeset/111/close",
            "body": "111",
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

        api = Api("https://test.pl")

        generator = api.changeset.download(111)
        
        second_node = None
        for action, element in generator:
            if "testkey" in element.tags and element.tags.get("testkey") == "secondnode":
                second_node = copy(element)

        self.assertIsInstance(second_node, Node)


        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/api/0.6/changeset/111/download",
            "body": body,
            "status": 404
        })

        def download():
            return api.changeset.download(111)
        
        self.assertRaises(ApiExceptions.IdNotFoundError, download)