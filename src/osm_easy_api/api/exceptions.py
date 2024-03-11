"""Exceptions thrown by API module."""
class IdNotFoundError(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)

class ChangesetAlreadyClosedOrUserIsNotAnAuthor(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)

class ChangesetNotClosed(Exception):
    pass

class LimitsExceeded(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class ErrorWhenParsingXML(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class AlreadySubscribed(Exception):
    pass

class NotSubscribed(Exception):
    pass

class ElementDeleted(Exception):
    pass

class NoteAlreadyClosed(Exception):
    pass

class NoteAlreadyOpen(Exception):
    pass

class TooManyRequests(Exception):
    pass

class Unauthorized(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class Forbidden(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

STATUS_CODE_EXCEPTIONS = {
    401: Unauthorized("You must provide an access token in order to use this endpoint."),
    403: Forbidden("Either the access token does not support the needed scope or you must be a moderator to use this endpoint."),
    400: ValueError("{TEXT}"),
    404: IdNotFoundError(),
    410: ElementDeleted(),
    412: ValueError("{TEXT}"),
    429: TooManyRequests(),
}
