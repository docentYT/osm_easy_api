from dataclasses import dataclass, field
from xml.dom import minidom
from copy import copy

from ..data_classes.tags import Tags

@dataclass
class osm_object_primitive():
    id: int | None = None
    visible: bool | None = None
    version: int | None = None
    changeset_id: int | None = None
    timestamp: str | None = None
    user_id: int | None = None
    tags: Tags = field(default_factory=Tags)

    def __str__(self):
        temp = f"{self.__class__.__name__}("
        for k in self.__dict__:
            temp += f"{k} = {getattr(self, k)}, "
        temp += ")"
        return temp

    def _to_xml(self, changeset_id, member_version=False, role="") -> minidom.Element:
        name = self.__class__.__name__.lower()
        root = minidom.Document()
        if member_version:
            element = root.createElement("member")
            element.setAttribute("type", name)
            element.setAttribute("ref", str(self.id))
            element.setAttribute("role", role)
            return element
        else:
            element = root.createElement(name)
            element.setAttribute("id",          str(self.id))
            element.setAttribute("version",     str(self.version))
            element.setAttribute("changeset",   str(changeset_id))
            return element
        
    def _to_dict(self):
        return_dict = copy(self.__dict__)
        return_dict.update({"type": self.__class__.__name__})
        return return_dict
    
    @classmethod
    def _from_dict(cls, dict):
        node = cls()
        dict.pop("type")
        node.__dict__ = copy(dict)
        return node