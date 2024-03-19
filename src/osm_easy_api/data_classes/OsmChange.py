from enum import Enum
from xml.dom import minidom
from collections import namedtuple
from typing import NamedTuple
from copy import deepcopy

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

    @property
    def _current_negative_id(self):
        self.__current_negative_id -= 1
        return self.__current_negative_id
    
    @_current_negative_id.setter
    def _current_negative_id(self, value):
        self.__current_negative_id = value

    def __init__(self, version: str, generator: str, sequence_number: str):
        self.meta = Meta(version, generator, sequence_number)
        self.elements = {
            Node: {Action.CREATE: [], Action.MODIFY: [], Action.DELETE: [], Action.NONE: []},
            Way: {Action.CREATE: [], Action.MODIFY: [], Action.DELETE: [], Action.NONE: []},
            Relation: {Action.CREATE: [], Action.MODIFY: [], Action.DELETE: [], Action.NONE: []}}
        self._current_negative_id = 0

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
    
    @staticmethod
    def _make_osmChange_valid(osmChange: 'OsmChange'):
        def fix_negative_or_none_version_and_id(type):
            for element in osmChange.get(type, Action.CREATE):
                if element.id is None or element.id < 0:
                    if element.version is None:
                        element.version = 1
                    element.id = osmChange._current_negative_id

        fix_negative_or_none_version_and_id(Node)
        fix_negative_or_none_version_and_id(Way)
        fix_negative_or_none_version_and_id(Relation)

        def add_relation_members_with_negative_ids(action: Action):
            for relation in osmChange.get(Relation, action):
                for member in relation.members:
                    member_id = member.element.id
                    if member_id is None or member_id < 0:
                        member.element.id = osmChange._current_negative_id
                        elements = osmChange.get(type(member.element), Action.CREATE)
                        for element in elements:
                            if element == member:
                                elements.remove(element)
                                break
                        osmChange.add(member.element, Action.CREATE)

        add_relation_members_with_negative_ids(Action.CREATE)
        add_relation_members_with_negative_ids(Action.MODIFY)

        def add_way_nodes_with_negative_ids(action: Action):
            for way in osmChange.get(Way, action):
                for node in way.nodes:
                    node_id = node.id
                    if node_id is None or node_id < 0:
                        node.id = osmChange._current_negative_id
                        elements = osmChange.get(Node, Action.CREATE)
                        for element in elements:
                            if element == node:
                                elements.remove(element)
                                break
                        osmChange.add(node, Action.CREATE)
        
        add_way_nodes_with_negative_ids(Action.CREATE)
        add_way_nodes_with_negative_ids(Action.MODIFY)

    def to_xml(self, changeset_id: int = -1, make_osmChange_valid: bool = True, work_on_copy: bool = False) -> str:
        """Returns xml string in OsmChange format.

        Args:
            changeset_id (int): Changeset id to be added to the elements. External programmes (like JOSM) when sending changes will probably complete this field themselves. Defaults to -1.
            make_osmChange_valid (bool, optional): Modifies the OsmChange object to comply with the standard. Defaults to True.
            work_on_copy (bool, optional): Creates a copy of the OsmChange object and makes a change on it if make_osmChange_valid is True. Memory-intensive and not recommended, especially since python operates on references. Defaults to False.

        Returns:
            str: xml string.
        """
        osmChange = self
        if work_on_copy: osmChange = deepcopy(self)
        if make_osmChange_valid: OsmChange._make_osmChange_valid(osmChange)

        return OsmChange._to_xml(osmChange, changeset_id)

    @staticmethod
    def _to_xml(osmChange: 'OsmChange', changeset_id):
        root = minidom.Document()
        xml = root.createElement("osmChange")
        xml.setAttribute("version", osmChange.meta.version)
        xml.setAttribute("generator", osmChange.meta.generator)
        root.appendChild(xml)

        def append_elements_to_master_element(master_name, elements):
            if not elements: return
            master = root.createElement(master_name)
            for element in elements:
                master.appendChild(element._to_xml(changeset_id))
            xml.appendChild(master)
            
        append_elements_to_master_element("create", osmChange.get(Node, Action.CREATE))
        append_elements_to_master_element("modify", osmChange.get(Node, Action.MODIFY))
        append_elements_to_master_element("delete", osmChange.get(Node, Action.DELETE))

        append_elements_to_master_element("create", osmChange.get(Way, Action.CREATE))
        append_elements_to_master_element("modify", osmChange.get(Way, Action.MODIFY))
        append_elements_to_master_element("delete", osmChange.get(Way, Action.DELETE))

        append_elements_to_master_element("create", osmChange.get(Relation, Action.CREATE))
        append_elements_to_master_element("modify", osmChange.get(Relation, Action.MODIFY))
        append_elements_to_master_element("delete", osmChange.get(Relation, Action.DELETE))

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