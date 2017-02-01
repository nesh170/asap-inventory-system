class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class InvalidLoggerError(Error):
    """Exception raised if the username is not system or not in the system, not allowed to log

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message