from enum import Enum
from xml.dom import minidom
from collections import namedtuple
from typing import NamedTuple

from ..data_classes.node import Node
from ..data_classes.way import Way
from ..data_classes.relation import Relation

Meta = NamedTuple("Meta", [("version", str), ("generator", str), ("sequence_number", str)])
Meta.__doc__ = """\
    Namedtuple, which stores information about OsmChange.
    """

class Action(Enum):
    """Enum that represents the actions performed on an element in a given OsmChange."""
    CREATE = 0
    MODIFY = 1
    DELETE = 2
    NONE = 3

class OsmChange():
    meta: Meta
    elements: dict

    def __init__(self, version: str, generator: str, sequence_number: str):
        self.meta = Meta(version, generator, sequence_number)
        self.elements = {
            Node: {Action.CREATE: [], Action.MODIFY: [], Action.DELETE: [], Action.NONE: []},
            Way: {Action.CREATE: [], Action.MODIFY: [], Action.DELETE: [], Action.NONE: []},
            Relation: {Action.CREATE: [], Action.MODIFY: [], Action.DELETE: [], Action.NONE: []}}

    def __str__(self):
        temp = f"OsmChange(version={self.meta.version}, generator={self.meta.generator}, sequence_number={self.meta.sequence_number}. "
        temp += f"Node: Create({len(self.elements[Node][Action.CREATE])}), "
        temp += f"Modify({len(self.elements[Node][Action.MODIFY])}), "
        temp += f"Delete({len(self.elements[Node][Action.DELETE])}), "
        temp += f"None({len(self.elements[Node][Action.NONE])}). "

        temp += f"Way: Create({len(self.elements[Way][Action.CREATE])}), "
        temp += f"Modify({len(self.elements[Way][Action.MODIFY])}), "
        temp += f"Delete({len(self.elements[Way][Action.DELETE])}), "
        temp += f"None({len(self.elements[Way][Action.NONE])}). "

        temp += f"Relation: Create({len(self.elements[Relation][Action.CREATE])}), "
        temp += f"Modify({len(self.elements[Relation][Action.MODIFY])}), "
        temp += f"Delete({len(self.elements[Relation][Action.DELETE])}), "
        temp += f"None({len(self.elements[Relation][Action.NONE])})."
        return temp

    def _to_xml(self, changeset_id):
        root = minidom.Document()
        xml = root.createElement("osmChange")
        xml.setAttribute("version", self.meta.version)
        xml.setAttribute("generator", self.meta.generator)
        root.appendChild(xml)

        def append_elements_to_master_element(master_name, elements):
            if not elements: return
            master = root.createElement(master_name)
            for element in elements:
                master.appendChild(element._to_xml(changeset_id))
            xml.appendChild(master)
            
        append_elements_to_master_element("create", self.get(Node, Action.CREATE))
        append_elements_to_master_element("modify", self.get(Node, Action.MODIFY))
        append_elements_to_master_element("delete", self.get(Node, Action.DELETE))

        append_elements_to_master_element("create", self.get(Way, Action.CREATE))
        append_elements_to_master_element("modify", self.get(Way, Action.MODIFY))
        append_elements_to_master_element("delete", self.get(Way, Action.DELETE))

        append_elements_to_master_element("create", self.get(Relation, Action.CREATE))
        append_elements_to_master_element("modify", self.get(Relation, Action.MODIFY))
        append_elements_to_master_element("delete", self.get(Relation, Action.DELETE))

        xml_str = root.toprettyxml(indent="\t")
        return xml_str

    def get(self, type: type[Node | Way | Relation], action: Action = Action.NONE) -> list[Node | Way | Relation]:
        """Gets list of elements with provided type and action.

        Args:
            type (type[Node | Way | Relation]): Object type to return.
            action (Action, optional): Defaults to Action.NONE.

        Returns:
            list[Node | Way | Relation]: List of elements.
        """
        return self.elements[type][action]

    def add(self, object: Node | Way | Relation, action: Action = Action.NONE):
        self.elements[type(object)][action].append(object)

    def remove(self, object: Node | Way | Relation, action: Action = Action.NONE):
        self.elements[type(object)][action].remove(object)