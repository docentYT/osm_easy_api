import requests
from xml.etree import ElementTree
from enum import Enum

from typing import TYPE_CHECKING, Generator, Tuple
if TYPE_CHECKING:
    from urllib3.response import HTTPResponse
    from requests.models import Response

from ._URLs import URLs
from .endpoints import Misc_Container, Changeset_Container, Elements_Container, Gpx_Container, User_Container, Notes_Container
from .exceptions import STATUS_CODE_EXCEPTIONS

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

    def _request(self, method: _RequestMethods, url: str, stream: bool = False, custom_status_code_exceptions: dict = {int: Exception}, body = None) -> "Response":
        response = requests.request(str(method), url, stream=stream, data=body.encode('utf-8') if body else None, headers=self._headers)
        if response.status_code == 200: return response

        exception = custom_status_code_exceptions.get(response.status_code, None) or STATUS_CODE_EXCEPTIONS.get(response.status_code, None)
        if not exception: exception = custom_status_code_exceptions.get(-1, None)
        if not exception: raise NotImplementedError(f"Invalid (and unexpected) response code {response.status_code} for {url}. Please report it on GitHub.")
        if str(exception): raise type(exception)(str(exception).format(TEXT=response.text, CODE=response.status_code)) from exception
        raise exception
    
    @staticmethod
    def _raw_stream_parser(xml_raw_stream: "HTTPResponse") -> Generator[ElementTree.Element, None, None]:
            iterator = ElementTree.iterparse(xml_raw_stream, events=['end'])
            for event, element in iterator:
                yield element

    def _request_generator(self, method: _RequestMethods, url: str, custom_status_code_exceptions: dict = {int: Exception}) -> Generator[ElementTree.Element, None, None]:
        response = self._request(method=method, url=url, stream=True, custom_status_code_exceptions=custom_status_code_exceptions)
        response.raw.decode_content = True
        return self._raw_stream_parser(response.raw)