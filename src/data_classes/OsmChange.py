from enum import Enum
from collections import namedtuple
from typing import NamedTuple

from ..data_classes.node import Node
from ..data_classes.way import Way
from ..data_classes.relation import Relation

Meta = NamedTuple("Meta", [("version", str), ("generator", str), ("sequence_number", str)])

class Action(Enum):
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