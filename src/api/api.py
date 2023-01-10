import requests
from requests.auth import HTTPBasicAuth
from xml.etree import ElementTree
from enum import Enum

from typing import TYPE_CHECKING, Generator, Tuple
if TYPE_CHECKING:
    from urllib3.response import HTTPResponse
    from requests.models import Response

from ._URLs import URLs
from .endpoints import Misc_Container, Changeset_Container

class Api():
    class Requirement(Enum):
        YES = 0,
        NO = 1,
        OPTIONAL = 2

    class RequestMethods(Enum):
        GET = 0,
        PUT = 1,
        POST = 2

        def __str__(self):
            return self.name

    def __init__(self, url: str = "https://master.apis.dev.openstreetmap.org", username: str | None = None, password: str | None = None):
        self._url = URLs(url)
        self.misc = Misc_Container(self)
        self.changeset = Changeset_Container(self)

        if username and password:
            self._auth = HTTPBasicAuth(username, password)
        else:
            self._auth = None

    def _request(self, method: RequestMethods, url: str, auth_requirement: Requirement = Requirement.OPTIONAL, stream: bool = False, auto_status_code_handling: bool = True, body = None) -> "Response":
        match auth_requirement:
            case self.Requirement.YES:
                if not self._auth: raise ValueError("No creditentials provided during class initalization!")
                response = requests.request(str(method), url, stream=stream, auth=self._auth, data=body)
            case self.Requirement.OPTIONAL:
                response = requests.request(str(method), url, stream=stream, auth=self._auth, data=body)
            case self.Requirement.NO:
                response = requests.request(str(method), url, stream=stream, data=body)
                
        if auto_status_code_handling: assert response.status_code == 200, f"Invalid and unexpected response code {response.status_code} for {url}"
        return response

    @staticmethod
    def _raw_stream_parser(xml_raw_stream: "HTTPResponse") -> Generator[Tuple[str, ElementTree.Element], None, None]:
        iterator = ElementTree.iterparse(xml_raw_stream, events=('start', 'end'))
        for event, element in iterator:
            yield(event, element)
            element.clear()
    
    def _get_generator(self, url: str, auth_requirement: Requirement = Requirement.OPTIONAL, auto_status_code_handling: bool = True) -> Generator[Tuple[str, ElementTree.Element], None, None] | Tuple[int, Generator[Tuple[str, ElementTree.Element], None, None]]:
        response = self._request(self.RequestMethods.GET, url, auth_requirement, auto_status_code_handling=auto_status_code_handling, stream=True)
        response.raw.decode_content = True
        if auto_status_code_handling:
            return self._raw_stream_parser(response.raw)
        else:
            return (response.status_code, self._raw_stream_parser(response.raw))