"""Custom class for Somnofy actions."""

import logging
import os

from . import exceptions

_LOGGER = logging.getLogger(__name__)


class Somnofy:
    """Somnofy API class."""

    def __init__(self):
        """Init API."""

        self.data = {}

    async def check_connection(ip):
        """Check if there is any response on IP."""

        try:
            response = os.system("ping -c 1 " + ip)

            # and then check the response...
            if response == 0:
                _LOGGER.debug("Device is responsive")
                return True
            else:
                _LOGGER.debug("Device not responsive")
                return False

        except ():
            _LOGGER.error("Can not ping Somnyify device")
            raise exceptions.SomnofyConnectionError
