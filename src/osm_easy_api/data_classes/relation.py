from dataclasses import dataclass, field
from typing import NamedTuple
from copy import copy

from ..data_classes.osm_object_primitive import osm_object_primitive
from ..data_classes import Node, Way


_RELATION_DICTIONARY_TYPE = dict[str, str | list["_MEMBER_DICTIONARY_TYPE"]]
_MEMBER_DICTIONARY_TYPE = dict[str, str | dict[str, str | list[dict[str, str]]] | _RELATION_DICTIONARY_TYPE]

@dataclass
class Relation(osm_object_primitive):
    members: list['Member'] = field(default_factory=list)

    def __post_init__(self):
        super().__init__(self.id, self.visible, self.version, self.changeset_id, self.timestamp, self.user_id, self.tags)

    def _to_xml(self, changeset_id, member_version=False, role=""):
        if member_version:
            return super()._to_xml(changeset_id, member_version=member_version, role=role)
        else:
            element = super()._to_xml(changeset_id)
            for tag in self.tags._to_xml():
                element.appendChild(tag)
            
            for member, role in self.members:
                element.appendChild(member._to_xml(changeset_id=changeset_id, member_version=True, role=role))

            return element
        
    def to_dict(self) -> dict[str, str | list[_MEMBER_DICTIONARY_TYPE]]:
        super_dict: dict[str, str | list[_MEMBER_DICTIONARY_TYPE]] = super().to_dict() # type: ignore
        members: list[_MEMBER_DICTIONARY_TYPE] = []
        for member in self.members:
            members.append(member.to_dict())
        super_dict["members"] = members
        return super_dict
    
    @classmethod
    def from_dict(cls, dict: dict[str, str | list[_MEMBER_DICTIONARY_TYPE]]):
        temp_dict = copy(dict)
        relation = super().from_dict(temp_dict) # type: ignore
        members = copy(dict["members"])
        relation.members.clear()
        for member in members:
            relation.members.append(Member.from_dict(member))
        return relation

class Member(NamedTuple("Member", [("element", Node | Way | Relation), ("role", str)])):
    def to_dict(self) -> _MEMBER_DICTIONARY_TYPE:
        return {"element": self.element.to_dict(), "role": self.role, "type": "Member"}
    
    @classmethod
    def from_dict(cls, dict) -> "Member":
        if not dict.get("type"): 
            raise ValueError("No type key in the dictionary!")
        match dict["element"]["type"]:
            case "Node": return cls(Node.from_dict(dict["element"]), dict["role"])
            case "Way": return cls(Way.from_dict(dict["element"]), dict["role"])
            case "Relation": return cls(Relation.from_dict(dict["element"]), dict["role"])
            case _: raise ValueError(f'{dict["type"]} not supported for relation member.') 