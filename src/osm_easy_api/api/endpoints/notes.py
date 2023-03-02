from typing import TYPE_CHECKING, Generator, Tuple
if TYPE_CHECKING: # pragma: no cover
    from xml.etree import ElementTree
    from ...api import Api

from ...api import exceptions
from ...data_classes import User, Note, Comment

from copy import copy, deepcopy
from xml.dom import minidom

class Notes_Container:
    def __init__(self, outer):
        self.outer: "Api" = outer

    @staticmethod
    def _xml_to_note(generator: Generator[Tuple[str, 'ElementTree.Element'], None, None]) -> list[Note]:
        note_list = []
        temp_note = Note()
        for event, element in generator:
            if event == "start":
                match element.tag:
                    case "note": 
                        temp_note.longitude = element.attrib["lon"]
                        temp_note.latitude = element.attrib["lat"]
                    case "id":
                        assert element.text, "[ERROR::API::ENDPOINTS::NOTE::_xml_to_note] No element.text in tag 'id'"
                        temp_note.id = int(element.text)
                    case "date_created":
                        temp_note.note_created_at = element.text
                    case "status":
                        temp_note.open = True if element.text == "open" else False
                    case "comments":
                        for comment in element:
                            temp_comment = Comment()
                            temp_user = User()
                            for comment_tag in comment:
                                # Comment specific data
                                if comment_tag.tag == "date":
                                    assert comment_tag.text, "[ERROR::API::ENDPOINTS::NOTE::_xml_to_note] No comment_tag.text in tag 'date'"
                                    temp_comment.comment_created_at = comment_tag.text
                                # User specific data
                                elif comment_tag.tag == "uid":
                                    assert comment_tag.text, "[ERROR::API::ENDPOINTS::NOTE::_xml_to_note] No comment_tag.text in tag 'uid'"
                                    temp_user.id = int(comment_tag.text)
                                elif comment_tag.tag == "user":
                                    temp_user.display_name = comment_tag.text
                                    temp_comment.user = deepcopy(temp_user)
                                # Comment specific data
                                elif comment_tag.tag == "action":
                                    temp_comment.action = comment_tag.text
                                elif comment_tag.tag == "text":
                                    temp_comment.text = comment_tag.text or ""
                                elif comment_tag.tag == "html":
                                    temp_comment.html = comment_tag.text or ""
                            temp_note.comments.append(deepcopy(temp_comment))
                            del temp_user
                            del temp_comment

            elif element.tag == "note":
                note_list.append(deepcopy(temp_note))
                temp_note = Note()
                temp_note.comments = []

        if (len(note_list) == 0): raise exceptions.EmptyResult()
        return note_list

    def get(self, id: int) -> Note:
        """Returns note with given id.

        Args:
            id (int): Note id.

        Raises:
            exceptions.IdNotFoundError: Note with given id cannot be found.

        Returns:
            Note: Note object.
        """
        status_code, generator = self.outer._get_generator(
            url=self.outer._url.note["get"].format(id=id),
            auth_requirement=self.outer._Requirement.NO,
            auto_status_code_handling=False)
        
        return self._xml_to_note(generator)[0]
    
    def get_bbox(self, left: str, bottom: str, right: str, top: str, limit: int = 100, closed_days: int = 7) -> list[Note]:
        """Get notes in bbox.

        Args:
            left (str): Left bbox
            bottom (str): Bottom bbox
            right (str): Right bbox
            top (str): Top bbox
            limit (int, optional): Max number of notes (1 < limit < 1000). Defaults to 100.
            closed_days (int, optional): Number of days a note needs to be closed to no longer be returned (0 - only open, -1 - all). Defaults to 7.

        Raises:
            ValueError: Any of args limit is exceeded.

        Returns:
            list[Note]: List of notes.
        """
        url=self.outer._url.note["get_bbox"].format(left=left, bottom=bottom, right=right, top=top, limit=limit, closed_days=closed_days)
        status_code, generator = self.outer._get_generator(
            url=url,
            auth_requirement=self.outer._Requirement.NO,
            auto_status_code_handling=False)
        
        match status_code:
            case 200: pass
            case 400: raise ValueError("Limits exceeded")

        return self._xml_to_note(generator)
    
    def create(self, latitude: str, longitude: str, text: str) -> Note:
        """Creates new note.

        Args:
            latitude (str): Latitude
            longitude (str): Longitude
            text (str): Note description

        Returns:
            Note: Object of newly created note.
        """
        generator = self.outer._post_generator(
            url=self.outer._url.note["create"].format(latitude=latitude, longitude=longitude, text=text),
            auth_requirement=self.outer._Requirement.NO,
            auto_status_code_handling=True)
        
        return self._xml_to_note(generator)[0]
    
    def comment(self, id: int, text: str) -> Note:
        """Add a new comment to note

        Args:
            id (int): Note id
            text (str): Comment text

        Raises:
            exceptions.IdNotFoundError: Cannot find note with given id
            exceptions.NoteAlreadyClosed: Note is closed

        Returns:
            Note: Note object of commented note
        """
        status_code, generator = self.outer._post_generator(
            url=self.outer._url.note["comment"].format(id=id, text=text),
            auth_requirement=self.outer._Requirement.YES,
            auto_status_code_handling=False)
        
        match status_code:
            case 200: pass
            case 404: raise exceptions.IdNotFoundError()
            case 409: raise exceptions.NoteAlreadyClosed()

        return self._xml_to_note(generator)[0]
    
    def close(self, id: int, text: str | None = None) -> Note:
        """Close a note as fixed.

        Args:
            id (int): Note id.
            text (str | None, optional): Text to add as comment when closing note. Defaults to None.

        Raises:
            exceptions.IdNotFoundError: Cannot find note with given id.
            exceptions.NoteAlreadyClosed: Note already closed.

        Returns:
            Note: Note object of closed note.
        """
        url=self.outer._url.note["close"].format(id=id, text=text)
        param = f"?text={text}" if text else ""

        status_code, generator = self.outer._post_generator(
            url=url+param,
            auth_requirement=self.outer._Requirement.YES,
            auto_status_code_handling=False)
        
        match status_code:
            case 200: pass
            case 404: raise exceptions.IdNotFoundError()
            case 409: raise exceptions.NoteAlreadyClosed()

        return self._xml_to_note(generator)[0]
    
    def reopen(self, id: int, text: str | None = None) -> Note:
        """Close a note as fixed.

        Args:
            id (int): Note id.
            text (str | None, optional): Text to add as comment when closing note. Defaults to None.

        Raises:
            exceptions.IdNotFoundError: Cannot find note with given id.
            exceptions.NoteAlreadyClosed: Note already closed.

        Returns:
            Note: Note object of closed note.
        """
        url=self.outer._url.note["reopen"].format(id=id, text=text)
        param = f"?text={text}" if text else ""

        status_code, generator = self.outer._post_generator(
            url=url+param,
            auth_requirement=self.outer._Requirement.YES,
            auto_status_code_handling=False)
        
        match status_code:
            case 200: pass
            case 404: raise exceptions.IdNotFoundError()
            case 409: raise exceptions.NoteAlreadyOpen()
            case 410: raise exceptions.ElementDeleted()

        return self._xml_to_note(generator)[0]
    
    def search(self, text: str, limit: int = 100, closed_days: int = 7, user_id: int | None = None, from_date: str | None = None, to_date: str | None = None, sort: str = "updated_at", order: str = "newest") -> list[Note]:
        """Search for notes with initial text and comments.

        Args:
            text (str): Text to search for in inital text and comments.
            limit (int, optional): Limit of returned notes. Defaults to 100.
            closed_days (int, optional): Days a note needs to be closed to no longer be returned. Defaults to 7.
            user_id (int | None, optional): Search for notes created by user. Defaults to None.
            from_date (str | None, optional): Begining of a date range (ISO 8601). Defaults to None.
            to_date (str | None, optional): End of a date range (ISO 8601). Defaults to None.
            sort (str, optional): Which value should be used to sort notes ("updated_at" or "created_at"). Defaults to "updated_at".
            order (str, optional): Order of returned notes ("newset" or "oldest"). Defaults to "newest".

        Raises:
            ValueError: Limits exceeded.

        Returns:
            list[Note]: List of notes objects.
        """
        url=self.outer._url.note["search"].format(text=text, limit=limit, closed=closed_days)
        if user_id: url += f"&user={user_id}"
        if from_date: url += f"&from={from_date}"
        if to_date: url += f"&from={to_date}"
        if sort: url += f"&sort={sort}"
        if order: url += f"&order={order}"

        print(url)
        status_code, generator = self.outer._get_generator(
            url=url,
            auth_requirement=self.outer._Requirement.NO,
            auto_status_code_handling=False)
        
        match status_code:
            case 200: pass
            case 400: raise ValueError("Limits exceeded")

        try:
            return self._xml_to_note(generator)
        except:
            return []