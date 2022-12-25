from typing import TYPE_CHECKING, Generator
if TYPE_CHECKING:
    from xml.etree import ElementTree
    from src import Node, Way, Relation

# TODO: Update OsmChange_parser_generator to have more general usage
from src.diff.diff_parser import OsmChange_parser_generator

class Misc:
        def __init__(self, outer):
            self.outer = outer

        def versions(self) -> list:
            """Returns API versions supported by this instance.

            Raises:
                ValueError: [ERROR::API::MISC::versions] CAN'T FIND version

            Returns:
                _type_: _description_
            """
            gen = self.outer._get_generator(self.outer.url.misc["versions"])
            versions = []
            for event, element in gen:
                if element.tag == "version" and event == "start": versions.append(element.text)
            if len(versions) == 0: raise ValueError("[ERROR::API::MISC::versions] CAN'T FIND version")
            return versions
        
        def capabilities(self):
            def osm_parser(dict: dict, osm_element: "ElementTree.Element"):
                dict.update({"osm": {}})
                for attribute in osm_element.attrib:
                        dict["osm"].update({
                            attribute: osm_element.attrib[attribute]
                        })
            
            def api_parser(dict: dict, api_element: "ElementTree.Element"):
                dict.update({"api": {}})
                for child in api_element:
                    dict["api"].update({child.tag: child.attrib})

            def policy_parser(dict: dict, policy_element: "ElementTree.Element"):
                dict.update({"policy": {}})
                for child in policy_element:
                    if child.tag == "imagery":
                        dict["policy"].update({"imagery": {"blacklist_regex": []}})
                        for blacklist in child:
                            dict["policy"]["imagery"]["blacklist_regex"].append(blacklist.attrib["regex"])

            HEAD_TAGS = ("osm", "api", "policy")
            gen = self.outer._get_generator(self.outer.url.misc["capabilities"])
            return_dict = {}

            for event, element in gen:
                if element.tag in HEAD_TAGS and event == "start":
                    match element.tag:
                        case "osm": osm_parser(return_dict, element)
                        case "api": api_parser(return_dict, element)
                        case "policy": policy_parser(return_dict, element)

            return return_dict

        def get_map_in_bbox(self, left: float, bottom: float, right: float, top: float) -> Generator["Node | Way | Relation", None, None]:
            param = f"?bbox={left},{bottom},{right},{top}"
            stream = self.outer._request_raw_stream(self.outer.url.misc["map"] + param)
            gen = OsmChange_parser_generator(stream, None)
            next(gen) # for meta data
            for action, element in gen: # type: ignore
                yield element           # type: ignore

        def permissions(self):
            gen = self.outer._get_generator(self.outer.url.misc["permissions"])
            return_permission_list = []

            for event, element in gen:
                if element.tag == "permission" and event == "start":
                    return_permission_list.append(element.attrib["name"])
            return return_permission_list
