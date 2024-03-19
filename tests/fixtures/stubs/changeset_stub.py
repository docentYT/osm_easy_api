from osm_easy_api.data_classes import Changeset, Tags

XML_RESPONSE_BODY = """<?xml version="1.0" encoding="UTF-8"?>
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

OBJECT = Changeset(
            id=111,
            timestamp="2022-12-26T13:33:40Z",
            open=False,
            user_id="18179",
            comments_count="1",
            changes_count="0",
            tags=Tags({"testing": "yes", "created_by": "osm-python-api", "comment": "aaa"}),
            discussion=[{"date": "2022-12-26T14:22:22Z", "user_id": "18179", "text": "abc"}]
        )