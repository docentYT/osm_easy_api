import requests
from requests.auth import HTTPBasicAuth
from xml.etree import ElementTree
from enum import Enum

from typing import TYPE_CHECKING, Generator, Tuple
if TYPE_CHECKING: # pragma: no cover
    from urllib3.response import HTTPResponse
    from requests.models import Response

from ._URLs import URLs
from .endpoints import Misc_Container, Changeset_Container, Elements_Container, Gpx_Container, User_Container, Notes_Container

class Api():
    """Class used to communicate with API."""
    class _Requirement(Enum):
        YES = 0,
        NO = 1,
        OPTIONAL = 2

    class _RequestMethods(Enum):
        GET = 0,
        PUT = 1,
        POST = 2,
        DELETE = 3

        def __str__(self):
            return self.name

    def __init__(self, url: str = "https://master.apis.dev.openstreetmap.org", username: str | None = None, password: str | None = None, user_agent: str | None = None):
        self._url = URLs(url)
        self.misc = Misc_Container(self)
        self.changeset = Changeset_Container(self)
        self.elements = Elements_Container(self)
        self.gpx = Gpx_Container(self)
        self.user = User_Container(self)
        self.notes = Notes_Container(self)

        if username and password:
            self._auth = HTTPBasicAuth(username.encode('utf-8'), password.encode('utf-8'))
        else:
            self._auth = None

        if user_agent:
            self._user_agent = user_agent

    def _request(self, method: _RequestMethods, url: str, auth_requirement: _Requirement = _Requirement.OPTIONAL, stream: bool = False, auto_status_code_handling: bool = True, body = None) -> "Response":
        headers = {}
        if hasattr(self, "_user_agent"):
            headers.update({"User-Agent": self._user_agent})
        match auth_requirement:
            case self._Requirement.YES:
                if not self._auth: raise ValueError("No credentials provided during class initialization!")
                response = requests.request(str(method), url, stream=stream, auth=self._auth, data=body.encode('utf-8') if body else None, headers=headers)
            case self._Requirement.OPTIONAL:
                response = requests.request(str(method), url, stream=stream, auth=self._auth, data=body.encode('utf-8') if body else None, headers=headers)
            case self._Requirement.NO:
                response = requests.request(str(method), url, stream=stream, data=body.encode('utf-8') if body else None, headers=headers)
        if auto_status_code_handling: assert response.status_code == 200, f"Invalid (and unexpected) response code {response.status_code} for {url}"
        return response
    
    @staticmethod
    def _raw_stream_parser(xml_raw_stream: "HTTPResponse") -> Generator[ElementTree.Element, None, None]:
            iterator = ElementTree.iterparse(xml_raw_stream, events=('end', ))
            for event, element in iterator:
                yield element
        
    def _get_generator(self, url: str, auth_requirement: _Requirement = _Requirement.OPTIONAL, auto_status_code_handling: bool = True) -> Generator[ElementTree.Element, None, None] | Tuple[int, Generator[ElementTree.Element, None, None]]:
        response = self._request(self._RequestMethods.GET, url, auth_requirement, auto_status_code_handling=auto_status_code_handling, stream=True)
        response.raw.decode_content = True
        if auto_status_code_handling:
            return self._raw_stream_parser(response.raw)
        else:
            return (response.status_code, self._raw_stream_parser(response.raw))
        
    def _post_generator(self, url: str, auth_requirement: _Requirement = _Requirement.OPTIONAL, auto_status_code_handling: bool = True) -> Generator[ElementTree.Element, None, None] | Tuple[int, Generator[ElementTree.Element, None, None]]:
        response = self._request(self._RequestMethods.POST, url, auth_requirement, auto_status_code_handling=auto_status_code_handling, stream=True)
        response.raw.decode_content = True
        if auto_status_code_handling:
            return self._raw_stream_parser(response.raw)
        else:
            return (response.status_code, self._raw_stream_parser(response.raw))