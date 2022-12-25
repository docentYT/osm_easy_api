import unittest
import responses

from src import Api

class TestApi(unittest.TestCase):
    api = Api("https://test.pl")

    def test__request_raw_stream(self):
        with self.assertRaises(ValueError):
            self.api._request_raw_stream("https://master.apis.dev.openstreetmap.org/api/wegwegwegwe")

class TestApiMisc(unittest.TestCase):
    api = Api("https://test.pl")

    @responses.activate
    def test_versions(self):
        versions_body = """<?xml version="1.0" encoding="UTF-8"?>
        <osm generator="OpenStreetMap server" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
            <api>
                <version>0.6</version>
                <version>0.5</version>
            </api>
        </osm>
        """
        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/api/versions",
            "body": versions_body,
            "status": 200
        })

        self.assertEqual(self.api.misc.versions(), ["0.6", "0.5"])

    @responses.activate
    def test_capabilities(self):
        capabilities_body = """<?xml version="1.0" encoding="UTF-8"?>
        <osm version="0.6" generator="OpenStreetMap server" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
            <api>
                <version minimum="0.6" maximum="0.6"/>
                <area maximum="0.25"/>
                <note_area maximum="25"/>
                <tracepoints per_page="5000"/>
                <waynodes maximum="2000"/>
                <relationmembers maximum="32000"/>
                <changesets maximum_elements="10000"/>
                <timeout seconds="300"/>
                <status database="online" api="online" gpx="online"/>
            </api>
            <policy>
                <imagery>
                    <blacklist regex=".*\\.google(apis)?\\..*/.*"/>
                    <blacklist regex="http://xdworld\\.vworld\\.kr:8080/.*"/>
                    <blacklist regex=".*\\.here\\.com[/:].*"/>
                </imagery>
            </policy>
        </osm>
        """
        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/api/capabilities",
            "body": capabilities_body,
            "status": 200
        })

        self.assertEqual(self.api.misc.capabilities(), {
            "osm": {
                "version": "0.6",
                "generator": "OpenStreetMap server",
                "copyright": "OpenStreetMap and contributors",
                "attribution": "http://www.openstreetmap.org/copyright",
                "license": "http://opendatacommons.org/licenses/odbl/1-0/"
            },
            "api": {
                "version": {
                    "minimum": "0.6",
                    "maximum": "0.6"
                },
                "area": {
                    "maximum": "0.25"
                },
                "note_area": {
                    "maximum": "25"
                },
                "tracepoints": {
                    "per_page": "5000"
                },
                "waynodes": {
                    "maximum": "2000"
                },
                "relationmembers": {
                    "maximum": "32000"
                },
                "changesets": {
                    "maximum_elements": "10000"
                },
                "timeout": {
                    "seconds": "300"
                },
                "status": {
                    "database": "online",
                    "api": "online",
                    "gpx": "online"
                }
            },
            "policy": {
                "imagery": {
                    "blacklist_regex": [".*\\.google(apis)?\\..*/.*", "http://xdworld\\.vworld\\.kr:8080/.*", ".*\\.here\\.com[/:].*"]
                }
            }
        })

    @responses.activate
    def test_get_map_in_bbox(self):
        map_body = """<?xml version="1.0" encoding="UTF-8"?>
        <osm version="0.6" generator="CGImap 0.8.8 (1745474 spike-07.openstreetmap.org)" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
            <bounds minlat="52.2456710" minlon="21.1049350" maxlat="52.2463930" maxlon="21.1060240"/>
            <node id="209148101" visible="true" version="5" changeset="19209334" timestamp="2013-12-01T12:46:59Z" user="Tomekg" uid="373244" lat="52.2442992" lon="21.1159144"/>
            <node id="209148170" visible="true" version="6" changeset="95380013" timestamp="2020-12-06T21:05:19Z" user="Robercin" uid="699708" lat="52.2443420" lon="21.1147933"/>
            <node id="209148176" visible="true" version="7" changeset="124865726" timestamp="2022-08-13T19:42:24Z" user="kwiatek_123" uid="14519311" lat="52.2444528" lon="21.1139596">
                <tag k="crossing" v="uncontrolled"/>
                <tag k="crossing:island" v="no"/>
                <tag k="crossing_ref" v="zebra"/>
                <tag k="highway" v="crossing"/>
                <tag k="tactile_paving" v="yes"/>
            </node>
            <node id="209148181" visible="true" version="7" changeset="19209334" timestamp="2013-12-01T12:47:00Z" user="Tomekg" uid="373244" lat="52.2447030" lon="21.1123870"/>
            <node id="209148183" visible="true" version="9" changeset="126329493" timestamp="2022-09-18T12:44:24Z" user="kwiatek_123" uid="14519311" lat="52.2452268" lon="21.1093203"/>
        </osm>
        """
        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/api/0.6/map?bbox=111,222,333,444",
            "body": map_body,
            "status": 200
        })

        gen = self.api.misc.get_map_in_bbox(111, 222, 333, 444)
        self.assertEqual(next(gen).id, 209148101)

    @responses.activate
    def test_permissions(self):
        permissions_body = """<?xml version="1.0" encoding="UTF-8"?>
        <osm version="0.6" generator="OpenStreetMap server" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
            <permissions>
                <permission name="allow_read_prefs"/>
                <permission name="allow_write_prefs"/>
                <permission name="allow_write_diary"/>
                <permission name="allow_write_api"/>
                <permission name="allow_read_gpx"/>
                <permission name="allow_write_gpx"/>
                <permission name="allow_write_notes"/>
            </permissions>
        </osm>
        """
        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/api/0.6/permissions",
            "body": permissions_body,
            "status": 200
        })

        self.assertEqual(self.api.misc.permissions(), ["allow_read_prefs", "allow_write_prefs", "allow_write_diary", "allow_write_api", "allow_read_gpx", "allow_write_gpx", "allow_write_notes"])

class TestApiTwo(unittest.TestCase):
    def test_aaa(self):
        self.assertEqual(1, 1)