from typing import TYPE_CHECKING
import shutil
if TYPE_CHECKING: # pragma: no cover
    from ...api import Api

# TODO: GPX full support and parser

class Gpx_Container:
    def __init__(self, outer):
        self.outer: "Api" = outer

    def get(self, file_to: str, left: str, bottom: str, right: str, top: str, page_number: int) -> None:
        """Downloads gps points to file

        Args:
            file_to (str): Path where you want to save gpx
            left (int): Bounding box
            bottom (int): Bounding box
            right (int): Bounding box
            top (int): Bounding box
            page_number (int): Which group of 5 000 points you want to get.
        """
        response = self.outer._request(self.outer._RequestMethods.GET, self.outer._url.gpx["get"].format(left=left, bottom=bottom, right=right, top=top, page_number=page_number), self.outer._Requirement.NO, True, False)
        with open(file_to, "wb") as f_to:
            shutil.copyfileobj(response.raw, f_to)