from typing import Dict

from ..data_classes import User

class Comment():
    def __init__(self,
                comment_created_at: str | None = None,
                user: User | None = None,
                action: str | None = None,
                text: str | None = None,
                html: str | None = None
        ):
        self.comment_created_at = comment_created_at
        self.user = user
        self.action = action
        self.text = text
        self.html = html

    def __str__(self):
        temp = f"{self.__class__.__name__}("
        for k in self.__dict__:
            temp += f"{k} = {getattr(self, k)}, "
        temp += ")"
        return temp

class Note():
    def __init__(self,
                id: int | None = None,
                latitude: str | None = None,   # str to prevent rounding values
                longitude: str | None = None,
                note_created_at: str | None = None,
                open: bool = False,
                comments: list[Comment] = []
        ):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.note_created_at = note_created_at
        self.open = open
        self.comments = comments

    def __str__(self):
        temp = f"{self.__class__.__name__}("
        for k in self.__dict__:
            temp += f"{k} = {getattr(self, k)}, "
        temp += ")"
        return temp
        