from enum import Enum
from xml.dom import minidom
from dataclasses import dataclass



class Visibility(Enum):
    """See https://wiki.openstreetmap.org/wiki/Visibility_of_GPS_traces for values meaning."""
    IDENTIFIABLE = "identifiable"
    PUBLIC = "public"
    TRACKABLE = "trackable"
    PRIVATE = "private"

@dataclass
class GpxFile():
    id: int
    name: str
    user_id: int
    visibility: Visibility
    pending: bool
    timestamp: str
    latitude: str
    longitude: str
    description: str
    tags: list[str]

    def __str__(self):
        temp = f"{self.__class__.__name__}("
        for k in self.__dict__:
            temp += f"{k} = {getattr(self, k)}, "
        temp += ")"
        return temp
    
    def _to_xml(self) -> minidom.Element:
        root = minidom.Document()
        gpx_file = root.createElement("gpx_file")
        gpx_file.setAttribute("id", str(self.id))
        gpx_file.setAttribute("name", self.name)
        gpx_file.setAttribute("uid", str(self.user_id))
        gpx_file.setAttribute("visibility", self.visibility.value)
        gpx_file.setAttribute("pending", str.lower(str(self.pending)))
        gpx_file.setAttribute("timestamp", self.timestamp)
        gpx_file.setAttribute("lat", self.latitude)
        gpx_file.setAttribute("lon", self.longitude)
        
        description = root.createElement("description")
        description_text_node = root.createTextNode(self.description)
        description.appendChild(description_text_node)
        gpx_file.appendChild(description)

        for tag in self.tags:
            tag_node = root.createElement("tag")
            tag_text_node = root.createTextNode(tag)
            tag_node.appendChild(tag_text_node)
            gpx_file.appendChild(tag_node)

        return gpx_file