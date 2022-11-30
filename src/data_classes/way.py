from dataclasses import dataclass, field

from ..data_classes.osm_object_primitive import osm_object_primitive
from ..data_classes.node import Node

@dataclass
class Way(osm_object_primitive):
    nodes: list[Node] = field(default_factory=list)

    def __post_init__(self):
        super().__init__(self.id, self.visible, self.version, self.changeset_id, self.timestamp, self.user_id, self.tags)