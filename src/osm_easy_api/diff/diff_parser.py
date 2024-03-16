from xml.etree import ElementTree
from typing import Generator, cast, TYPE_CHECKING, TypeVar, Type
if TYPE_CHECKING:
    import gzip

from ..data_classes import Node, Way, Relation, OsmChange, Action, Tags
from ..data_classes.relation import Member
from ..data_classes.OsmChange import Meta

STRING_TO_ACTION = {
    "create": Action.CREATE,
    "modify": Action.MODIFY,
    "delete": Action.DELETE
}

def _add_members_to_relation_from_element(relation: Relation, element: ElementTree.Element) -> None:
    def _append_member(relation: Relation, type: type[Node | Way | Relation], member_attrib: dict) -> None:
        relation.members.append(Member(type(id=int(member_attrib["ref"])), member_attrib["role"]))

    for member in element:
        if member.tag == "member":
            match member.attrib["type"]:
                case "node":        _append_member(relation, Node,      member.attrib)
                case "way":         _append_member(relation, Way,       member.attrib)
                case "relation":    _append_member(relation, Relation,  member.attrib)

def _add_nodes_to_way_from_element(way: Way, element: ElementTree.Element) -> None:
    for nd in element:
        if nd.tag == "nd":
            way.nodes.append(Node(id=int(nd.attrib["ref"])))


def _is_correct(element: ElementTree.Element, tags: Tags | str) -> bool:
    """Checks if provided element has all required tags.

    Args:
        element (ElementTree.Element): Element to look tags in.
        tags (Tags | str): Required tags or required tag key.

    Returns:
        bool: True if element has required tags. False otherwise.
    """
    if not tags: return True

    if type(tags) == str:
        for tag in element:
            if tag.tag != "tag": continue
            if tag.attrib["k"] == tags: return True
        return False
    elif type(tags) == Tags:
        matching_tags_counter = 0
        for tag in element:
            if tag.tag != "tag": continue
            if tag.attrib["k"] in tags and tag.attrib["v"] == tags[tag.attrib["k"]]:
                matching_tags_counter += 1
        return matching_tags_counter == len(tags)
    
    raise ValueError("[ERROR::DIFF_PARSER::_IS_CORRECT] Unexpected return.")


Node_Way_Relation = TypeVar("Node_Way_Relation", Node, Way, Relation)
def _create_osm_object_from_attributes(elementType: Type[Node_Way_Relation], attributes: dict) -> Node_Way_Relation:

    id = int(attributes["id"])
    visible = None
    if attributes.get("visible"):
        visible = True if attributes["visible"] == "true" else False
    version = int(attributes["version"])
    timestamp = str(attributes["timestamp"])
    user_id = int(attributes.get("uid", -1))
    changeset_id = int(attributes["changeset"])

    element = elementType(id=id, visible=visible, version=version, timestamp=timestamp, user_id=user_id, changeset_id=changeset_id)

    if type(element) == Node:
        element.latitude = str(attributes.get("lat"))
        element.longitude = str(attributes.get("lon"))

    return element

def _element_to_osm_object(element: ElementTree.Element) -> Node | Way | Relation:
    def append_tags(element: ElementTree.Element, append_to: Node | Way | Relation):
        for tag in element:
                    if tag.tag == "tag": append_to.tags.add(tag.attrib["k"], tag.attrib["v"])

    osmObject = None
    match element.tag:
        case "node":
            osmObject = _create_osm_object_from_attributes(Node, element.attrib)
        case "way": 
            osmObject = _create_osm_object_from_attributes(Way, element.attrib)
            _add_nodes_to_way_from_element(osmObject, element)
        case "relation":
            osmObject = _create_osm_object_from_attributes(Relation, element.attrib)
            _add_members_to_relation_from_element(osmObject, element)
        case _: assert False, f"[ERROR::DIFF_PARSER::_ELEMENT_TO_OSM_OBJECT] Unknown element tag: {element.tag}"

    append_tags(element, osmObject)
    return osmObject

def _OsmChange_parser_generator(file: "gzip.GzipFile", sequence_number: str | None, required_tags: Tags | str = Tags()) -> Generator[tuple[Action, Node | Way | Relation] | Meta, None, None]:
    """Generator with elements in diff file. First yield will be Meta namedtuple.

    Args:
        file (gzip.GzipFile): File (stream) to parse.
        sequence_number (str): Sequence number for Meta namedtuple.
        required_tags (Tags | str, optional): Useful if you want to prefetch specific tags. Other tags will be ignored.

    Yields:
        Generator[tuple[Action, Node | Way | Relation] | Meta, None, None]: First yield will be Meta namedtuple with data about diff. Next yields will be osm data classes.
    """
    action: Action = Action.NONE
    try:
        file.seek(0)
    except: pass
    iterator = ElementTree.iterparse(file, events=['start'])
    _, root = next(iterator)
    yield Meta(version=root.attrib["version"], generator=root.attrib["generator"], sequence_number=sequence_number or "")
    for event, element in iterator:
        if element.tag in ("modify", "create", "delete"): 
            action = STRING_TO_ACTION.get(element.tag, Action.NONE)
        elif element.tag in ("node", "way", "relation") and _is_correct(element, required_tags):
            osmObject = _element_to_osm_object(element)
            yield(action, osmObject)
        element.clear()

def _OsmChange_parser(file: "gzip.GzipFile", sequence_number: str | None, required_tags: Tags | str = Tags()) -> OsmChange:
    """Creates OsmChange object from generator.

    Args:
        file (gzip.GzipFile): File (stream) to parse.
        sequence_number (str): Sequence number for Meta in osmChange object.
        required_tags (Tags | str, optional): Useful if you want to prefetch specific tags. Other tags will be ignored.

    Returns:
        OsmChange: osmChange object.
    """
    gen = _OsmChange_parser_generator(file, sequence_number, required_tags)
    # FIXME: Maybe OsmChange_parser_generator should return tuple(Meta, gen)? EDIT: I think Meta should be generated somewhere else
    meta = next(gen)
    assert type(meta) == Meta, "[ERROR::DIFF_PARSER::OSMCHANGE_PARSER] meta type is not equal to Meta."
    osmChange = OsmChange(meta.version, meta.generator, meta.sequence_number)
    for action, element in gen: # type: ignore (Next gen elements must be proper tuple type.)
        element = cast(Node | Way | Relation, element)
        action = cast(Action, action)
        osmChange.add(element, action)
    return osmChange
