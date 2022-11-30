from dataclasses import dataclass, field

from ..data_classes.tags import Tags

@dataclass
class osm_object_primitive():
    id: int | None = None
    visible: bool | None = None
    version: int | None = None
    changeset_id: int | None = None
    timestamp: str | None = None
    user_id: int | None = None
    tags: Tags = field(default_factory=Tags)

    def __str__(self):
        temp = f"{self.__class__.__name__}("
        for k in self.__dict__:
            temp += f"{k} = {getattr(self, k)}, "
        temp += ")"
        return temp