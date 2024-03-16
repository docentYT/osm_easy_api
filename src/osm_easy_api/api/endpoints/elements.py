from typing import TYPE_CHECKING, TypeVar, Type, cast
if TYPE_CHECKING:
    from ...api import Api

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

        Custom exceptions:
            - **409 -> `osm_easy_api.api.exceptions.ChangesetAlreadyClosedOrUserIsNotAnAuthor`:** Changeset has already been closed.

        Returns:
            int: Id of new element.
        """
        element_name = element.__class__.__name__.lower()
        body = f"<osm>\n{element._to_xml(changeset_id).toprettyxml()}</osm>"
        response = self.outer._request(self.outer._RequestMethods.PUT, self.outer._url.elements["create"].format(element_type=element_name), body=body,
                                       custom_status_code_exceptions={
                                           409: exceptions.ChangesetAlreadyClosedOrUserIsNotAnAuthor("{TEXT}")
                                           })
        
        return int(response.text)

    def get(self, elementType: Type[Node_Way_Relation], id: int) -> Node_Way_Relation:
        """""Get element by id

        Args:
            elementType (Type[Node_Way_Relation]): Element type.
            id (int): Element id.

        Custom exceptions:
            - **410 -> `osm_easy_api.api.exceptions.ElementDeleted`:** Element has been deleted. Maybe you should use `version` instead?

        Returns:
            Node_Way_Relation: Representation of element.
        """""
        element_name = elementType.__name__.lower()
        url = self.outer._url.elements["read"].format(element_type=element_name, id=id)
        generator = self.outer._request_generator(method=self.outer._RequestMethods.GET,
            url=url,
            custom_status_code_exceptions={410: exceptions.ElementDeleted()})
        
        for elem in generator:
            if elem.tag in ("node", "way", "relation"):
                object = _element_to_osm_object(elem)
                return cast(elementType, object)
        
        assert False, "No objects to parse!"
    
    def update(self, element: Node | Way | Relation, changeset_id: int) -> int:
        """Updates data for existing element.

        Args:
            element (Node | Way | Relation): Element with updated data. Version of element must be the same as in database. Unchanged data also must be provided.
            changeset_id (int): Changeset id in which you want to update element.

        Custom exceptions:
            - **409 -> `osm_easy_api.api.exceptions.ElementDeleted`:** Error when updating element (bad element data) OR element version does not match the current database version.
            - **412 -> `osm_easy_api.api.exceptions.IdNotFoundError`:** Way or relation has members/elements that do not exist or are not visible.

        Returns:
            int: The new version number.
        """
        element.changeset_id = changeset_id
        element_name = element.__class__.__name__.lower()
        body = f"<osm>\n{element._to_xml(element.changeset_id).toprettyxml()}</osm>"
        response = self.outer._request(self.outer._RequestMethods.PUT, self.outer._url.elements["update"].format(element_type=element_name, id=element.id), body=body, custom_status_code_exceptions={
            409: ValueError("{TEXT}"),
            412: exceptions.IdNotFoundError("{TEXT}"),
        })

        return int(response.text)
    
    def delete(self, element: Node | Way | Relation, changeset_id: int) -> int:
        """Deletes element. 

        Args:
            element (Node | Way | Relation): Element object which you want to delete. Id is not sufficient.
            changeset_id (int): Changeset id in which you want to delete element.

        Custom exceptions:
            - **409 -> `osm_easy_api.api.exceptions.ChangesetAlreadyClosedOrUserIsNotAnAuthor`:** Changeset has already been closed.

        Returns:
            int: The new version number.
        """
        element.changeset_id = changeset_id
        element_name = element.__class__.__name__.lower()
        body = f"<osm>\n{element._to_xml(element.changeset_id).toprettyxml()}</osm>"
        response = self.outer._request(self.outer._RequestMethods.DELETE, self.outer._url.elements["delete"].format(element_type=element_name, id=element.id), body=body, custom_status_code_exceptions={
            409: exceptions.ChangesetAlreadyClosedOrUserIsNotAnAuthor("{TEXT}")
        })

        return int(response.text)
    
    def history(self, elementType: Type[Node_Way_Relation], id: int) -> list[Node_Way_Relation]:
        """Returns all old versions of element.

        Args:
            elementType (Type[Node_Way_Relation]): Element type to search for.
            id (int): Element id.

        Returns:
            list[Node_Way_Relation]: List of previous versions of element.
        """
        element_name = elementType.__name__.lower()
        url = self.outer._url.elements["history"].format(element_type=element_name, id=id)
        generator = self.outer._request_generator(method=self.outer._RequestMethods.GET, url=url)
        
        objects_list = []
        for elem in generator:
            if elem.tag == element_name:
                objects_list.append(_element_to_osm_object(elem))
            
        return objects_list
    
    def version(self, elementType: Type[Node_Way_Relation], id: int, version: int) -> Node_Way_Relation:
        """Returns specific version of element.

        Args:
            elementType (Type[Node_Way_Relation]): Element type.
            id (int): Element id.
            version (int): Version number you are looking for.

        Custom exceptions:
            - **403 -> `osm_easy_api.api.exceptions.IdNotFoundError`:** This version of the element is not available (due to redaction).

        Returns:
            Node_Way_Relation: Element in specific version.
        """
        element_name = elementType.__name__.lower()
        url = self.outer._url.elements["version"].format(element_type=element_name, id=id, version=version)
        generator = self.outer._request_generator(
            method=self.outer._RequestMethods.GET,
            url=url,
            custom_status_code_exceptions={
                403: exceptions.IdNotFoundError("This version of the element is not available (due to redaction)")
            })
    
        for elem in generator:
            if elem.tag in ("node", "way", "relation"):
                return cast(Node_Way_Relation, _element_to_osm_object(elem))
        assert False, "[ERROR::API::ENDPOINTS::ELEMENTS::version] Cannot create an element."
    
    def get_query(self, elementType: Type[Node_Way_Relation], ids: list[int]) -> list[Node_Way_Relation]:
        """Allows fetch multiple elements at once.

        Args:
            elementType (Type[Node_Way_Relation]): Elements type.
            ids (list[int]): List of ids you are looking for.

        Custom exceptions:
            - **414 -> ValueError:** Request url was too long (too many ids).

        Returns:
            list[Node_Way_Relation]: List of elements you are looking for.
        """
        element_name = elementType.__name__.lower() + 's'
        param = f"?{element_name}="
        for id in ids: param += f"{id},"
        param = param[:-1]
        url = self.outer._url.elements["multi_fetch"].format(element_type=element_name) + param
        generator = self.outer._request_generator(
            method=self.outer._RequestMethods.GET,
            url=url,
            custom_status_code_exceptions={
                414: ValueError("URL too long (too many ids)")
            })
        
        objects_list = []
        for elem in generator:
            if elem.tag == elementType.__name__.lower():
                objects_list.append(_element_to_osm_object(elem))
            
        return objects_list
    
    def relations(self, elementType: Type[Node | Way | Relation], id: int) -> list[Relation]:
        """Gets all relations that given element is in.

        Args:
            elementType (Type[Node  |  Way  |  Relation]): Element type.
            id (int): Element id.

        Returns:
            list[Relation]: List of Relations that element is in.
        """
        element_name = elementType.__name__.lower()
        url = self.outer._url.elements["relations"].format(element_type=element_name, id=id)
        generator = self.outer._request_generator(method=self.outer._RequestMethods.GET, url=url)
        
        relations_list = []
        for elem in generator:
            if elem.tag == "relation":
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
        generator = self.outer._request_generator(method=self.outer._RequestMethods.GET, url=url)
        
        ways_list = []
        for elem in generator:
            if elem.tag == "way":
                ways_list.append(_element_to_osm_object(elem))
            
        return ways_list
    
    def full(self, elementType: Type[Way_Relation], id: int) -> Way_Relation:
        """Retrieves a way or relation and all other elements referenced by it. See https://wiki.openstreetmap.org/wiki/API_v0.6#Full:_GET_/api/0.6/[way|relation]/#id/full for more info.

        Args:
            elementType (Type[Way_Relation]): Type of element.
            id (int): Element id.

        Returns:
            Way_Relation: Way or Relation with complete data.
        """
        element_name = elementType.__name__.lower()
        url = self.outer._url.elements["full"].format(element_type = element_name, id=id)
        generator = self.outer._request_generator(method=self.outer._RequestMethods.GET, url=url)
        
        nodes_dict: dict[int, Node] = {}
        ways_dict:  dict[int, Way]  = {}
        relations_dict: dict[int, Relation] = {}
        for elem in generator:
            if elem.tag == "node":
                node = cast(Node, _element_to_osm_object(elem))
                assert node.id, f"[ERROR::API::ENDPOINTS::ELEMENTS::full] No id for {node}"
                nodes_dict.update({node.id: node})
            if elem.tag == "way":
                way = cast(Way, _element_to_osm_object(elem))
                assert way.id, f"[ERROR::API::ENDPOINTS::ELEMENTS::full] No id for {node}"
                ways_dict.update({way.id: way})
            if elem.tag == "relation" and element_name == "relation":
                relation = cast(Relation, _element_to_osm_object(elem))
                assert relation.id, f"[ERROR::API::ENDPOINTS::ELEMENTS::full] No id for {node}"
                relations_dict.update({relation.id: relation})
        
        for way in ways_dict.values():
            for i in range(len(way.nodes)):
                node_id = way.nodes[i].id
                assert node_id, f"[ERROR::API::ENDPOINTS::ELEMENTS::full] No id for {node}"
                node = nodes_dict[node_id]
                way.nodes[i] = deepcopy(node)

        if element_name == "relation":
            for relation in relations_dict.values():
                members = relation.members
                for i in range(len(members)):
                    element = members[i].element
                    assert element.id, f"[ERROR::API::ENDPOINTS::ELEMENTS::full] No id for {element}"
                    if isinstance(element, Node):
                        members[i] = Member(deepcopy(nodes_dict[element.id]), members[i].role)
                    elif isinstance(element, Way):
                        members[i] = Member(deepcopy(ways_dict[element.id]), members[i].role)

            del nodes_dict, ways_dict
            return cast(Way_Relation, relations_dict[id])
        else:
            del nodes_dict, relations_dict
            return cast(Way_Relation, ways_dict[id])
        
    def redaction(self, element: type[Node | Way | Relation], id: int, version: int, redaction_id: int) -> None:
        """Moderator only https://wiki.openstreetmap.org/wiki/API_v0.6#Redaction:_POST_/api/0.6/[node|way|relation]/#id/#version/redact?redaction=#redaction_id

        Args:
            element (type[Node  |  Way  |  Relation]): Element type
            id (int): Element id
            version (int): Version to redaction
            redaction_id (int): https://www.openstreetmap.org/redactions
        """
        element_name = element.__name__.lower()
        self.outer._request(self.outer._RequestMethods.POST, self.outer._url.elements["redaction"].format(element_type=element_name, id=id, version=version, redaction_id=redaction_id))