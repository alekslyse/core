"""Config flow for Somnofy integration."""
import asyncio
import logging
import json

from async_timeout import timeout
import voluptuous as vol
from voluptuous.error import EmailInvalid, LengthInvalid, RequiredFieldInvalid

from homeassistant import config_entries, core, exceptions, data_entry_flow
from homeassistant.const import CONF_DEVICE_ID, CONF_EMAIL, CONF_NAME, CONF_PASSWORD, CONF_HOST, CONF_PORT, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import format_mac

from .const import DOMAIN, CONF_TOPIC_ENVIRONMENT, CONF_TOPIC_PRESENCE  # pylint:disable=unused-import
from .exceptions import ApiError
from .somnofy import Somnofy, CredentialErrors, SerialNotMatchError

_LOGGER = logging.getLogger(__name__)

@config_entries.HANDLERS.register(DOMAIN)
class SomnofyFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Somnofy Config Flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL
    init_info = None

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
                        websession
                    )
                    result = await somnofy.verify_credentials()
                    if result:
                        self.init_info = None
                        return await self.async_step_config(self.init_info, result, somnofy, user_input)

                    
                       

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
                    vol.Required(CONF_DEVICE_ID): str
                }
            ),
            errors=errors,

        )


        
    async def async_step_config(self, user_input=None, api_response=None, somnofy=None, p_user_input = None):
        # Specify items in the order they are to be displayed in the UI
        
        if api_response is not None:
            self.api = json.loads(api_response)

        if api_response is not None:
            self.credentials = p_user_input

        _LOGGER.error(self.credentials)

        errors = {}

        changed = False
        if user_input is not None:
            if user_input[CONF_HOST] != self.api['server']['host']:
                 _LOGGER.error("Host changed")
                 self.api['server']['host'] = user_input[CONF_HOST]
                 changed = True
       
            if user_input[CONF_PORT] != self.api['server']['port']:
                 _LOGGER.error("Port changed")
                 self.api['server']['port'] = user_input[CONF_PORT]
                 changed = True
            
            if user_input[CONF_USERNAME] != self.api['server']['username']:
                 _LOGGER.error("username changed")
                 self.api['server']['username'] = user_input[CONF_USERNAME]
                 changed = True

            if user_input[CONF_PASSWORD] != self.api['server']['password']:
                 _LOGGER.error("password changed")
                 self.api['server']['password'] = user_input[CONF_PASSWORD]
                 changed = True

            if user_input[CONF_TOPIC_ENVIRONMENT] != self.api['services'][0]['topic']:
                 _LOGGER.error("environment topic changed")
                 self.api['services'][0]['topic'] = user_input[CONF_TOPIC_ENVIRONMENT]
                 changed = True

            if user_input[CONF_TOPIC_PRESENCE] != self.api['services'][1]['topic']:
                _LOGGER.error("presence topic changed")
                self.api['services'][1]['topic'] = user_input[CONF_TOPIC_PRESENCE]
                changed = True
    
            if changed is False:
                 return self.async_create_entry(
                        title="Somnofy Sleep Tracker",
                        data={
                            "data_response": self.api
                        },
                    )
            else:
                websession = async_get_clientsession(self.hass)
                try:
                    async with timeout(10):
                        somnofy = Somnofy(
                            self.credentials['email'],
                            self.credentials['password'],
                            self.credentials['device_id'],
                            websession
                        )
                        result = await somnofy.setSettings(user_input[CONF_HOST], user_input[CONF_PORT], user_input[CONF_USERNAME], user_input[CONF_PASSWORD], user_input[CONF_TOPIC_ENVIRONMENT], user_input[CONF_TOPIC_PRESENCE]  )
                        if result:
                             return self.async_create_entry(
                                 title="Somnofy Sleep Tracker",
                                    data={
                                        "data_response": result,
                                        "input": self.credentials,
                                        "api": self.api
                                    },
                                )

                
                except (CredentialErrors):
                    errors["base"] = "auth_error" 
            

            
        
                

  
            
        
        data_schema = {
            vol.Required(CONF_HOST, default=self.api['server']['host']): str,
            vol.Optional(CONF_PORT, default=self.api['server']['port']): int,
            vol.Optional(CONF_USERNAME, default=self.api['server']['username']): str,
            vol.Optional(CONF_PASSWORD, default=self.api['server']['password']): str,
            vol.Required(CONF_TOPIC_ENVIRONMENT, default=self.api['services'][0]['topic']): str,
            vol.Required(CONF_TOPIC_PRESENCE, default=self.api['services'][1]['topic'] ): str,
        }

        


        return self.async_show_form(step_id="config", data_schema=vol.Schema(data_schema), errors=errors, )
        
        


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidHost(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname."""
