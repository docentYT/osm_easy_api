from dataclasses import dataclass
from xml.dom import minidom

from ..data_classes.osm_object_primitive import osm_object_primitive

@dataclass
class Node(osm_object_primitive):
    latitude: str | None = None   # str to prevent rounding values
    longitude: str | None = None

    def __post_init__(self):
        super().__init__(self.id, self.visible, self.version, self.changeset_id, self.timestamp, self.user_id, self.tags)

    def _to_xml(self, changeset_id, way_version = False, member_version = False, role=""):
        if way_version:
            root = minidom.Document()
            element = root.createElement("nd")
            element.setAttribute("ref", str(self.id))
            return element
        elif member_version:
            return super()._to_xml(changeset_id, member_version, role)
        else:
            element = super()._to_xml(changeset_id)
            element.setAttribute("lat",    str(self.latitude))
            element.setAttribute("lon",   str(self.longitude))

            for tag in self.tags._to_xml():
                element.appendChild(tag)
            return element