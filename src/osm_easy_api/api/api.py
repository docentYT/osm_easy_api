import requests
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
    class _RequestMethods(Enum):
        GET = 0,
        PUT = 1,
        POST = 2,
        DELETE = 3

        def __str__(self):
            return self.name

    def __init__(self, url: str = "https://master.apis.dev.openstreetmap.org", access_token: str | None = None, user_agent: str | None = None):
        self._url = URLs(url)
        self.misc = Misc_Container(self)
        self.changeset = Changeset_Container(self)
        self.elements = Elements_Container(self)
        self.gpx = Gpx_Container(self)
        self.user = User_Container(self)
        self.notes = Notes_Container(self)

        self._headers = {}
        if access_token:
            self._headers.update({"Authorization": "Bearer {}".format(access_token)})

        if user_agent:
            self._headers.update({"User-Agent": user_agent})

    def _request(self, method: _RequestMethods, url: str, stream: bool = False, auto_status_code_handling: bool = True, body = None) -> "Response":
        response = requests.request(str(method), url, stream=stream, data=body.encode('utf-8') if body else None, headers=self._headers)
        if auto_status_code_handling: assert response.status_code == 200, f"Invalid (and unexpected) response code {response.status_code} for {url}"
        return response
    
    @staticmethod
    def _raw_stream_parser(xml_raw_stream: "HTTPResponse") -> Generator[ElementTree.Element, None, None]:
            iterator = ElementTree.iterparse(xml_raw_stream, events=('end', ))
            for event, element in iterator:
                yield element
        
    def _get_generator(self, url: str, auto_status_code_handling: bool = True) -> Generator[ElementTree.Element, None, None] | Tuple[int, Generator[ElementTree.Element, None, None]]:
        response = self._request(self._RequestMethods.GET, url, auto_status_code_handling=auto_status_code_handling, stream=True)
        response.raw.decode_content = True
        if auto_status_code_handling:
            return self._raw_stream_parser(response.raw)
        else:
            return (response.status_code, self._raw_stream_parser(response.raw))
        
    def _post_generator(self, url: str, auto_status_code_handling: bool = True) -> Generator[ElementTree.Element, None, None] | Tuple[int, Generator[ElementTree.Element, None, None]]:
        response = self._request(self._RequestMethods.POST, url, auto_status_code_handling=auto_status_code_handling, stream=True)
        response.raw.decode_content = True
        if auto_status_code_handling:
            return self._raw_stream_parser(response.raw)
        else:
            return (response.status_code, self._raw_stream_parser(response.raw))