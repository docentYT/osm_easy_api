from xml.etree import ElementTree
from typing import Generator, cast, TYPE_CHECKING
if TYPE_CHECKING:
    import gzip

from ..data_classes import Node, Way, Relation, OsmChange, Action, Tags
from ..data_classes.OsmChange import Meta
from ..utils import element_to_osm_object

STRING_TO_ACTION = {
    "create": Action.CREATE,
    "modify": Action.MODIFY,
    "delete": Action.DELETE
}

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
    
    assert False, ValueError("[ERROR::DIFF_PARSER::_IS_CORRECT] Unexpected return.") # pragma: no cover

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
            osmObject = element_to_osm_object(element)
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
    assert isinstance(meta, Meta), "[ERROR::DIFF_PARSER::OSMCHANGE_PARSER] meta type is not equal to Meta." # pragma: no cover
    osmChange = OsmChange(meta.version, meta.generator, meta.sequence_number)
    for action, element in gen: # type: ignore (Next gen elements must be proper tuple type.)
        element = cast(Node | Way | Relation, element)
        action = cast(Action, action)
        osmChange.add(element, action)
    return osmChange
