from dataclasses import dataclass, field
from copy import copy

from ..data_classes.osm_object_primitive import osm_object_primitive
from ..data_classes.node import Node

@dataclass
class Way(osm_object_primitive):
    nodes: list[Node] = field(default_factory=list)

    def __post_init__(self):
        super().__init__(self.id, self.visible, self.version, self.changeset_id, self.timestamp, self.user_id, self.tags)

    def _to_xml(self, changeset_id, member_version=False, role=""):
        if member_version:
            return super()._to_xml(changeset_id, member_version=member_version, role=role)
        else:
            element = super()._to_xml(changeset_id)
            for tag in self.tags._to_xml():
                element.appendChild(tag)
                
            for node in self.nodes:
                node_element = node._to_xml(changeset_id, way_version=True)
                element.appendChild(node_element)
            return element
        
    def to_dict(self) -> dict[str, str | list[dict[str, str]]]:
        super_dict: dict[str, str | list[dict[str, str]]] = super().to_dict() # type: ignore
        nodes: list[dict[str, str]] = []
        for node in self.nodes:
            nodes.append(node.to_dict())
        super_dict["nodes"] = nodes
        return super_dict
    
    @classmethod
    def from_dict(cls, dict: dict[str, str | list[dict[str, str]]]):
        temp_dict = copy(dict)
        way = super().from_dict(temp_dict) # type: ignore (ignoring list of nodes)
        nodes = copy(dict["nodes"])
        way.nodes.clear()
        for node in nodes:
            way.nodes.append(Node.from_dict(node)) # type: ignore
        return way