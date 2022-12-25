import requests
from requests.auth import HTTPBasicAuth
from xml.etree import ElementTree
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from urllib3.response import HTTPResponse

from ._URLs import URLs
from .endpoints import Misc

class Api():
    def __init__(self, url: str = "https://master.apis.dev.openstreetmap.org", username: str | None = None, password: str | None = None):
        self._url = URLs(url)
        self.misc = Misc(self)

        if username and password:
            self._auth = HTTPBasicAuth(username, password)
        else:
            self._auth = None


    @staticmethod
    def _raw_stream_parser(xml_raw_stream: "HTTPResponse"):
        iterator = ElementTree.iterparse(xml_raw_stream, events=('start', 'end'))
        for event, element in iterator:
            yield(event, element)
            element.clear()

    def _request_raw_stream(self, url: str):
        if self._auth: response = requests.get(url, stream=True, auth=self._auth)
        else: response = requests.get(url, stream=True)
        if response.status_code != 200: raise ValueError(f"Invalid response code {response.status_code} for {url}")
        response.raw.decode_content = True
        return response.raw
    
    def _get_generator(self, url: str):
        return self._raw_stream_parser(self._request_raw_stream(url))