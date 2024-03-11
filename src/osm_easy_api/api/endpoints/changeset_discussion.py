from typing import TYPE_CHECKING
if TYPE_CHECKING: # pragma: no cover
    from ...api import Api

from ...api import exceptions

import urllib.parse

class Changeset_Discussion_Container:
    def __init__(self, outer):
        self.outer: "Api" = outer

    def comment(self, changeset_id: int, text: str) -> None:
        """Add a comment to a changeset.

        Args:
            changeset_id (int): Changeset id.
            text (str): The comment text.

        Raises:
            exceptions.ChangesetNotClosed: Changeset must be closed to add comment.
            exceptions.TooManyRequests: Request has been blocked due to rate limiting.
        """
        self.outer._request(self.outer._RequestMethods.POST, self.outer._url.changeset_discussion["comment"].format(id=changeset_id, text=urllib.parse.quote(text)), custom_status_code_exceptions={409: exceptions.ChangesetNotClosed()})

    def subscribe(self, changeset_id: int) -> None:
        """Subscribe to the discussion to receive notifications for new comments.

        Args:
            changeset_id (int): Changeset id.

        Raises:
            exceptions.AlreadySubscribed: You are already subscribed to this changeset.
        """
        self.outer._request(self.outer._RequestMethods.POST, self.outer._url.changeset_discussion["subscribe"].format(id=changeset_id), custom_status_code_exceptions={409: exceptions.AlreadySubscribed()})

    def unsubscribe(self, changeset_id: int) -> None:
        """Unsubscribe from discussion to stop receiving notifications.

        Args:
            changeset_id (int): Changeset id.

        Raises:
            exceptions.NotSubscribed: You are not subscribed to this changeset.
        """
        self.outer._request(self.outer._RequestMethods.POST, self.outer._url.changeset_discussion["unsubscribe"].format(id=changeset_id), custom_status_code_exceptions={404: exceptions.NotSubscribed()})

    def hide(self, comment_id: int) -> None:
        """Set visible flag on changeset comment to false. MODERATOR ONLY!

        Args:
            comment_id (int): Comment id.

        Raises:
            exceptions.NotAModerator: You are not a moderator.
            exceptions.IdNotFoundError: Comment with provided id not found.
        """
        self.outer._request(self.outer._RequestMethods.POST, self.outer._url.changeset_discussion["hide"].format(comment_id=comment_id), custom_status_code_exceptions={403: exceptions.NotAModerator()})

    def unhide(self, comment_id: int) -> None:
        """Set visible flag on changeset comment to true. MODERATOR ONLY!

        Args:
            comment_id (int): Comment id.

        Raises:
            exceptions.NotAModerator: You are not a moderator.
            exceptions.IdNotFoundError: Comment with provided id not found.
        """
        self.outer._request(self.outer._RequestMethods.POST, self.outer._url.changeset_discussion["unhide"].format(comment_id=comment_id), custom_status_code_exceptions={403: exceptions.NotAModerator()})