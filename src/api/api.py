import requests
from xml.etree import ElementTree
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from urllib3.response import HTTPResponse

from ._URLs import URLs
from .endpoints import Misc

class Api():
    def __init__(self, url: str = "https://master.apis.dev.openstreetmap.org"):
        self.url = URLs(url)
        self.misc = Misc(self)

    @staticmethod
    def _raw_stream_parser(xml_raw_stream: "HTTPResponse"):
        iterator = ElementTree.iterparse(xml_raw_stream, events=('start', 'end'))
        for event, element in iterator:
            yield(event, element)
            element.clear()

    @staticmethod
    def _request_raw_stream(url: str):
        response = requests.get(url, stream=True)
        if response.status_code != 200: raise ValueError(f"Invalid response code {response.status_code} for {url}")
        response.raw.decode_content = True
        return response.raw
    
    def _get_generator(self, url: str):
        return self._raw_stream_parser(self._request_raw_stream(url))