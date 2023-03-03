from xml.etree import ElementTree
from typing import Generator
import gzip # for typing

from ..data_classes import Node, Way, Relation, OsmChange, Action, Tags
from ..data_classes.relation import Member
from ..data_classes.OsmChange import Meta

def _string_to_action(string: str) -> Action:
    """Returns Action from string name.

    Args:
        string (str): "create" | "modify" | "delete"

    Returns:
        Action: If no match found returns Action.NONE.
    """
    match string:
        case "create": return Action.CREATE
        case "modify": return Action.MODIFY
        case "delete": return Action.DELETE

        case _: return Action.NONE

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


def _if_correct(element: ElementTree.Element, tags: Tags | str) -> bool:
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
        good_tags_count = 0
        for tag in element:
            if tag.tag != "tag": continue
            if tag.attrib["k"] in tags and tag.attrib["v"] == tags[tag.attrib["k"]]: #type: ignore (We already checked if type(tags)==Tags)
                good_tags_count += 1
        return good_tags_count == len(tags)
    
    raise ValueError("[ERROR::DIFF_PARSER::_IF_CORRECT] Unexpected return.")

    # good_tags_count = 0
    # for tag in element:
    #     if tag.tag != "tag": continue
    #     if type(tags) == Tags and tag.attrib["k"] in tags and tag.attrib["v"] == tags[tag.attrib["k"]]:
    #         good_tags_count += 1
    #     elif type(tags) == str:
    #         if tag.attrib["k"] == tags:
    #             return True
    # return good_tags_count == len(tags)

def _create_node_from_attributes(attributes: dict) -> Node:
    visible = None
    if attributes.get("visible"):
        visible = True if attributes["visible"] == "true" else False
    return Node(
        id =            int(    attributes["id"]        ),
        visible =       visible,
        version =       int(    attributes["version"]   ),
        timestamp =     str(    attributes["timestamp"] ),
        user_id =       int(    attributes["uid"]       ),
        changeset_id =  int(    attributes["changeset"] ),
        latitude =      str(    attributes.get("lat")   ),
        longitude =     str(    attributes.get("lon")   )
    )

def _create_way_from_attributes(attributes: dict) -> Way:
    visible = None
    if attributes.get("visible"):
        visible = True if attributes["visible"] == "true" else False
    return Way(
        id              = int(  attributes["id"]        ),
        visible =       visible,
        version         = int(  attributes["version"]   ),
        timestamp       = str(  attributes["timestamp"] ),
        user_id         = int(  attributes["uid"]       ),
        changeset_id    = int(  attributes["changeset"] )
    )

def _create_relation_from_attributes(attributes: dict) -> Relation:
    visible = None
    if attributes.get("visible"):
        visible = True if attributes["visible"] == "true" else False
    return Relation(
        id              = int(  attributes["id"]        ),
        visible =       visible,
        version         = int(  attributes["version"]   ),
        timestamp       = str(  attributes["timestamp"] ),
        user_id         = int(  attributes["uid"]       ),
        changeset_id    = int(  attributes["changeset"] )
    )

def _element_to_osm_object(element: ElementTree.Element) -> Node | Way | Relation:
    def append_tags(element: ElementTree.Element, append_to: Node | Way | Relation):
        for tag in element:
                    if tag.tag == "tag": append_to.tags.add(tag.attrib["k"], tag.attrib["v"])
    match element.tag:
        case "node": 
            node = _create_node_from_attributes(element.attrib)
            append_tags(element, node)
            return node
        case "way": 
            way = _create_way_from_attributes(element.attrib)
            _add_nodes_to_way_from_element(way, element)
            append_tags(element, way)
            return way
        case "relation":
            relation = _create_relation_from_attributes(element.attrib)
            _add_members_to_relation_from_element(relation, element)
            append_tags(element, relation)
            return relation
        case _: raise ValueError("[ERROR::DIFF_PARSER::_ELEMENT_TO_OSM_OBJECT] Unkown element tag:", element.tag)

def OsmChange_parser_generator(file: gzip.GzipFile, sequence_number: str | None, required_tags: Tags | str = Tags()) -> Generator[tuple[Action, Node | Way | Relation] | Meta, None, None]:
    """Generator with elements in diff file. First yield will be Meta namedtuple.

    Args:
        file (gzip.GzipFile): File (stream) to parse.
        sequence_number (str): Sequence number for Meta namedtuple.
        required_tags (Tags | str, optional): Useful if you want to prefetch specific tags. Other tags will be ignored.

    Yields:
        Generator[Meta | Node | Way | Relation, None, None]: First yield will be Meta namedtuple with data about diff. Next yields will be osm data classes.
    """
    action_string = ""
    try:
        file.seek(0)
    except: pass
    iterator = ElementTree.iterparse(file, events=('start', 'end'))
    _, root = next(iterator)
    yield Meta(version=root.attrib["version"], generator=root.attrib["generator"], sequence_number=sequence_number or "")
    for event, element in iterator:
        if element.tag in ("modify", "create", "delete") and event=="start": 
            action_string = element.tag
        elif element.tag in ("node", "way", "relation"):
            if not element.attrib: continue

            if (_if_correct(element, required_tags)):
                node_way_relation = _element_to_osm_object(element)
                assert node_way_relation, "[ERROR::DIFF_PARSER::OSMCHANGE_PARSER_GENERATOR] node_way_relation is equal to None!"
                
                # for tag in element:
                #     if tag.tag == "tag": node_way_relation.tags.add(tag.attrib["k"], tag.attrib["v"])

                action = _string_to_action(action_string)
                yield(action, node_way_relation)
        element.clear()

def OsmChange_parser(file: gzip.GzipFile, sequence_number: str | None, required_tags: Tags | str = Tags()) -> OsmChange:
    """Creates OsmChange object from generator.

    Args:
        file (gzip.GzipFile): File (stream) to parse.
        sequence_number (str): Sequence number for Meta in osmChange object.
        required_tags (Tags | str, optional): Useful if you want to prefetch specific tags. Other tags will be ignored.

    Returns:
        OsmChange: osmChange object.
    """
    gen = OsmChange_parser_generator(file, sequence_number, required_tags)
    # FIXME: Maybe OsmChange_parser_generator should return tuple(Meta, gen)? EDIT: I think Meta should be generated somewhere else
    meta = next(gen)
    assert type(meta) == Meta, "[ERROR::DIFF_PARSER::OSMCHANGE_PARSER] meta type is not equal to Meta."
    osmChange = OsmChange(meta.version, meta.generator, meta.sequence_number) # type: ignore
    for action, element in gen: # type: ignore (Next gen elements must be proper tuple type.)
        assert type(action) == Action, "[ERROR::DIFF_PARSER::OSMCHANGE_PARSER] action type is not equal to Action."
        osmChange.add(element, action)  # type: ignore (I just created assert for it, didn't I?)
    return osmChange