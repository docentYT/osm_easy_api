from osm_easy_api import Note, Comment, User

XML_RESPONSE_BODY = """<osm version="0.6" generator="OpenStreetMap server" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
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

OBJECT = Note(id=37970, latitude="52.2722000", longitude="20.4660000", note_created_at="2023-02-26 13:37:26 UTC", open=True, comments=[
    Comment(comment_created_at="2023-02-26 13:37:26 UTC", user=User(id=18179, display_name="kwiatek_123 bot"), action="opened", text="test", html="")
])