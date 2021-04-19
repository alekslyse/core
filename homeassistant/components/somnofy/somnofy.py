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
        
        self._email = email
        self._password = password
        self._serial = serial
        self.websession = websession

    async def verify_credentials(self):
        """Check if credentials are ok."""

        
        resp = await self.websession.get(url="https://api.somnofy.com/v1/devices/"+self._serial+"/settings/device/mqtt", auth=BasicAuth(self._email, self._password), raise_for_status=False)
        if resp.status == 200:
            _LOGGER.info("Logged successfully to the somnofy API %s", await resp.text())
            return await resp.text()
        elif resp.status == 500:
            _LOGGER.error("Could login, but wrong device id %s", await resp.text())
            raise SerialNotMatchError("Could not login to the somnofy API" )
        else:
            _LOGGER.error("Could not login to the somnofy API %s", await resp.text())
            raise CredentialErrors("Could not login to the somnofy API" )

                
    async def setSettings(self, host = None, port = None, username = None, password = None, topic_environment = None, topic_presence = None):
        """Update Somnefy server with new data"""

        payload = {
                    "server": {
                        "host": host,
                        "port": port,
                        "username": username,
                        "password": password
                    },
                    "services": [
                        {
                            "type": "environment",
                            "topic": topic_environment,
                            "enabled": True,
                            "parameters": {
                                "interval": 60
                            }
                        },
                        {
                            "type": "presence",
                            "topic": topic_presence,
                            "enabled": True,
                            "parameters": {
                                "presence_delay": 5,
                                "no_presence_delay": 60,
                                "resend_interval": 60
                            }
                        }
                        ]
                    }
        resp = await self.websession.put(url="https://api.somnofy.com/v1/devices/"+self._serial+"/settings/device/mqtt", auth=BasicAuth(self._email, self._password),json=payload, raise_for_status=False)
        if resp.status == 200:
            _LOGGER.info("Logged successfully to the somnofy API %s", await resp.text())
            return await resp.text()
        elif resp.status == 500:
            _LOGGER.error("Could login, but wrong device id %s", await resp.text())
            raise SerialNotMatchError("Could not login to the somnofy API" )
        else:
            _LOGGER.error("Could not login to the somnofy API %s", await resp.text())
            raise CredentialErrors("Could not login to the somnofy API" )




class ApiError(Exception):
    """Raised when an API error occured."""

    def __init__(self, status: str):
        """Initialize."""
        super().__init__(status)
        self.status = status

class SerialNotMatchError(Exception):
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