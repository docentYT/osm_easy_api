from typing import TYPE_CHECKING, Generator, Tuple
if TYPE_CHECKING: # pragma: no cover
    from xml.etree import ElementTree
    from ... import Node, Way, Relation
    from ... import Api

from ...api import exceptions
# TODO: Update OsmChange_parser_generator to have more general usage
from ...diff.diff_parser import OsmChange_parser_generator

class Misc_Container:
        def __init__(self, outer):
            self.outer: Api = outer

        def versions(self) -> list:
            """Returns API versions supported by this instance.

            Raises:
                ValueError: [ERROR::API::MISC::versions] CAN'T FIND version

            Returns:
                list: List of supported versions by instance.
            """
            gen: Generator[Tuple[str, 'ElementTree.Element'], None, None] = self.outer._get_generator(self.outer._url.misc["versions"])
            versions = []
            for event, element in gen:
                if element.tag == "version" and event == "start": versions.append(element.text)
            if len(versions) == 0: raise ValueError("[ERROR::API::MISC::versions] CAN'T FIND version")
            return versions
        
        def capabilities(self) -> dict:
            """Returns dictionary of capabilities and limitations of the current API.

            Returns:
                dict: Capabilities and limitations of the current API.
            """
            def osm_parser(dict: dict, osm_element: "ElementTree.Element") -> None:
                dict.update({"osm": {}})
                for attribute in osm_element.attrib:
                        dict["osm"].update({
                            attribute: osm_element.attrib[attribute]
                        })
            
            def api_parser(dict: dict, api_element: "ElementTree.Element") -> None:
                dict.update({"api": {}})
                for child in api_element:
                    dict["api"].update({child.tag: child.attrib})

            def policy_parser(dict: dict, policy_element: "ElementTree.Element") -> None:
                dict.update({"policy": {}})
                for child in policy_element:
                    if child.tag == "imagery":
                        dict["policy"].update({"imagery": {"blacklist_regex": []}})
                        for blacklist in child:
                            dict["policy"]["imagery"]["blacklist_regex"].append(blacklist.attrib["regex"])

            HEAD_TAGS = ("osm", "api", "policy")
            gen: Generator[Tuple[str, 'ElementTree.Element'], None, None] = self.outer._get_generator(self.outer._url.misc["capabilities"])
            return_dict = {}

            for event, element in gen:
                if element.tag in HEAD_TAGS and event == "start":
                    match element.tag:
                        case "osm": osm_parser(return_dict, element)
                        case "api": api_parser(return_dict, element)
                        case "policy": policy_parser(return_dict, element)

            return return_dict

        def get_map_in_bbox(self, left: float, bottom: float, right: float, top: float) -> Generator["Node | Way | Relation | str", None, None]:
            """Returns generator of map data in border box. See https://wiki.openstreetmap.org/wiki/API_v0.6#Retrieving_map_data_by_bounding_box:_GET_/api/0.6/map for more info. 

            Args:
                left (float)
                bottom (float)
                right (float)
                top (float)

            Yields:
                Node | Way | Relation
            """
            response = self.outer._request(method=self.outer._RequestMethods.GET,
                url=self.outer._url.misc["map"].format(left=left, bottom=bottom, right=right, top=top),
                auth_requirement=self.outer._Requirement.OPTIONAL,
                stream=True,
                auto_status_code_handling=False
            )

            match response.status_code:
                case 200: pass
                case 400: raise exceptions.LimitsExceeded("You are trying to download too much data.")
                case 509: raise exceptions.LimitsExceeded("You have downloaded too much data. Please try again later. See https://wiki.openstreetmap.org/wiki/Developer_FAQ#I've_been_blocked_from_the_API_for_downloading_too_much._Now_what?")
            
            response.raw.decode_content = True
            def generator():
                gen = OsmChange_parser_generator(response.raw, None)
                next(gen) # for meta data
                for action, element in gen: # type: ignore
                    yield element           # type: ignore
            return generator()

        def permissions(self) -> list:
            """Returns list of permissions granted to the current API connection.

            Returns:
                list: List of permissions names.
            """
            gen: Generator[Tuple[str, 'ElementTree.Element'], None, None] = self.outer._get_generator(self.outer._url.misc["permissions"])
            return_permission_list = []

            for event, element in gen:
                if element.tag == "permission" and event == "start":
                    return_permission_list.append(element.attrib["name"])
            return return_permission_list
