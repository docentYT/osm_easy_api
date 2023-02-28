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
    
class EmptyResult(Exception):
    pass

class AlreadySubscribed(Exception):
    pass

class NotSubscribed(Exception):
    pass

class NotAModerator(Exception):
    pass

class ElementDeleted(Exception):
    pass

class NoteAlreadyClosed(Exception):
    pass

class NoteAlreadyOpen(Exception):
    pass