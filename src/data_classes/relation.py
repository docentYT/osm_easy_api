from dataclasses import dataclass, field
from typing import NamedTuple

from ..data_classes.osm_object_primitive import osm_object_primitive
from ..data_classes.node import Node
from ..data_classes.way import Way

@dataclass
class Relation(osm_object_primitive):
    members: list['Member'] = field(default_factory=list)

    def __post_init__(self):
        super().__init__(self.id, self.visible, self.version, self.changeset_id, self.timestamp, self.user_id, self.tags)

Member = NamedTuple("Member", [("element", Node | Way | Relation), ("role", str)])