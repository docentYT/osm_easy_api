import unittest
import responses
from copy import copy

import os
from dotenv import load_dotenv
load_dotenv()
LOGIN, PASSWORD = os.getenv("login"), os.getenv("password")

from osm_easy_api import Api
from osm_easy_api.data_classes import Node, Way, Relation
from osm_easy_api.api import exceptions as ApiExceptions

class TestApiElements(unittest.TestCase):

    @responses.activate
    def test_create(self):
        responses.add(**{
            "method": responses.PUT,
            "url": "https://test.pl/api/0.6/node/create",
            "body": "1",
            "status": 200
        })

        api = Api("https://test.pl", LOGIN, PASSWORD)
        node = Node(latitude="123", longitude="321")
        self.assertEqual(api.elements.create(node, 123), 1)

    @responses.activate
    def test_get(self):
        should_be = "Node(id = 1, visible = None, version = 110, changeset_id = 232293, timestamp = 2022-02-22T11:31:20Z, user_id = 12342, tags = {'name': 'ali', 'source': 'local knowledge', 'start_date': '2022', 'traffic_calming': 'hump'}, latitude = 53.7573714, longitude = -0.4465657, )"
        body = """<osm version="0.6" generator="OpenStreetMap server" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
<node id="1" visible="true" version="110" changeset="232293" timestamp="2022-02-22T11:31:20Z" user="alisvndk88" uid="12342" lat="53.7573714" lon="-0.4465657">
<tag k="name" v="ali"/>
<tag k="source" v="local knowledge"/>
<tag k="start_date" v="2022"/>
<tag k="traffic_calming" v="hump"/>
</node>
</osm>
        """
        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/api/0.6/node/123",
            "body": body,
            "status": 200
        })

        api = Api("https://test.pl", LOGIN, PASSWORD)
        node = api.elements.get(Node, 123)
        self.assertEqual(str(node), should_be)

    @responses.activate
    def test_update(self):
        should_be = "Node(id = 1, visible = None, version = 1, changeset_id = 232293, timestamp = 2022-02-22T11:31:20Z, user_id = 12342, tags = {'name': 'ali', 'source': 'local knowledge', 'start_date': '2022', 'traffic_calming': 'hump'}, latitude = 1, longitude = -0.4465657, )"
        body = """<osm version="0.6" generator="OpenStreetMap server" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
<node id="1" visible="true" version="1" changeset="232293" timestamp="2022-02-22T11:31:20Z" user="alisvndk88" uid="12342" lat="1" lon="-0.4465657">
<tag k="name" v="ali"/>
<tag k="source" v="local knowledge"/>
<tag k="start_date" v="2022"/>
<tag k="traffic_calming" v="hump"/>
</node>
</osm>
        """
        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/api/0.6/node/123",
            "body": body,
            "status": 200
        })
        responses.add(**{
            "method": responses.PUT,
            "url": "https://test.pl/api/0.6/node/1",
            "body": "2",
            "status": 200
        })

        api = Api("https://test.pl", LOGIN, PASSWORD)
        node = api.elements.get(Node, 123)
        node.latitude = "1"
        self.assertEqual(api.elements.update(node, 1), 2)
        node = api.elements.get(Node, 123)
        self.assertEqual(str(node), should_be)

    @responses.activate
    def test_delete(self):
        responses.add(**{
            "method": responses.DELETE,
            "url": "https://test.pl/api/0.6/node/123",
            "body": "3",
            "status": 200
        })

        api = Api("https://test.pl", LOGIN, PASSWORD)
        node = Node(123)
        api.elements.delete(node, 333)

    @responses.activate
    def test_history(self):
        body = """<osm version="0.6" generator="CGImap 0.8.8 (763507 faffy.openstreetmap.org)" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
<node id="1" visible="true" version="1" changeset="1" timestamp="2009-09-03T10:17:35Z" user="guggis" uid="1" lat="46.9259516" lon="7.4002000"/>
<node id="1" visible="false" version="2" changeset="72" timestamp="2009-09-06T15:31:49Z" user="guggis" uid="1"/>
<node id="1" visible="true" version="3" changeset="187635" timestamp="2020-10-31T17:48:44Z" user="GoodClover" uid="10561" lat="53.7573714" lon="-0.4465657">
<tag k="amenity" v="clock"/>
</node>
<node id="1" visible="true" version="4" changeset="188429" timestamp="2020-11-27T11:25:28Z" user="juminet-dev" uid="10688" lat="53.7573714" lon="-0.4465657">
<tag k="amenity" v="clock"/>
<tag k="source" v="local knowledge"/>
</node>
</osm>"""
        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/api/0.6/node/123/history",
            "body": body,
            "status": 200
        })

        api = Api("https://test.pl", LOGIN, PASSWORD)
        history = api.elements.history(Node, 123)
        self.assertEqual(len(history), 4)
        self.assertEqual(history[3].user_id, 10688)

    @responses.activate
    def test_version(self):
        body = """<osm version="0.6" generator="OpenStreetMap server" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
<node id="1" visible="true" version="4" changeset="188429" timestamp="2020-11-27T11:25:28Z" user="juminet-dev" uid="10688" lat="53.7573714" lon="-0.4465657">
<tag k="amenity" v="clock"/>
<tag k="source" v="local knowledge"/>
</node>
</osm>"""
        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/api/0.6/node/123/4",
            "body": body,
            "status": 200
        })

        api = Api("https://test.pl", LOGIN, PASSWORD)
        version = api.elements.version(Node, 123, 4)
        self.assertEqual(version.user_id, 10688)

    @responses.activate
    def test_get_query(self):
        body = """<osm version="0.6" generator="CGImap 0.8.8 (763506 faffy.openstreetmap.org)" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
<node id="1" visible="true" version="110" changeset="232293" timestamp="2022-02-22T11:31:20Z" user="alisvndk88" uid="12342" lat="53.7573714" lon="-0.4465657">
<tag k="name" v="ali"/>
<tag k="source" v="local knowledge"/>
<tag k="start_date" v="2022"/>
<tag k="traffic_calming" v="hump"/>
</node>
<node id="2" visible="false" version="5" changeset="218253" timestamp="2021-07-16T14:35:08Z" user="samuelb" uid="10021"/>
</osm>"""

        responses.add(**{
                    "method": responses.GET,
                    "url": "https://test.pl/api/0.6/nodes?nodes=1,2",
                    "body": body,
                    "status": 200
                })

        api = Api("https://test.pl", LOGIN, PASSWORD)
        nodes = api.elements.get_query(Node, [1, 2])
        self.assertEqual(nodes[0].user_id, 12342)
        self.assertEqual(nodes[1].user_id, 10021)

    @responses.activate
    def test_relations(self):
        body = """<osm version="0.6" generator="CGImap 0.8.8 (763507 faffy.openstreetmap.org)" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
<relation id="79" visible="true" version="1" changeset="381" timestamp="2009-09-15T20:35:39Z" user="green525" uid="12">
<member type="way" ref="4751" role="outer"/>
<member type="way" ref="4752" role="outer"/>
<member type="way" ref="4757" role="outer"/>
<tag k="admin_level" v="9"/>
<tag k="alt_name" v="Korgõmõisa"/>
</relation>
<relation id="100" visible="true" version="1" changeset="386" timestamp="2009-09-15T20:42:18Z" user="green525" uid="12">
<member type="way" ref="4913" role="outer"/>
<member type="way" ref="4914" role="outer"/>
<member type="way" ref="4915" role="outer"/>
<member type="way" ref="4916" role="outer"/>
<member type="way" ref="4754" role="outer"/>
<member type="way" ref="4917" role="outer"/>
<tag k="admin_level" v="9"/>
</relation>
</osm>"""
        responses.add(**{
                    "method": responses.GET,
                    "url": "https://test.pl/api/0.6/way/111/relations",
                    "body": body,
                    "status": 200
                })
        
        api = Api("https://test.pl", LOGIN, PASSWORD)
        relations = api.elements.relations(Way, 111)
        self.assertEqual(relations[0].id, 79)
        self.assertEqual(relations[1].members[0].role, "outer")

    @responses.activate
    def test_ways(self):
        body = """<osm version="0.6" generator="CGImap 0.8.8 (763506 faffy.openstreetmap.org)" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
<way id="5638" visible="true" version="1" changeset="417" timestamp="2009-09-15T21:45:23Z" user="green525" uid="12">
</way>
<way id="5638" visible="true" version="1" changeset="417" timestamp="2009-09-15T21:45:23Z" user="green525" uid="12">
<nd ref="1368"/>
</way>
</osm>"""

        responses.add(**{
                            "method": responses.GET,
                            "url": "https://test.pl/api/0.6/node/111/ways",
                            "body": body,
                            "status": 200
                        })
                
        api = Api("https://test.pl", LOGIN, PASSWORD)
        ways = api.elements.ways(111)
        self.assertEqual(ways[0].id, 5638)
        self.assertEqual(ways[1].nodes[0].id, 1368)

    @responses.activate
    def test_full(self):
        body = """<osm version="0.6" generator="CGImap 0.8.8 (763510 faffy.openstreetmap.org)" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
<node id="571346" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:07Z" user="green525" uid="12" lat="57.6680386" lon="27.0883216"/>
<node id="571347" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:07Z" user="green525" uid="12" lat="57.6693578" lon="27.0864870"/>
<node id="571348" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:07Z" user="green525" uid="12" lat="57.6711863" lon="27.0916125"/>
<node id="571349" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:07Z" user="green525" uid="12" lat="57.6713047" lon="27.0916473"/>
<node id="571350" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:07Z" user="green525" uid="12" lat="57.6713134" lon="27.0915570"/>
<node id="571351" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:07Z" user="green525" uid="12" lat="57.6713637" lon="27.0913669"/>
<node id="571352" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:07Z" user="green525" uid="12" lat="57.6716535" lon="27.0908388"/>
<node id="571353" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:07Z" user="green525" uid="12" lat="57.6727166" lon="27.0898317"/>
<node id="571354" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:07Z" user="green525" uid="12" lat="57.6733457" lon="27.0890602"/>
<node id="571355" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:07Z" user="green525" uid="12" lat="57.6739327" lon="27.0880815"/>
<node id="571356" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:07Z" user="green525" uid="12" lat="57.6745159" lon="27.0872202"/>
<node id="571357" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:07Z" user="green525" uid="12" lat="57.6757980" lon="27.0860556"/>
<node id="571358" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:07Z" user="green525" uid="12" lat="57.6766301" lon="27.0863249"/>
<node id="571359" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:07Z" user="green525" uid="12" lat="57.6773723" lon="27.0867816"/>
<node id="571360" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:07Z" user="green525" uid="12" lat="57.6779142" lon="27.0891609"/>
<node id="571361" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:07Z" user="green525" uid="12" lat="57.6781759" lon="27.0914729"/>
<node id="571362" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:07Z" user="green525" uid="12" lat="57.6788840" lon="27.0915498"/>
<node id="571363" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:07Z" user="green525" uid="12" lat="57.6800650" lon="27.0910729"/>
<node id="571364" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:08Z" user="green525" uid="12" lat="57.6824734" lon="27.1082556"/>
<node id="571365" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:08Z" user="green525" uid="12" lat="57.6819202" lon="27.1084863"/>
<node id="571366" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:08Z" user="green525" uid="12" lat="57.6811597" lon="27.1090458"/>
<node id="571367" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:08Z" user="green525" uid="12" lat="57.6792847" lon="27.1083284"/>
<node id="571368" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:08Z" user="green525" uid="12" lat="57.6789593" lon="27.1085940"/>
<node id="571369" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:08Z" user="green525" uid="12" lat="57.6789167" lon="27.1104747"/>
<node id="571370" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:08Z" user="green525" uid="12" lat="57.6777798" lon="27.1120815"/>
<node id="571371" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:08Z" user="green525" uid="12" lat="57.6821509" lon="27.0952061"/>
<node id="571372" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:08Z" user="green525" uid="12" lat="57.6821993" lon="27.0955894"/>
<node id="571373" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:08Z" user="green525" uid="12" lat="57.6819003" lon="27.0958581"/>
<node id="571374" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:08Z" user="green525" uid="12" lat="57.6820605" lon="27.0984493"/>
<node id="571375" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:08Z" user="green525" uid="12" lat="57.6821702" lon="27.1014594"/>
<node id="571376" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:08Z" user="green525" uid="12" lat="57.6819854" lon="27.0939874"/>
<node id="571377" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:08Z" user="green525" uid="12" lat="57.6818008" lon="27.0928491"/>
<node id="571378" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:08Z" user="green525" uid="12" lat="57.6816037" lon="27.0927791"/>
<node id="571379" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:08Z" user="green525" uid="12" lat="57.6815136" lon="27.0926883"/>
<node id="571380" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:08Z" user="green525" uid="12" lat="57.6813820" lon="27.0926130"/>
<node id="571381" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:08Z" user="green525" uid="12" lat="57.6813012" lon="27.0922836"/>
<node id="571382" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:08Z" user="green525" uid="12" lat="57.6809371" lon="27.0916554"/>
<node id="571383" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:08Z" user="green525" uid="12" lat="57.6807847" lon="27.0915913"/>
<node id="571384" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:08Z" user="green525" uid="12" lat="57.6806238" lon="27.0917370"/>
<node id="571385" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:08Z" user="green525" uid="12" lat="57.6804800" lon="27.0917437"/>
<node id="571386" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:08Z" user="green525" uid="12" lat="57.6802748" lon="27.0915506"/>
<node id="571387" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:09Z" user="green525" uid="12" lat="57.6801522" lon="27.0913006"/>
<node id="571388" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:09Z" user="green525" uid="12" lat="57.6626714" lon="27.1005699"/>
<node id="571389" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:09Z" user="green525" uid="12" lat="57.6640539" lon="27.1022133"/>
<node id="571390" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:09Z" user="green525" uid="12" lat="57.6657370" lon="27.1048681"/>
<node id="571391" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:09Z" user="green525" uid="12" lat="57.6667347" lon="27.1069345"/>
<node id="571392" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:09Z" user="green525" uid="12" lat="57.6672713" lon="27.1082145"/>
<node id="571393" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:09Z" user="green525" uid="12" lat="57.6684662" lon="27.1095779"/>
<node id="571394" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:09Z" user="green525" uid="12" lat="57.6688884" lon="27.1102379"/>
<node id="571395" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:09Z" user="green525" uid="12" lat="57.6674261" lon="27.0892154"/>
<node id="571396" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:09Z" user="green525" uid="12" lat="57.6647617" lon="27.0922925"/>
<node id="571397" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:09Z" user="green525" uid="12" lat="57.6626050" lon="27.0951005"/>
<node id="571398" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:09Z" user="green525" uid="12" lat="57.6626071" lon="27.0997070"/>
<node id="571399" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:09Z" user="green525" uid="12" lat="57.6722880" lon="27.1103280"/>
<node id="571400" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:09Z" user="green525" uid="12" lat="57.6723685" lon="27.1096890"/>
<node id="571401" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:09Z" user="green525" uid="12" lat="57.6728846" lon="27.1084396"/>
<node id="571402" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:09Z" user="green525" uid="12" lat="57.6748692" lon="27.1114048"/>
<node id="571403" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:09Z" user="green525" uid="12" lat="57.6770447" lon="27.1102738"/>
<way id="6177" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:07Z" user="green525" uid="12">
<nd ref="571346"/>
<nd ref="571347"/>
<nd ref="571348"/>
<nd ref="571349"/>
<nd ref="571350"/>
<nd ref="571351"/>
<nd ref="571352"/>
<nd ref="571353"/>
<nd ref="571354"/>
<nd ref="571355"/>
<nd ref="571356"/>
<nd ref="571357"/>
<nd ref="571358"/>
<nd ref="571359"/>
<nd ref="571360"/>
<nd ref="571361"/>
<nd ref="571362"/>
<nd ref="571363"/>
<tag k="admin_level" v="9"/>
<tag k="boundary" v="administrative"/>
<tag k="source" v="Maa-amet 01.06.2009"/>
</way>
<way id="6178" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:08Z" user="green525" uid="12">
<nd ref="571364"/>
<nd ref="571365"/>
<nd ref="571366"/>
<nd ref="571367"/>
<nd ref="571368"/>
<nd ref="571369"/>
<nd ref="571370"/>
<tag k="admin_level" v="9"/>
<tag k="boundary" v="administrative"/>
<tag k="source" v="Maa-amet 01.06.2009"/>
</way>
<way id="6179" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:08Z" user="green525" uid="12">
<nd ref="571371"/>
<nd ref="571372"/>
<nd ref="571373"/>
<nd ref="571374"/>
<nd ref="571375"/>
<nd ref="571364"/>
<tag k="admin_level" v="9"/>
<tag k="boundary" v="administrative"/>
<tag k="source" v="Maa-amet 01.06.2009"/>
</way>
<way id="6180" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:09Z" user="green525" uid="12">
<nd ref="571371"/>
<nd ref="571376"/>
<nd ref="571377"/>
<nd ref="571378"/>
<nd ref="571379"/>
<nd ref="571380"/>
<nd ref="571381"/>
<nd ref="571382"/>
<nd ref="571383"/>
<nd ref="571384"/>
<nd ref="571385"/>
<nd ref="571386"/>
<nd ref="571387"/>
<nd ref="571363"/>
<tag k="admin_level" v="9"/>
<tag k="boundary" v="administrative"/>
<tag k="source" v="Maa-amet 01.06.2009"/>
</way>
<way id="6181" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:09Z" user="green525" uid="12">
<nd ref="571388"/>
<nd ref="571389"/>
<nd ref="571390"/>
<nd ref="571391"/>
<nd ref="571392"/>
<nd ref="571393"/>
<nd ref="571394"/>
<tag k="admin_level" v="9"/>
<tag k="boundary" v="administrative"/>
<tag k="source" v="Maa-amet 01.06.2009"/>
</way>
<way id="6182" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:09Z" user="green525" uid="12">
<nd ref="571346"/>
<nd ref="571395"/>
<nd ref="571396"/>
<nd ref="571397"/>
<nd ref="571398"/>
<nd ref="571388"/>
<tag k="admin_level" v="9"/>
<tag k="boundary" v="administrative"/>
<tag k="source" v="Maa-amet 01.06.2009"/>
</way>
<way id="6183" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:09Z" user="green525" uid="12">
<nd ref="571394"/>
<nd ref="571399"/>
<nd ref="571400"/>
<nd ref="571401"/>
<nd ref="571402"/>
<nd ref="571403"/>
<nd ref="571370"/>
<tag k="admin_level" v="9"/>
<tag k="boundary" v="administrative"/>
<tag k="source" v="Maa-amet 01.06.2009"/>
</way>
<relation id="226" visible="true" version="1" changeset="426" timestamp="2009-09-15T22:04:10Z" user="green525" uid="12">
<member type="way" ref="6177" role="outer"/>
<member type="way" ref="6178" role="outer"/>
<member type="way" ref="6179" role="outer"/>
<member type="way" ref="6180" role="outer"/>
<member type="way" ref="6181" role="outer"/>
<member type="way" ref="6182" role="outer"/>
<member type="way" ref="6183" role="outer"/>
<tag k="admin_level" v="9"/>
<tag k="alt_name" v="Piipsemäe"/>
<tag k="boundary" v="administrative"/>
<tag k="EHAK:code" v="6179"/>
<tag k="EHAK:countycode" v="0086"/>
<tag k="EHAK:parishcode" v="0181"/>
<tag k="is_in" v="Haanja vald"/>
<tag k="name" v="Piipsemäe küla"/>
<tag k="type" v="multipolygon"/>
</relation>
</osm>"""

        responses.add(**{
                            "method": responses.GET,
                            "url": "https://test.pl/api/0.6/relation/226/full",
                            "body": body,
                            "status": 200
                        })
                
        api = Api("https://test.pl", LOGIN, PASSWORD)
        relation = api.elements.full(Relation, 226)
        self.assertEqual(relation.id, 226)
        self.assertEqual(relation.members[1].element.id, 6178)
        self.assertEqual(relation.members[2].element.id, 6179)
        self.assertEqual(relation.members[2].element.nodes[0].id, 571371)
        self.assertEqual(relation.members[2].element.nodes[0].changeset_id, 426)

        body = """<osm version="0.6" generator="CGImap 0.8.8 (763506 faffy.openstreetmap.org)" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
<node id="5281" visible="true" version="1" changeset="287" timestamp="2009-09-14T23:02:39Z" user="green525" uid="12" lat="58.5769849" lon="26.2733110"/>
<node id="5282" visible="true" version="1" changeset="287" timestamp="2009-09-14T23:02:39Z" user="green525" uid="12" lat="58.5769093" lon="26.2764914"/>
<node id="5283" visible="true" version="1" changeset="287" timestamp="2009-09-14T23:02:40Z" user="green525" uid="12" lat="58.5770894" lon="26.2769814"/>
<node id="5284" visible="true" version="1" changeset="287" timestamp="2009-09-14T23:02:40Z" user="green525" uid="12" lat="58.5772252" lon="26.2773688"/>
<node id="5285" visible="true" version="1" changeset="287" timestamp="2009-09-14T23:02:40Z" user="green525" uid="12" lat="58.5791452" lon="26.2765855"/>
<node id="5286" visible="true" version="1" changeset="287" timestamp="2009-09-14T23:02:40Z" user="green525" uid="12" lat="58.5793185" lon="26.2789710"/>
<node id="5287" visible="true" version="1" changeset="287" timestamp="2009-09-14T23:02:40Z" user="green525" uid="12" lat="58.5812457" lon="26.2783619"/>
<node id="5288" visible="true" version="1" changeset="287" timestamp="2009-09-14T23:02:40Z" user="green525" uid="12" lat="58.5815179" lon="26.2806201"/>
<node id="5289" visible="true" version="1" changeset="287" timestamp="2009-09-14T23:02:40Z" user="green525" uid="12" lat="58.5816982" lon="26.2821864"/>
<node id="5290" visible="true" version="1" changeset="287" timestamp="2009-09-14T23:02:40Z" user="green525" uid="12" lat="58.5823199" lon="26.2875168"/>
<node id="5291" visible="true" version="1" changeset="287" timestamp="2009-09-14T23:02:40Z" user="green525" uid="12" lat="58.5834131" lon="26.2869959"/>
<node id="5292" visible="true" version="1" changeset="287" timestamp="2009-09-14T23:02:40Z" user="green525" uid="12" lat="58.5840471" lon="26.2918803"/>
<way id="226" visible="true" version="1" changeset="287" timestamp="2009-09-14T23:02:40Z" user="green525" uid="12">
<nd ref="5281"/>
<nd ref="5282"/>
<nd ref="5283"/>
<nd ref="5284"/>
<nd ref="5285"/>
<nd ref="5286"/>
<nd ref="5287"/>
<nd ref="5288"/>
<nd ref="5289"/>
<nd ref="5290"/>
<nd ref="5291"/>
<nd ref="5292"/>
<tag k="admin_level" v="9"/>
<tag k="boundary" v="administrative"/>
<tag k="source" v="Maa-amet 01.06.2009"/>
</way>
</osm>"""

        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/api/0.6/way/226/full",
            "body": body,
            "status": 200
        })

        way = api.elements.full(Way, 226)
        self.assertEqual(way.id, 226)
        self.assertEqual(way.nodes[0].id, 5281)
        self.assertEqual(way.nodes[0].latitude, "58.5769849")
        self.assertEqual(way.nodes[0].longitude, "26.2733110")
        self.assertEqual(way.nodes[1].latitude, "58.5769093")
