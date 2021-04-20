"""Config flow for Somnofy integration."""
import json
import logging

from async_timeout import timeout
import voluptuous as vol

from homeassistant.components.dhcp import HOSTNAME, IP

from homeassistant import config_entries, exceptions
from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_EMAIL,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (  # pylint:disable=unused-import
    CONF_TOPIC_ENVIRONMENT,
    CONF_TOPIC_PRESENCE,
    DOMAIN,
)
from .somnofy import CredentialErrors, SerialNotMatchError, Somnofy

_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class SomnofyFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Somnofy Config Flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL
    init_info = None

    def __init__(self):
        """Initialize the Somnefy flow."""
        self.hostname = None


    async def async_step_dhcp(self, discovery_info: dict):
        """Prepare configuration for a DHCP discovered Somnify device."""
        
        _LOGGER.debug("Found a DHCP match on device %s", discovery_info.get(HOSTNAME).upper())

        self.hostname = discovery_info.get(HOSTNAME)[8:18].upper()

   
        _LOGGER.debug("This is a Somnofy device")

        await self.async_set_unique_id(self.hostname)
        self._abort_if_unique_id_configured()

    
        if self._hostname_already_configured(self.hostname):
            _LOGGER.debug("This is a Somnofy device has already been setup")
            return self.async_abort(reason="already_configured")


        self.hostname = self.hostname
        self.context["title_placeholders"] = {CONF_DEVICE_ID: self.hostname}
        _LOGGER.debug("Sending hostname to the main class %s", self.hostname)
        return await self.async_step_user()
        
    
    def _hostname_already_configured(self, host):
        """See if we already have an entry matching the host."""
        for entry in self._async_current_entries():
            _LOGGER.error(entry.data.get(CONF_DEVICE_ID))
            _LOGGER.error(host)
            if entry.data.get(CONF_DEVICE_ID) == host:
                return True
        return False

    async def async_step_user(self, user_input=None):
        """Handle the user input."""

        errors = {}

        if user_input is not None:

            unique_id = user_input[CONF_DEVICE_ID]
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            websession = async_get_clientsession(self.hass)
            try:
                async with timeout(10):
                    somnofy = Somnofy(
                        user_input[CONF_EMAIL],
                        user_input[CONF_PASSWORD],
                        user_input[CONF_DEVICE_ID],
                        websession,
                    )
                    result = await somnofy.verify_credentials()
                    if result:
                        self.init_info = None
                        return await self.async_step_config(
                            self.init_info, result, user_input
                        )

            except (CredentialErrors):
                errors["base"] = "auth_error"

            except (SerialNotMatchError):
                errors["base"] = "serial_error"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Required(CONF_DEVICE_ID, default=self.hostname): str,
                }
            ),
            errors=errors,
        )

        @staticmethod
        @callback
        def async_get_options_flow(config_entry):
            return OptionsFlowHandler()


        class OptionsFlowHandler(config_entries.OptionsFlow):
            async def async_step_init(self, user_input=None):
                """Manage the options."""
                if user_input is not None:
                    return self.async_create_entry(title="", data=user_input)

                return self.async_show_form(
                    step_id="init",
                    data_schema=vol.Schema(
                        {
                            vol.Required(
                                "show_things",
                                default=self.config_entry.options.get("show_things"),
                            ): bool
                        }
                    ),
                )
    
    

    
    
    async def async_step_config(
        self, user_input=None, api_response=None, p_user_input=None
    ):
        """Config step."""

        if api_response is not None:
            self.api = json.loads(api_response)

        if api_response is not None:
            self.credentials = p_user_input

        _LOGGER.error(self.credentials)

        errors = {}

        changed = False
        if user_input is not None:
            if user_input[CONF_HOST] != self.api["server"]["host"]:
                _LOGGER.error("Host changed")
                self.api["server"]["host"] = user_input[CONF_HOST]
                changed = True

            if user_input[CONF_PORT] != self.api["server"]["port"]:
                _LOGGER.error("Port changed")
                self.api["server"]["port"] = user_input[CONF_PORT]
                changed = True

            if user_input[CONF_USERNAME] != self.api["server"]["username"]:
                _LOGGER.error("username changed")
                self.api["server"]["username"] = user_input[CONF_USERNAME]
                changed = True

            if user_input[CONF_PASSWORD] != self.api["server"]["password"]:
                _LOGGER.error("password changed")
                self.api["server"]["password"] = user_input[CONF_PASSWORD]
                changed = True

            if user_input[CONF_TOPIC_ENVIRONMENT] != self.api["services"][0]["topic"]:
                _LOGGER.error("environment topic changed")
                self.api["services"][0]["topic"] = user_input[CONF_TOPIC_ENVIRONMENT]
                changed = True

            if user_input[CONF_TOPIC_PRESENCE] != self.api["services"][1]["topic"]:
                _LOGGER.error("presence topic changed")
                self.api["services"][1]["topic"] = user_input[CONF_TOPIC_PRESENCE]
                changed = True

            if changed is False:
                return self.async_create_entry(
                    title="Somnofy Non-Contact Smart Sleep Monitor",
                    data={
                        "device_id": self.credentials[CONF_DEVICE_ID],
                        "email": self.credentials[CONF_EMAIL],
                        "password": self.credentials[CONF_PASSWORD],
                        "user_input": user_input,
                    },
                )
            else:
                websession = async_get_clientsession(self.hass)
                try:
                    async with timeout(10):
                        somnofy = Somnofy(
                            self.credentials["email"],
                            self.credentials["password"],
                            self.credentials["device_id"],
                            websession,
                        )
                        result = await somnofy.setSettings(
                            user_input[CONF_HOST],
                            user_input[CONF_PORT],
                            user_input[CONF_USERNAME],
                            user_input[CONF_PASSWORD],
                            user_input[CONF_TOPIC_ENVIRONMENT],
                            user_input[CONF_TOPIC_PRESENCE],
                        )
                        if result:
                            return self.async_create_entry(
                                title="Somnofy Non-Contact Smart Sleep Monitor - "
                                + self.credentials[CONF_DEVICE_ID],
                                data={
                                    "data_response": result,
                                    "input": self.credentials,
                                    "api": self.api,
                                },
                            )

                except (CredentialErrors):
                    errors["base"] = "auth_error"

        data_schema = {
            vol.Required(CONF_HOST, default=self.api["server"]["host"]): str,
            vol.Optional(CONF_PORT, default=self.api["server"]["port"]): int,
            vol.Optional(CONF_USERNAME, default=self.api["server"]["username"]): str,
            vol.Optional(CONF_PASSWORD, default=self.api["server"]["password"]): str,
            vol.Required(
                CONF_TOPIC_ENVIRONMENT, default=self.api["services"][0]["topic"]
            ): str,
            vol.Required(
                CONF_TOPIC_PRESENCE, default=self.api["services"][1]["topic"]
            ): str,
        }

        return self.async_show_form(
            step_id="config",
            data_schema=vol.Schema(data_schema),
            errors=errors,
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidHost(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname."""
