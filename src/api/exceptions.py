class IdNotFoundError(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)

class ChangesetAlreadyClosedOrUserIsNotAnAuthor(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)

class LimitsExceeded(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class ErrorWhenParsingXML(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)