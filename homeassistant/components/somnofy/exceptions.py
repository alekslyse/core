"""Custom exceptions."""


class ApiError(Exception):
    """Raised when an API error occured."""

    def __init__(self, status: str):
        """Initialize."""
        super().__init__(status)
        self.status = status

class CredentialErrors(Exception):
    """Raised when credentials was not correct."""

    def __init__(self, status: str):
        """Initialize."""
        super().__init__(status)
        self.status = status

class SerialError(Exception):
    """Raised when the user doesnt own the unit."""

    def __init__(self, status: str):
        """Initialize."""
        super().__init__(status)
        self.status = status