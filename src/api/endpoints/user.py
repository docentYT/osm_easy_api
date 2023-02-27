from typing import TYPE_CHECKING, Generator, Tuple
if TYPE_CHECKING:
    from xml.etree import ElementTree
    from api import Api

from src.api import exceptions
from src.data_classes import User

from copy import deepcopy
from xml.dom import minidom

class User_Container:
    def __init__(self, outer):
        self.outer: "Api" = outer

    @staticmethod
    def _xml_to_user(generator: Generator[Tuple[str, 'ElementTree.Element'], None, None]) -> list[User]:
        user_list = []
        temp_user = User()
        for event, element in generator:
            if event == "start":
                match element.tag:
                    case "user":
                        temp_user = User(id=int(element.attrib["id"]), display_name=element.attrib["display_name"], account_created_at=element.attrib["account_created"])
                    case "description":
                        temp_user.description = element.text
                    case "contributor-terms":
                        temp_user.contributor_terms_agreed = bool(element.attrib["agreed"])
                    case "img":
                        temp_user.img_url = element.attrib["href"]
                    case "roles":
                        temp_user.roles = []
                        for role in element:
                            temp_user.roles.append(role.tag)
                    case "changesets":
                        temp_user.changesets_count = int(element.attrib["count"])
                    case "traces":
                        temp_user.traces_count = int(element.attrib["count"])
                    case "blocks":
                        for block_type in element:
                            temp_user.blocks = {"received": {"count": 0, "active": 0}, "issued": {"count": 0, "active": 0}}
                            if block_type.tag == "received":
                                temp_user.blocks["received"]["count"] = int(block_type.attrib["count"])
                                temp_user.blocks["received"]["active"] = int(block_type.attrib["active"])
                            elif block_type.tag == "issued":
                                temp_user.blocks["issued"]["count"] = int(block_type.attrib["count"])
                                temp_user.blocks["issued"]["active"] = int(block_type.attrib["active"])

            elif element.tag == "user":
                user_list.append(deepcopy(temp_user)) 

        if (len(user_list) == 0): raise exceptions.EmptyResult()
        return user_list

    def get(self, id: int) -> User:
        """Get user data by id.

        Args:
            id (int): User id.

        Returns:
            User: User object.
        """
        generator = self.outer._get_generator(
            url=self.outer._url.user["get"].format(id=id),
            auth_requirement=self.outer._Requirement.NO,
            auto_status_code_handling=True)
        
        return self._xml_to_user(generator)[0]
    
    def get_query(self, ids: list[int]) -> list[User]:
        """Search for multiple users on one call.

        Args:
            ids (list[int]): List of users ids.

        Returns:
            list[User]: List of User objects.
        """
        param = ""
        for id in ids:
            param += f"{id},"
        param = param[:-1]
        generator = self.outer._get_generator(
            url=self.outer._url.user["get_query"] + param,
            auth_requirement=self.outer._Requirement.NO,
            auto_status_code_handling=True)
        
        return self._xml_to_user(generator)
    
    def get_current(self) -> User:
        """Get User object for current authenticated user.

        Returns:
            User: User object.
        """
        generator = self.outer._get_generator(
            url=self.outer._url.user["get_current"],
            auth_requirement=self.outer._Requirement.YES,
            auto_status_code_handling=True)
        
        return self._xml_to_user(generator)[0]
    
    def get_preferences(self, key: str | None = None) -> dict[str, str]:
        """Get preferences for current logged user.

        Args:
            key (str | None, optional): Key to search for. Defaults to None (Returns all preferences).

        Raises:
            ValueError: Preference not found if key was provided

        Returns:
            dict[str, str]: Dictionary of preferences
        """
        url = self.outer._url.user["preferences"]
        if key:
            url += f"/{key}"
            response = self.outer._request(self.outer._RequestMethods.GET, url, self.outer._Requirement.YES, auto_status_code_handling=False)
            match response.status_code:
                case 200: pass
                case 404: raise ValueError("Preference not found")
            return {key: response.text}
        generator = self.outer._get_generator(
            url=url,
            auth_requirement=self.outer._Requirement.YES,
            auto_status_code_handling=True)
        
        preferences = {}
        for event, element in generator:
            if event == "start" and element.tag == "preference":
                preferences.update({element.attrib["k"]: element.attrib["v"]})
        return preferences
    
    def set_preferences(self, preferences: dict[str, str]) -> None:
        """Changes all preferences to new dict.

        Args:
            preferences (dict[str, str]): New preferences.
        """
        root = minidom.Document()
        preferences_element = root.createElement("preferences")
        for preference in preferences:
            temp = root.createElement("preference")
            temp.setAttribute("k", preference)
            temp.setAttribute("v", preferences[preference])
            preferences_element.appendChild(temp)
        root.appendChild(preferences_element)
        xml_str = root.toprettyxml(indent="\t")

        self.outer._request(self.outer._RequestMethods.PUT, self.outer._url.user["preferences"], self.outer._Requirement.YES, stream=True, body=xml_str)
        
    def delete_preference(self, key: str) -> None:
        """Deletes only one preference with given key.

        Args:
            key (str): Key to delete.

        Raises:
            ValueError: Preference not found.
        """
        url = self.outer._url.user["preferences"]
        url += f"/{key}"
        response = self.outer._request(self.outer._RequestMethods.DELETE, url, self.outer._Requirement.YES, auto_status_code_handling=False)
        match response.status_code:
            case 200: pass
            case 404: raise ValueError("Preference not found")