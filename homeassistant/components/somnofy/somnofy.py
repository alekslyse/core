"""Custom class for Somnofy actions."""

import logging
import os

from aiohttp import ClientSession, BasicAuth

from . import exceptions

_LOGGER = logging.getLogger(__name__)


class Somnofy():
    """Somnofy API class."""

    def __init__(  # pylint:disable=too-many-arguments
        self, email: str, password: str, serial: str, websession: ClientSession
    ):
        
        self.email = None
        self.password = None
        self.serial = None
        self.websession = websession

    async def verify_credentials(self) ->bool:
        """Check if credentials are ok."""

        
        resp = await self.websession.get(url="https://api.somnofy.com/v1/devices/VTKBMNSHGQ/settings/device/mqtt", auth=BasicAuth("aleksander.lyse@gmail.com", "D6JZahGdRr5Cri"), raise_for_status=False)
        if resp.status == 200:
            _LOGGER.info("Logged successfully to the somnofy API %s", await resp.text())
            return True
        else:
            _LOGGER.error("Could not login to the somnofy API %s", await resp.text())
            raise CredentialErrors(
        "Could not login to the somnofy API"
        )
        return False







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