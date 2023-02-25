from typing import Dict

class URLs:
    def __init__(self, base_url: str):
        self.base_url = base_url
        six_url = base_url + "/api/0.6"

        self.misc: Dict[str, str] = {
            "versions": base_url + "/api/versions",
            "capabilities": base_url + "/api/capabilities",
            "map": six_url + "/map?bbox={left},{bottom},{right},{top}",
            "permissions": six_url + "/permissions"
        }

        self.changeset: Dict[str, str] = {
            "create": six_url + "/changeset/create",
            "update": six_url + "/changeset/{id}",
            "get": six_url + "/changeset",
            "get_query": six_url + "/changesets",
            "close": six_url + "/changeset/{id}/close",
            "download": six_url + "/changeset/{id}/download",
            "upload": six_url + "/changeset/{id}/upload",
        }

        self.changeset_discussion: Dict[str, str] = {
            "comment": six_url + "/changeset/{id}/comment?text={text}",
            "subscribe": six_url + "/changeset/{id}/subscribe",
            "unsubscribe": six_url + "/changeset/{id}/unsubscribe",
            "hide": six_url + "/changeset/comment/{comment_id}/hide",
            "unhide": six_url + "/changeset/comment/{comment_id}/unhide"
        }

        self.elements: Dict[str, str] = {
            "create": six_url + "/{element_type}/create",
            "read": six_url + "/{element_type}/{id}",
            "update": six_url + "/{element_type}/{id}",
            "delete": six_url + "/{element_type}/{id}",
            "history": six_url + "/{element_type}/{id}/history",
            "version": six_url + "/{element_type}/{id}/{version}",
            "multi_fetch": six_url + "/{element_type}",
            "relations": six_url + "/{element_type}/{id}/relations",
            "ways": six_url + "/node/{id}/ways",
            "full": six_url + "/{element_type}/{id}/full",
            "redaction": six_url + "/{element_type}/{id}/{version}/redact?redaction={redaction_id}"
        }