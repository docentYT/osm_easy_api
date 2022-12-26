import requests
from requests.auth import HTTPBasicAuth
from xml.etree import ElementTree
from enum import Enum

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from urllib3.response import HTTPResponse
    from requests.models import Response

from ._URLs import URLs
from .endpoints import Misc

class Api():
    class Requirement(Enum):
        YES = 0,
        NO = 1,
        OPTIONAL = 2

    def __init__(self, url: str = "https://master.apis.dev.openstreetmap.org", username: str | None = None, password: str | None = None):
        self._url = URLs(url)
        self.misc = Misc(self)

        if username and password:
            self._auth = HTTPBasicAuth(username, password)
        else:
            self._auth = None

    def _request(self, url: str, auth_requirement: Requirement = Requirement.OPTIONAL, stream_data: bool = False) -> "Response":
        match auth_requirement:
            case self.Requirement.YES:
                if not self._auth: raise ValueError("No creditentials provided during class initalization!")
                response = requests.get(url, stream=stream_data, auth=self._auth)
            case self.Requirement.OPTIONAL:
                if self._auth: response = requests.get(url, stream=stream_data, auth=self._auth)
                else: response = requests.get(url, stream=stream_data)
            case self.Requirement.NO:
                response = requests.get(url, stream=stream_data)
        return response

    @staticmethod
    def _raw_stream_parser(xml_raw_stream: "HTTPResponse"):
        iterator = ElementTree.iterparse(xml_raw_stream, events=('start', 'end'))
        for event, element in iterator:
            yield(event, element)
            element.clear()
    
    def _get_generator(self, url: str, auth_requirement: Requirement = Requirement.OPTIONAL):
        response = self._request(url, auth_requirement, stream_data=True)
        if response.status_code != 200: raise ValueError(f"Invalid response code {response.status_code} for {url}")
        response.raw.decode_content = True
        return self._raw_stream_parser(response.raw)