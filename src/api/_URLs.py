from typing import Dict

class URLs:
    def __init__(self, base_url: str):
        self.base_url = base_url

        self.misc: Dict[str, str] = {
            "versions": base_url + "/api/versions",
            "capabilities": base_url + "/api/capabilities",
            "map": base_url + "/api/0.6/map",
            "permissions": base_url + "/api/0.6/permissions"
        }

        self.changeset: Dict[str, str] = {
            "create": base_url + "/api/0.6/changeset/create",
            "update": base_url + "/api/0.6/changeset/{id}",
            "get": base_url + "/api/0.6/changeset",
            "close": base_url + "/api/0.6/changeset/{id}/close",
            "download": base_url + "/api/0.6/changeset/{id}/download",
            "upload": base_url + "/api/0.6/changeset/{id}/upload"
        }