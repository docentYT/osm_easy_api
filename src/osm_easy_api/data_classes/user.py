from dataclasses import dataclass
from copy import copy
from typing import Dict

@dataclass
class User():
    id: int | None = None
    display_name: str | None = None
    account_created_at: str | None = None
    description: str | None = None
    contributor_terms_agreed: bool | None = None
    img_url: str | None = None
    roles: list[str] | None = None
    changesets_count: int | None = None
    traces_count: int | None = None
    blocks: Dict[str, Dict[str, int]] | None = None
    # = {
    #     "received": {
    #         "count": 0,
    #         "active": 0
    #     },
    #     "issued": {
    #         "count": 0,
    #         "active": 0
    #     }
    # }

    def __str__(self):
        temp = f"{self.__class__.__name__}("
        for k in self.__dict__:
            temp += f"{k} = {getattr(self, k)}, "
        temp += ")"
        return temp
        
    def to_dict(self) -> dict[str, str]:
        """Returns a dictionary that corresponds to the attributes of the user. In addition, a 'type':'user' is added.

        Returns:
            dict[str, str]: A dictionary that represents an user.
        """
        return_dict = copy(self.__dict__)
        return_dict.update({"type": self.__class__.__name__})
        return return_dict

    @classmethod
    def from_dict(cls, dict: dict[str, str]):
        """Creates an user from the data presented in the dictionary generated by the to_dict() method.

        Args:
            dict (dict[str, str]): Dictionary generated by the to_dict() method.

        Returns:
            User: The user object.
        """
        if not dict.get("type"): 
            raise ValueError("No type key in the dictionary!")
        if dict["type"] != cls.__name__:
            raise ValueError(f'You used incorrect class to create object from given dictionary. Use {dict["type"]}.from_dict() instead of {cls.__name__}.from_dict()')
        user = cls()
        temp_dict = copy(dict)
        temp_dict.pop("type")
        user.__dict__ = temp_dict
        return user