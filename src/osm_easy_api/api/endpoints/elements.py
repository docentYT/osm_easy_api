from typing import TYPE_CHECKING, TypeVar
if TYPE_CHECKING: # pragma: no cover
    from ...api import Api
    from xml.etree import ElementTree

from copy import deepcopy

from ...api import exceptions
from ...data_classes import Node, Way, Relation
from ...data_classes.relation import Member
from ...diff.diff_parser import _element_to_osm_object

Node_Way_Relation = TypeVar("Node_Way_Relation", Node, Way, Relation)
Way_Relation = TypeVar("Way_Relation", Way, Relation)

class Elements_Container:
    def __init__(self, outer):
        self.outer: "Api" = outer

    def create(self, element: Node | Way | Relation, changeset_id: int) -> int:
        """Creates a new element.

        Args:
            element (Node | Way | Relation): Type of element to create.
            changeset_id (int): Id of changeset to add to.

        Raises:
            ValueError: Error when creating element (bad element data)
            exceptions.ChangesetAlreadyClosedOrUserIsNotAnAuthor: Changeset has already been closed.
            ValueError: Way has nodes that do not exist or are not visible / relation has elements that do not exist or are not visible.

        Returns:
            int: Id of new element.
        """
        element_name = element.__class__.__name__.lower()
        body = f"<osm>\n{element._to_xml(changeset_id).toprettyxml()}</osm>"
        response = self.outer._request(self.outer._RequestMethods.PUT, self.outer._url.elements["create"].format(element_type=element_name), self.outer._Requirement.YES, body=body, auto_status_code_handling=False)

        match response.status_code:
            case 200: pass
            case 400: raise ValueError(response.content)
            case 409: raise exceptions.ChangesetAlreadyClosedOrUserIsNotAnAuthor(response.content)
            case 412: raise ValueError(response.content)
            case _: assert False, f"Unexpected response status code {response.status_code}. Please report it on github."
        
        return int(response.text)

    def get(self, element: type[Node_Way_Relation], id: int) -> Node_Way_Relation :
        """""Get element by id

        Args:
            element (type[Node_Way_Relation]): Element type.
            id (int): Element id.

        Raises:
            exceptions.IdNotFoundError: Not found element with given id and type.
            exceptions.ElementDeleted: Element has been deleted. Maybe you should use elements.version() instead?

        Returns:
            Node | Way | Relation: Representation of element.
        """""
        element_name = element.__name__.lower()
        url = self.outer._url.elements["read"].format(element_type=element_name, id=id)
        status_code, generator = self.outer._get_generator(
            url=url,
            auth_requirement=self.outer._Requirement.NO,
            auto_status_code_handling=False)
        
        match status_code:
            case 200: pass
            case 404: raise exceptions.IdNotFoundError()
            case 410: raise exceptions.ElementDeleted()
            case _: assert False, f"Unexpected response status code {status_code}. Please report it on github."
        
        for event, elem in generator:
            if elem.tag in ("node", "way", "relation") and event == "start":
                object = _element_to_osm_object(elem)
                return object
            
        return object
    
    def update(self, element: Node | Way | Relation, changeset_id: int) -> int:
        """Updates data for existing element.

        Args:
            element (Node | Way | Relation): Element with updated data. Version of element must be the same as in database. Unchanged data also must be provided.
            changeset_id (int): Changeset id in which you want to update element.

        Raises:
            ValueError: Error when updating element (bad element data) 
            ValueError: Element version does not match the current database version.
            exceptions.IdNotFoundError: Cannot find element with given id.
            exceptions.IdNotFoundError: Way or relation has members/elements that do not exist or are not visible.

        Returns:
            int: _description_
        """
        element.changeset_id = changeset_id
        element_name = element.__class__.__name__.lower()
        body = f"<osm>\n{element._to_xml(element.changeset_id).toprettyxml()}</osm>"
        response = self.outer._request(self.outer._RequestMethods.PUT, self.outer._url.elements["update"].format(element_type=element_name, id=element.id), self.outer._Requirement.YES, body=body, auto_status_code_handling=False)

        match response.status_code:
            case 200: pass
            case 400: raise ValueError(response.content)
            case 409: raise ValueError(response.content)
            case 404: raise exceptions.IdNotFoundError()
            case 412: raise exceptions.IdNotFoundError(response.content)
            case _: assert False, f"Unexpected response status code {response.status_code}. Please report it on github."
        return int(response.content)
    
    def delete(self, element: Node | Way | Relation, changeset_id: int) -> int:
        """Deletes element. 

        Args:
            element (Node | Way | Relation): Element object which you want to delete. Id is not sufficient.
            changeset_id (int): Changeset id in which you want to delete element.

        Raises:
            ValueError: Error when deleting object (bad element data).
            exceptions.IdNotFoundError: Cannot find element with given id (element.id).
            exceptions.ChangesetAlreadyClosedOrUserIsNotAnAuthor: Changeset has already been closed.
            exceptions.ElementDeleted: Element has already been deleted.
            ValueError: Node is still used in way or element is still member of relation.

        Returns:
            int: New version number.
        """
        element.changeset_id = changeset_id
        element_name = element.__class__.__name__.lower()
        body = f"<osm>\n{element._to_xml(element.changeset_id).toprettyxml()}</osm>"
        response = self.outer._request(self.outer._RequestMethods.DELETE, self.outer._url.elements["delete"].format(element_type=element_name, id=element.id), self.outer._Requirement.YES, body=body, auto_status_code_handling=False)

        match response.status_code:
            case 200: pass
            case 400: raise ValueError(response.content)
            case 404: raise exceptions.IdNotFoundError()
            case 409: raise exceptions.ChangesetAlreadyClosedOrUserIsNotAnAuthor(response.content)
            case 410: raise exceptions.ElementDeleted()
            case 412: raise ValueError(response.content)
            case _: assert False, f"Unexpected response status code {response.status_code}. Please report it on github."
        return int(response.content)
    
    def history(self, element: type[Node_Way_Relation], id: int) -> list[Node_Way_Relation]:
        """Returns all old versions of element.

        Args:
            element (type[Node_Way_Relation]): Element type to search for.
            id (int): Element id.

        Raises:
            exceptions.IdNotFoundError: cannot find element with given id.

        Returns:
            list[Node | Way | Relation]: List of previous versions of element.
        """
        element_name = element.__name__.lower()
        url = self.outer._url.elements["history"].format(element_type=element_name, id=id)
        status_code, generator = self.outer._get_generator(
            url=url,
            auth_requirement=self.outer._Requirement.NO,
            auto_status_code_handling=False)
        
        match status_code:
            case 200: pass
            case 404: raise exceptions.IdNotFoundError()
            case _: assert False, f"Unexpected response status code {status_code}. Please report it on github."
        
        objects_list = []
        for event, elem in generator:
            if elem.tag == element_name and event == "start":
                objects_list.append(_element_to_osm_object(elem))
            
        return objects_list
    
    def version(self, element: type[Node_Way_Relation], id: int, version: int) -> Node_Way_Relation:
        """Returns specific version of element.

        Args:
            element (type[Node_Way_Relation]): Element type.
            id (int): Element id.
            version (int): Version number you are looking for.

        Raises:
            exceptions.IdNotFoundError: This version of the element is not available (due to redaction)
            exceptions.IdNotFoundError: Cannot find element with given id.

        Returns:
            Node | Way | Relation: _description_
        """
        element_name = element.__name__.lower()
        url = self.outer._url.elements["version"].format(element_type=element_name, id=id, version=version)
        status_code, generator = self.outer._get_generator(
            url=url,
            auth_requirement=self.outer._Requirement.NO,
            auto_status_code_handling=False)
        
        match status_code:
            case 200: pass
            case 403: raise exceptions.IdNotFoundError("This version of the element is not available (due to redaction)")
            case 404: raise exceptions.IdNotFoundError()
            case _: assert False, f"Unexpected response status code {status_code}. Please report it on github."
        
        for event, elem in generator:
            if elem.tag in ("node", "way", "relation"):
                object = _element_to_osm_object(elem)
                return object
        assert False, "[ERROR::API::ENDPOINTS::ELEMENTS::version] Cannot create an element."
    
    def get_query(self, element: type[Node_Way_Relation], ids: list[int]) -> list[Node_Way_Relation]:
        """Allows fetch multiple elements at once.

        Args:
            element (type[Node  |  Way  |  Relation]): Elements type.
            ids (list[int]): List of ids you are looking for.

        Raises:
            ValueError: Parameters missing or wrong.
            exceptions.IdNotFoundError: One of the elements could not be found.
            ValueError: Request url was too long (too many ids.)

        Returns:
            list[Node | Way | Relation]: List of elements you are looking for.
        """
        element_name = element.__name__.lower() + 's'
        param = f"?{element_name}="
        for id in ids: param += f"{id},"
        param = param[:-1]
        url = self.outer._url.elements["multi_fetch"].format(element_type=element_name) + param
        status_code, generator = self.outer._get_generator(
            url=url,
            auth_requirement=self.outer._Requirement.NO,
            auto_status_code_handling=False)
        
        match status_code:
            case 200: pass
            case 400: raise ValueError()
            case 404: raise exceptions.IdNotFoundError()
            case 414: raise ValueError("URL too long (too many ids)")
            case _: assert False, f"Unexpected response status code {status_code}. Please report it on github."
        
        objects_list = []
        for event, elem in generator:
            if elem.tag == element.__name__.lower() and event == "start":
                objects_list.append(_element_to_osm_object(elem))
            
        return objects_list
    
    def relations(self, element: type[Node | Way | Relation], id: int) -> list[Relation]:
        """Gets all relations that given element is in.

        Args:
            element (type[Node  |  Way  |  Relation]): Element type.
            id (int): Element id.

        Returns:
            list[Relation]: List of Relations that element is in.
        """
        element_name = element.__name__.lower()
        url = self.outer._url.elements["relations"].format(element_type=element_name, id=id)
        status_code, generator = self.outer._get_generator(
            url=url,
            auth_requirement=self.outer._Requirement.NO,
            auto_status_code_handling=False)
        
        relations_list = []
        for event, elem in generator:
            if elem.tag == "relation" and event == "start":
                relations_list.append(_element_to_osm_object(elem))
            
        return relations_list
    
    def ways(self, node_id: int) -> list[Way]:
        """Gets list of ways that node with given id is in.

        Args:
            node_id (int): Node id.

        Returns:
            list[Way]: List of ways.
        """
        url = self.outer._url.elements["ways"].format(id=node_id)
        status_code, generator = self.outer._get_generator(
            url=url,
            auth_requirement=self.outer._Requirement.NO,
            auto_status_code_handling=False)
        
        ways_list = []
        for event, elem in generator:
            if elem.tag == "way" and event == "start":
                ways_list.append(_element_to_osm_object(elem))
            
        return ways_list
    
    def full(self, element: type[Way_Relation], id: int) -> Way_Relation:
        """Retrieves a way or relation and all other elements referenced by it. See https://wiki.openstreetmap.org/wiki/API_v0.6#Full:_GET_/api/0.6/[way|relation]/#id/full for more info.

        Args:
            element (type[Way_Relation]): Type of element.
            id (int): Element id.

        Raises:
            exceptions.IdNotFoundError: Cannot find element with given id.
            exceptions.ElementDeleted: Element already deleted.

        Returns:
            Way | Relation: Way or Relation with complete data.
        """
        element_name = element.__name__.lower()
        url = self.outer._url.elements["full"].format(element_type = element_name, id=id)
        status_code, generator = self.outer._get_generator(
            url=url,
            auth_requirement=self.outer._Requirement.NO,
            auto_status_code_handling=False)
        
        match status_code:
            case 200: pass
            case 404: raise exceptions.IdNotFoundError()
            case 410: raise exceptions.ElementDeleted()
            case _: assert False, f"Unexpected response status code {status_code}. Please report it on github."
        
        nodes_dict: dict[int, Node] = {}
        ways_dict:  dict[int, Way]  = {}
        relations_dict: dict[int, Relation] = {}
        for event, elem in generator:
            if event == "start":
                if elem.tag == "node":
                    node = _element_to_osm_object(elem)
                    nodes_dict.update({node.id: node})
                if elem.tag == "way":
                    way = _element_to_osm_object(elem)
                    ways_dict.update({way.id: way})
                if elem.tag == "relation" and element_name == "relation":
                    relation = _element_to_osm_object(elem)
                    relations_dict.update({relation.id: relation})
        
        for way_id in ways_dict:
            for i in range(len(ways_dict[way_id].nodes)):
                ways_dict[way_id].nodes[i] = deepcopy(nodes_dict[ways_dict[way_id].nodes[i].id])

        if element_name == "relation":
            for relation_id in relations_dict:
                members = relations_dict[relation_id].members
                for i in range(len(members)):
                    if isinstance(members[i].element, Node):
                        members[i] = Member(deepcopy(nodes_dict[members[i].element.id]), members[i].role)
                    elif isinstance(members[i].element, Way):
                        members[i] = Member(deepcopy(ways_dict[members[i].element.id]), members[i].role)

            del nodes_dict, ways_dict
            return relations_dict[id]
        else:
            del nodes_dict, relations_dict
            return ways_dict[id]
        
    def redaction(self, element: type[Node | Way | Relation], id: int, version: int, redaction_id: int) -> None:
        """Moderator only https://wiki.openstreetmap.org/wiki/API_v0.6#Redaction:_POST_/api/0.6/[node|way|relation]/#id/#version/redact?redaction=#redaction_id

        Args:
            element (type[Node  |  Way  |  Relation]): Element type
            id (int): Element id
            version (int): Version to redaction
            redaction_id (int): https://www.openstreetmap.org/redactions
        """
        element_name = element.__name__.lower()
        self.outer._request(self.outer._RequestMethods.POST, self.outer._url.elements["redaction"].format(element_type=element_name, id=id, version=version, redaction_id=redaction_id), self.outer._Requirement.YES, auto_status_code_handling=True)