from typing import Dict

class URLs:
    def __init__(self, base_url: str):
        self.base_url = base_url

        self.misc: Dict[str, str] = {
            "versions": base_url + "/api/versions",
            "capabilities": base_url + "/api/capabilities",
            "map": base_url + "/api/0.6/map?bbox={left},{bottom},{right},{top}",
            "permissions": base_url + "/api/0.6/permissions"
        }

        self.changeset: Dict[str, str] = {
            "create": base_url + "/api/0.6/changeset/create",
            "update": base_url + "/api/0.6/changeset/{id}",
            "get": base_url + "/api/0.6/changeset",
            "get_query": base_url + "/api/0.6/changesets",
            "close": base_url + "/api/0.6/changeset/{id}/close",
            "download": base_url + "/api/0.6/changeset/{id}/download",
            "upload": base_url + "/api/0.6/changeset/{id}/upload",
        }

        self.changeset_discussion: Dict[str, str] = {
            "comment": base_url + "/api/0.6/changeset/{id}/comment?text={text}",
            "subscribe": base_url + "/api/0.6/changeset/{id}/subscribe",
            "unsubscribe": base_url + "/api/0.6/changeset/{id}/unsubscribe",
            "hide": base_url + "/api/0.6/changeset/comment/{comment_id}/hide",
            "unhide": base_url + "/api/0.6/changeset/comment/{comment_id}/unhide"
        }