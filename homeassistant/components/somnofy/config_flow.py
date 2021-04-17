"""Config flow for Somnofy integration."""
import asyncio
import logging

from async_timeout import timeout
import voluptuous as vol
from voluptuous.error import EmailInvalid, LengthInvalid, RequiredFieldInvalid

from homeassistant import config_entries, core, exceptions, data_entry_flow
from homeassistant.const import CONF_DEVICE_ID, CONF_EMAIL, CONF_NAME, CONF_PASSWORD
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN  # pylint:disable=unused-import
from .exceptions import ApiError
from .somnofy import Somnofy, CredentialErrors

_LOGGER = logging.getLogger(__name__)


class SomnofyFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Somnofy Config Flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL
    init_info = None

    async def async_step_user(self, user_input=None):
        """Handle the user input."""

        errors = {}

        if user_input is not None:
            websession = async_get_clientsession(self.hass)
            try:
                async with timeout(10):
                    somnofy = Somnofy(
                        user_input[CONF_EMAIL],
                        user_input[CONF_PASSWORD],
                        user_input[CONF_DEVICE_ID],
                        websession
                    )
                    valid = await somnofy.verify_credentials()
                    if valid:
                        if not user_input[CONF_NAME]:
                            name = user_input[CONF_DEVICE_ID]
                        else:
                            name = user_input[CONF_NAME]
                        return self.async_create_entry(
                        title=name,
                        data={
                            "something_special": user_input["email"]
                        },
                    )

            except (CredentialErrors):
                errors["base"] = "auth_error" 

    
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Required(CONF_DEVICE_ID): str,
                    vol.Optional(CONF_NAME): str,
                }
            ),
            errors=errors,
        )

    async def async_step_account(self, user_input=None):
        return self.async_create_entry(title=self.data["title"], data=self.data)



class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidHost(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname."""
