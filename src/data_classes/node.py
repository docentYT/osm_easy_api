from dataclasses import dataclass

from ..data_classes.osm_object_primitive import osm_object_primitive

@dataclass
class Node(osm_object_primitive):
    latitude: str | None = None   # str to prevent rounding values
    longitude: str | None = None

    def __post_init__(self):
        super().__init__(self.id, self.visible, self.version, self.changeset_id, self.timestamp, self.user_id, self.tags)