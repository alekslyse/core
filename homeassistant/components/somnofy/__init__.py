"""The Detailed Hello World Push integration."""
import asyncio
import logging
import voluptuous as vol


from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_NAME, EVENT_HOMEASSISTANT_STOP, CONF_DEVICE_ID
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, DATA_HASS_CONFIG

_LOGGER = logging.getLogger(__name__)

# List of platforms to support. There should be a matching .py file for each,
# eg <cover.py> and <sensor.py>
PLATFORMS = ["sensor"]

_LOGGER.debug("Setting up somnofy sensors")

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.Schema({vol.Required(CONF_DEVICE_ID): cv.string})},
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Set up the Somnofy component."""

    hass.data[DATA_HASS_CONFIG] = config

    if DOMAIN not in config:
        return True

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_IMPORT},
            data=config[DOMAIN],
        )
    )

    return True



async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up somnofy from a config entry."""
    # Store an instance of the "connecting" class that does the work of speaking
    # with your actual devices.
  

  

 
    hass.data.setdefault(DOMAIN, {})

    
  

    

    # This creates each HA object for each platform your device requires.
    # It's done by calling the `async_setup_entry` function in each platform module.
    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True


async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(config_entry, platform)
                for platform in PLATFORMS
            ]
        )
    )

    if unload_ok:

        return unload_ok
