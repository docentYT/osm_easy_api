from ..data_classes import Tags

class Changeset():
    id: int
    timestamp: str
    open: bool
    user_id: str
    comments_count: str
    changes_count: str
    tags: Tags
    discussion: list[dict] | None = None

    def __init__(self, id: int, timestamp: str, open: bool, user_id: str, comments_count: str, changeset_count: str, tags: Tags, discussion: list[dict] | None = None):
        self.id = id
        self.timestamp = timestamp
        self.open = open
        self.user_id = user_id
        self.comments_count = comments_count
        self.changes_count = changeset_count
        self.tags = tags
        self.discussion = discussion

    def __str__(self):
        temp = f"{self.__class__.__name__}("
        for k in self.__dict__:
            temp += f"{k} = {getattr(self, k)}, "
        temp += ")"
        return temp