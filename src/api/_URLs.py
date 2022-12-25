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