import unittest
import responses

from ..fixtures.default_variables import LOGIN, PASSWORD

from osm_easy_api import Api

class TestApiElements(unittest.TestCase):

    @responses.activate
    def test_get(self):
        body = """<osm version="0.6" generator="OpenStreetMap server" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
<user id="1" display_name="guggis" account_created="2009-09-03T10:15:41Z">
<description>profil profil </description>
<contributor-terms agreed="true"/>
<img href="https://www.gravatar.com/avatar/123.png"/>
<roles> </roles>
<changesets count="1247"/>
<traces count="0"/>
<blocks>
<received count="0" active="0"/>
...
</blocks>
...
</user>
...
</osm>"""
        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/api/0.6/user/123",
            "body": body,
            "status": 200
        })

        api = Api("https://test.pl", LOGIN, PASSWORD)
        user = api.user.get(123)
        self.assertEqual(user.display_name, "guggis")
        self.assertEqual(user.img_url, "https://www.gravatar.com/avatar/123.png")
        self.assertEqual(user.changesets_count, 1247)

    @responses.activate
    def test_query(self):
        body = """<osm version="0.6" generator="OpenStreetMap server" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
<user id="1" display_name="guggis" account_created="2009-09-03T10:15:41Z">
<description>profil profil </description>
<contributor-terms agreed="true"/>
<img href="https://www.gravatar.com/avatar/123.png"/>
<roles> </roles>
<changesets count="1247"/>
<traces count="0"/>
<blocks>
<received count="0" active="0"/>
...
</blocks>
...
</user>
...
</osm>"""
        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/api/0.6/users?users=123",
            "body": body,
            "status": 200
        })

        api = Api("https://test.pl", LOGIN, PASSWORD)
        user = api.user.get_query([123])[0]
        self.assertEqual(user.display_name, "guggis")
        self.assertEqual(user.img_url, "https://www.gravatar.com/avatar/123.png")
        self.assertEqual(user.changesets_count, 1247)

    @responses.activate
    def test_get_preferences(self):
        body = """<osm version="0.6" generator="OpenStreetMap server">
	<preferences>
		<preference k="a" v="b" />
		<preference k="c" v="d" />
	</preferences>
</osm>"""
        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/api/0.6/user/preferences",
            "body": body,
            "status": 200
        })

        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/api/0.6/user/preferences/c",
            "body": "d",
            "status": 200
        })

        api = Api("https://test.pl", LOGIN, PASSWORD)
        preferences = api.user.get_preferences()
        self.assertEqual(preferences, {"a": "b", "c": "d"})
        preferences = api.user.get_preferences("c")
        self.assertEqual(preferences, {"c": "d"})

    @responses.activate
    def test_set_prefences(self):
        responses.add(**{
            "method": responses.PUT,
            "url": "https://test.pl/api/0.6/user/preferences",
            "body": None,
            "status": 200
        })

        api = Api("https://test.pl", LOGIN, PASSWORD)
        api.user.set_preferences({"a": "b"})

    @responses.activate
    def test_delete_preference(self):
        responses.add(**{
            "method": responses.DELETE,
            "url": "https://test.pl/api/0.6/user/preferences/c",
            "body": None,
            "status": 200
        })

        api = Api("https://test.pl", LOGIN, PASSWORD)
        api.user.delete_preference("c")