from xml.dom import minidom

from typing import TYPE_CHECKING, Generator, Tuple, cast
if TYPE_CHECKING:
    from xml.etree import ElementTree
    from ...api import Api
    from ...data_classes import Node, Way, Relation

from ...utils import join_url
from ...data_classes import Changeset, OsmChange, Tags, Action
from ...api import exceptions
from ...diff.diff_parser import _OsmChange_parser_generator

from .changeset_discussion import Changeset_Discussion_Container


class Changeset_Container:
    def __init__(self, outer):
        self.outer: "Api" = outer
        self.discussion = Changeset_Discussion_Container(outer)

    @staticmethod
    def _xml_to_changesets_list(generator: Generator['ElementTree.Element', None, None], include_discussion: bool = False) -> list[Changeset]:
        """Creates Changeset instance from xml provided by API

        Args:
            generator (Generator[ElementTree.Element, None, None]): Generator for xml file.
            include_discussion (bool, optional): Whether xml from generator has included discussion or not. Defaults to False.

        Returns:
            list[Changeset]: list of Changeset objects.
        """
        changesets_list = []
        tags = Tags()
        discussion = []
        for element in generator:
                if element.tag == "tag":
                    tags.update({element.attrib["k"]: element.attrib["v"]})
                elif include_discussion and element.tag == "discussion":
                    for comment in element:
                        discussion.append({"date": comment.attrib["date"], "user_id": comment.attrib["uid"], "text": comment[0].text})
                
                elif element.tag == "changeset":
                    changesets_list.append(Changeset(
                        int(element.attrib["id"]),
                        element.attrib["created_at"],
                        element.attrib["open"] == "true",
                        element.attrib["uid"],
                        element.attrib["comments_count"],
                        element.attrib["changes_count"],
                        tags,
                        discussion if include_discussion else None
                    ))
                    tags = Tags()
                    element.clear()

        return changesets_list

    def create(self, comment: str, tags: Tags | None = None) -> int:
        """Creates new changeset.

        Args:
            comment (str): Description for changeset.
            tags (Tags | None, optional): Tags for changeset. Defaults to None.

        Returns:
            int: Changeset ID.
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
            self.outer._url.changeset["create"], body=xml_str)
        return int(response.text)

    def get(self, id: int, include_discussion: bool = False) -> Changeset:
        """Get changeset data from OSM server.

        Args:
            id (int): Changeset ID.
            include_discussion (bool, optional): Include discussion or not. Defaults to False.

        Returns:
            Changeset: Changeset object.
        """
        include_discussion_text = "true" if include_discussion else "false"
        param = f"{id}?include_discussion={include_discussion_text}"
        generator = self.outer._request_generator(method=self.outer._RequestMethods.GET, url=join_url(self.outer._url.changeset["get"], param))

        return self._xml_to_changesets_list(generator, include_discussion)[0]

    def get_query(self, left: float | None = None, bottom: float | None = None, right: float | None = None, top: float | None = None,
    user_id: int | None = None, display_name: str | None = None,
    time_one: str | None = None, time_two: str | None = None,
    open: bool = False, closed: bool = False,
    changesets_id: list[int] | None = None,
    order: str = "newest",
    limit: int = 100
    ) -> list[Changeset]:
        """Get changesets with given criteria.

        Args:
            left (float | None, optional): Left side of bounding box (min_lon / west) Use left, bottom, right, top together. Defaults to None.
            bottom (float | None, optional): Bottom side of bounding box (min_lat / south). Use left, bottom, right, top together. Defaults to None.
            right (float | None, optional): Right side of bounding box (max_lon / east). Use left, bottom, right, top together. Defaults to None.
            top (float | None, optional): Top side of bounding box (max_lat / north). Use left, bottom, right, top together. Defaults to None.
            user_id (int | None, optional): User id. Defaults to None.
            display_name (str | None, optional): User display name. Defaults to None.
            time_one (str | None, optional): Find changesets closed after time_one. Defaults to None.
            time_two (str | None, optional): Requires time_one. Find changesets created before time_two. (Range time_one - time_two). Defaults to None.
            open (bool, optional): Find only open changesets. Defaults to False.
            closed (bool, optional): Find only closed changesets. Defaults to False.
            changesets_id (list[int] | None, optional): List of ids to search for. Defaults to None.
            order (str, optional): If 'newest', sort newest changesets first. If 'oldest', reverse order. Defaults to newest.
            limit (int, optional): Specifies the maximum number of changesets returned. Must be between 1 and 100. Defaults to 100.

        Custom exceptions:
            - **404 -> ValueError:** Invalid arguments.

        Returns:
            list[Changeset]: List of Changeset objects.
        """
        param = "?"
        if left or bottom or right or top: param += f"bbox={left},{bottom},{right},{top}&"
        if user_id:         param += f"user={user_id}&"
        if display_name:    param += f"display_name={display_name}&"
        if time_one:        param += f"time={time_one}&"
        if time_two:        param += f",{time_two}&"
        if open:            param += f"open={open}&"
        if closed:          param += f"closed={closed}&"
        if changesets_id:
            param += f"changesets={changesets_id[0]}"
            changesets_id.pop(0)
            for id in changesets_id:
                param += f",{id}"
            param += "&"
        param+=f"order={order}"
        param+=f"&limit={limit}"

        generator = self.outer._request_generator(
            method=self.outer._RequestMethods.GET,
            url=join_url(self.outer._url.changeset["get_query"], param),
            custom_status_code_exceptions={400: ValueError("Invalid arguments. See https://wiki.openstreetmap.org/wiki/API_v0.6#Query:_GET_/api/0.6/changesets for more info.")})

        return self._xml_to_changesets_list(generator)
    
    def update(self, id: int, comment: str | None = None, tags: Tags | None = None) -> Changeset:
        """Updates the changeset with new comment or tags or both.

        Args:
            id (int): Changeset ID.
            comment (str | None, optional): New changeset description. Defaults to None.
            tags (Tags | None, optional): New changeset tags. Defaults to None.

        Raises:
            ValueError: If no comment and tags was provided.

        Custom exceptions:
            - **409 -> `osm_easy_api.api.exceptions.ChangesetAlreadyClosedOrUserIsNotAnAuthor`:** Changeset was already closed or you are not the author.

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
            for key, value in tags.items():
                tag_xml = root.createElement("tag")
                tag_xml.setAttribute("k", key)
                tag_xml.setAttribute("v", value)
                changeset.appendChild(tag_xml)

        xml.appendChild(changeset)
        xml_str = root.toprettyxml(indent="\t")

        response = self.outer._request(self.outer._RequestMethods.PUT,
            self.outer._url.changeset["update"].format(id=id), body=xml_str, stream=True, custom_status_code_exceptions={409: exceptions.ChangesetAlreadyClosedOrUserIsNotAnAuthor("{TEXT}")})

        response.raw.decode_content = True
        return self._xml_to_changesets_list(self.outer._raw_stream_parser(response.raw), True)[0]

    def close(self, id: int) -> None:
        """Close changeset by ID.

        Args:
            id (int): Changeset ID.

        Custom exceptions:
            - **409 -> `osm_easy_api.api.exceptions.ChangesetAlreadyClosedOrUserIsNotAnAuthor`:** Changeset was already closed or you are not the author.
        """
        self.outer._request(self.outer._RequestMethods.PUT, self.outer._url.changeset["close"].format(id = id), custom_status_code_exceptions={409: exceptions.ChangesetAlreadyClosedOrUserIsNotAnAuthor("{TEXT}")})

    def download(self, id: int) -> Generator[Tuple['Action', 'Node | Way | Relation'], None, None]:
        """Download changes made in changeset. Like in 'diff' module.

        Args:
            id (int): Changeset ID.

        Yields:
            Generator: Diff generator like in 'diff' module.
        """
        stream = self.outer._request(self.outer._RequestMethods.GET, self.outer._url.changeset["download"].format(id=id), stream=True)

        stream.raw.decode_content = True
        def generator() -> Generator[tuple['Action', 'Node | Way | Relation'], None, None]:   
            gen = _OsmChange_parser_generator(stream.raw, None)
            next(gen) # for meta data
            for action, element in gen: # type: ignore
                action = cast('Action', action)
                element = cast('Node | Way | Relation', element)
                yield (action, element)
        return generator()

    def upload(self, changeset_id: int, osmChange: OsmChange, make_osmChange_valid: bool = True, work_on_copy: bool = False):
        # TODO: Parse returned xml
        """Upload OsmChange to OSM. You must provide changeset ID for open changeset.

        Args:
            changeset_id (int): Open changeset ID.
            osmChange (OsmChange): OsmChange instance with changes you want to upload. Action cannot be empty!
            make_osmChange_valid (bool): 

        Custom exceptions:
            - **400 -> `osm_easy_api.api.exceptions.ErrorWhenParsingXML`:** Incorrect OsmChange object. Maybe missing elements attributes.
            - **404 -> `osm_easy_api.api.exceptions.IdNotFoundError`:** No changeset with provided ID or can't find element with ID in OsmChange.
            - **409 -> `osm_easy_api.api.exceptions.ChangesetAlreadyClosedOrUserIsNotAnAuthor`:** Changeset already closed or you are not an author.
            OTHER -> ValueError: Unexpected but correct error.
        """
        self.outer._request(
            method=self.outer._RequestMethods.POST,
            url=self.outer._url.changeset["upload"].format(id=changeset_id),
            body = osmChange.to_xml(changeset_id, make_osmChange_valid, work_on_copy),
            custom_status_code_exceptions= {
                400: exceptions.ErrorWhenParsingXML("{TEXT}"),
                404: exceptions.IdNotFoundError("{TEXT}"),
                409: exceptions.ChangesetAlreadyClosedOrUserIsNotAnAuthor(),
                -1: ValueError("Unexpected but correct error. Status code: {CODE}")
            }
        )