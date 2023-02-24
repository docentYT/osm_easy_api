from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from api import Api



class Changeset_Discussion_Container:
    def __init__(self, outer):
        self.outer: "Api" = outer