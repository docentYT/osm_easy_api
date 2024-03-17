import shutil

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...api import Api

# TODO: GPX full support and parser

class Gpx_Container:
    def __init__(self, outer):
        self.outer: "Api" = outer

    def get(self, file_to: str, left: str, bottom: str, right: str, top: str, page_number: int = 0) -> None:
        """Downloads gps points to file.

        Args:
            file_to (str): Path where you want to save gpx
            left (int): Bounding box
            bottom (int): Bounding box
            right (int): Bounding box
            top (int): Bounding box
            page_number (int, optional): Which group of 5 000 points you want to get. Indexed from 0. Defaults to 0.
        """
        response = self.outer._request(self.outer._RequestMethods.GET, self.outer._url.gpx["get"].format(left=left, bottom=bottom, right=right, top=top, page_number=page_number), stream=True)
        with open(file_to, "wb") as f_to:
            shutil.copyfileobj(response.raw, f_to)

    def create(self, file_from: str, description: str, visibility: str, tags: list[str] | None = None) -> int:
        """Uploads a GPX file or archive of GPX files.

        Args:
            file_from (str): Path to file to be uploaded.
            description (str): The trace description.
            visibility (str): 'private', 'public', 'trackable' or 'identifiable'. See https://wiki.openstreetmap.org/wiki/Visibility_of_GPS_traces for more info.
            tags (Tags | None, optional): Tags for the trace. Defaults to None.

        Returns:
            int: ID of the new trace.
        """
        # TODO: Enum instead of visibility string
        with open(file_from, "rb") as f:
            tags_string = None
            if tags:
                for i in range(tags.__len__()):
                    tags[i] = tags[i]
                tags_string = ','.join(tags)
            files = {
                "file": f,
                "description": (None, description),
                "tags": (None, tags_string),
                "visibility": (None, visibility)
            }

            response = self.outer._request(self.outer._RequestMethods.POST, url=self.outer._url.gpx["create"], files=files)
            return int(response.text)