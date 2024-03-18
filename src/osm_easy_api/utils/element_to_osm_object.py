from osm_easy_api.data_classes import Node, Way, Relation

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from xml.etree.ElementTree import Element

def element_to_osm_object(element: 'Element') -> Node | Way | Relation:
    match element.tag:
        case "node":
            return Node._from_xml(element)
        case "way": 
            return Way._from_xml(element)
        case "relation":
            return Relation._from_xml(element)
        case _: assert False, f"[ERROR::DIFF_PARSER::_ELEMENT_TO_OSM_OBJECT] Unknown element tag: {element.tag}"