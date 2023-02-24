from xml.dom import minidom
from copy import copy

from typing import TYPE_CHECKING, Generator, Tuple
if TYPE_CHECKING:
    from xml.etree import ElementTree
    from api import Api
    from src import Node, Way, Relation

from src import Tags, Action
from src.utils import join_url
from src.data_classes import Changeset, OsmChange
from src.api import exceptions
from src.diff.diff_parser import OsmChange_parser_generator


class Changeset_Container:
    def __init__(self, outer):
        self.outer: "Api" = outer

    @staticmethod
    def _xml_to_changeset(generator: Generator[Tuple[str, 'ElementTree.Element'], None, None], include_discussion: bool = False) -> Changeset:
        """Creates Changeset instance from xml provided by API

        Args:
            generator (Generator[Tuple[str, ElementTree.Element], None, None]): Generator for xml file.
            include_discussion (bool, optional): Whether xml from generator has included discussion or not. Defaults to False.

        Returns:
            Changeset: Changeset object.
        """
        tags = Tags()
        discussion = []
        changeset_element = None
        for event, element in generator:
            if element.tag == "changeset" and event == "start":
                changeset_element = copy(element)
            elif element.tag == "tag" and event == "start":
                tags.update({element.attrib["k"]: element.attrib["v"]})
            elif include_discussion and element.tag == "discussion" and event == "start":
                for comment in element:
                    discussion.append({"date": comment.attrib["date"], "user_id": comment.attrib["uid"], "text": comment[0].text})

        assert changeset_element, "No changeset element in API response for get changeset. Should not happen."
        return Changeset(
                changeset_element.attrib["id"],
                changeset_element.attrib["created_at"],
                True if changeset_element.attrib["open"] == "true" else False,
                changeset_element.attrib["uid"],
                changeset_element.attrib["comments_count"],
                changeset_element.attrib["changes_count"],
                tags,
                discussion if include_discussion else None
            )

    def create(self, comment: str, tags: Tags | None = None) -> str:
        """Creates new changeset.

        Args:
            comment (str): Description for changeset.
            tags (Tags | None, optional): Tags for changeset. Defaults to None.

        Returns:
            str: Changeset ID.
        """
        root = minidom.Document()
        xml = root.createElement("osm")
        root.appendChild(xml)
        changeset = root.createElement("changeset")
        tag_xml = root.createElement("tag")
        tag_xml.setAttribute("k", "comment")
        tag_xml.setAttribute("v", comment)
        changeset.appendChild(tag_xml)
        if tags:
            for tag in tags._to_xml():
                changeset.appendChild(tag)

        xml.appendChild(changeset)
        xml_str = root.toprettyxml(indent="\t")

        response = self.outer._request(self.outer._RequestMethods.PUT,
            self.outer._url.changeset["create"], self.outer._Requirement.YES, body=xml_str)
        return response.text

    def get(self, id: str, include_discussion: bool = False) -> Changeset:
        """Get changeset data from OSM server.

        Args:
            id (str): Changeset ID.
            include_discussion (bool, optional): Include discussion or not. Defaults to False.

        Raises:
            exceptions.IdNotFoundError: Raises when there is no changeset with provided ID.

        Returns:
            Changeset: Changeset object.
        """
        include_discussion_text = "true" if include_discussion else "false"
        param = f"{id}?include_discussion={include_discussion_text}"
        status_code, generator = self.outer._get_generator(
            url=join_url(self.outer._url.changeset["get"], param),
            auth_requirement=self.outer._Requirement.NO,
            auto_status_code_handling=False)

        match status_code:
            case 200: pass
            case 404: raise exceptions.IdNotFoundError()

        return self._xml_to_changeset(generator, include_discussion) # type: ignore

    # def get_query(self, left: float | None = None, bottom: float | None = None, right: float | None = None, top: float | None = None,
    # user_id: str | None = None, display_name: str | None = None,
    # time_one: str | None = None, time_two: str | None = None,
    # open: bool = False, closed: bool = False,
    # changesets_id: list[str] | None = None
    # ):
    #     pass
    
    def update(self, id: str, comment: str | None = None, tags: Tags | None = None) -> Changeset:
        """Updates the changeset with new comment or tags or both.

        Args:
            id (str): Changeset ID.
            comment (str | None, optional): New changeset description. Defaults to None.
            tags (Tags | None, optional): New changeset tags. Defaults to None.

        Raises:
            ValueError: If no comment and tags was provided.
            exceptions.IdNotFoundError: When there is no changeset with given ID.
            exceptions.ChangesetAlreadyClosedOrUserIsNotAnAuthor: Changeset was already closed or you are not the author.

        Returns:
            Changeset: New Changeset object.
        """
        if not comment and not tags: raise ValueError("Please provide comment or tags or both.")

        root = minidom.Document()
        xml = root.createElement("osm")
        root.appendChild(xml)
        changeset = root.createElement("changeset")
        if comment:
            tag_xml = root.createElement("tag")
            tag_xml.setAttribute("k", "comment")
            tag_xml.setAttribute("v", comment)
            changeset.appendChild(tag_xml)
        if tags:
            for tag in tags:
                tag_xml = root.createElement("tag")
                tag_xml.setAttribute("k", tag)
                tag_xml.setAttribute("v", tags.get(tag))  # type: ignore
                changeset.appendChild(tag_xml)

        xml.appendChild(changeset)
        xml_str = root.toprettyxml(indent="\t")

        response = self.outer._request(self.outer._RequestMethods.PUT,
            self.outer._url.changeset["update"].format(id=id), self.outer._Requirement.YES, body=xml_str, stream=True, auto_status_code_handling = False)

        match response.status_code:
            case 200: pass
            case 404: raise exceptions.IdNotFoundError()
            case 409: raise exceptions.ChangesetAlreadyClosedOrUserIsNotAnAuthor(response.text)

        response.raw.decode_content = True
        return self._xml_to_changeset(self.outer._raw_stream_parser(response.raw), True)

    def close(self, id: str) -> None:
        """Close changeset by ID.

        Args:
            id (str): Changeset ID.

        Raises:
            exceptions.IdNotFoundError: There is no changeset with given ID.
            exceptions.ChangesetAlreadyClosedOrUserIsNotAnAuthor: The changeset was already closer or you are not the author.
        """
        response = self.outer._request(self.outer._RequestMethods.PUT, self.outer._url.changeset["close"].format(id = id), self.outer._Requirement.YES, auto_status_code_handling = False)
        match response.status_code:
            case 200: pass
            case 404: raise exceptions.IdNotFoundError()
            case 409: raise exceptions.ChangesetAlreadyClosedOrUserIsNotAnAuthor(response.text)

    def download(self, id: str) -> Generator[Tuple['Action', 'Node | Way | Relation'], None, None]:
        """Download changes made in changeset. Like in 'diff' module.

        Args:
            id (str): Changeset ID.

        Raises:
            exceptions.IdNotFoundError: There is no changeset with given ID.

        Yields:
            Generator: Diff generator like in 'diff' module.
        """
        stream = self.outer._request(self.outer._RequestMethods.GET, self.outer._url.changeset["download"].format(id=id), self.outer._Requirement.NO, stream=True, auto_status_code_handling = False)

        match stream.status_code:
            case 200: pass
            case 404: raise exceptions.IdNotFoundError()
        
        stream.raw.decode_content = True
        def generator() -> Generator[tuple['Action', 'Node | Way | Relation'], None, None]:   
            gen = OsmChange_parser_generator(stream.raw, None)
            next(gen) # for meta data
            for action, element in gen: # type: ignore
                assert isinstance(action, Action), "ERROR::API::ENDPOINTS::CHANGESET::download action TYPE IS NOT EQUAL TO ACTION"
                yield (action, element) # type: ignore (We checked if it is Action)
        return generator()

    def upload(self, changeset_id: str, osmChange: OsmChange):
        # TODO: Parse returned xml
        """Upload OsmChange to OSM. You must provide changeset ID for open changeset.

        Args:
            changeset_id (str): Open changeset ID.
            osmChange (OsmChange): OsmChange instance with changes you want to upload.

        Raises:
            exceptions.ErrorWhenParsingXML: Incorrect OsmChange object. Maybe missing elements attributes.
            exceptions.IdNotFoundError: No changeset with provided ID or can't find element with ID in OsmChange.
            exceptions.ChangesetAlreadyClosedOrUserIsNotAnAuthor: Changeset already closed or you are not an author.
            ValueError: Unexpected but correct error.
        """
        response = self.outer._request(
            method=self.outer._RequestMethods.POST,
            url=self.outer._url.changeset["upload"].format(id=changeset_id),
            auth_requirement=self.outer._Requirement.YES,
            body = osmChange._to_xml(changeset_id),
            auto_status_code_handling=False
        )
        match response.status_code:
            case 200: pass
            case 400: raise exceptions.ErrorWhenParsingXML(response.text)
            case 404: raise exceptions.IdNotFoundError(response.text)
            case 409: raise exceptions.ChangesetAlreadyClosedOrUserIsNotAnAuthor()
            case _: raise ValueError("Unexpected but correct error. Status code:", response.status_code)