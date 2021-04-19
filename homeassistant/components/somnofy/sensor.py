"""Platform for sensor integration."""
import json
import logging

from homeassistant.components import mqtt
from homeassistant.const import CONF_DEVICE_ID
from homeassistant.core import callback
from homeassistant.helpers.entity import Entity
from homeassistant.util import slugify

from .const import DOMAIN
from .definitions import DEFINITIONS

_LOGGER = logging.getLogger(__name__)

_LOGGER.debug("Setting up somnofy sensors")


ATTR_CONDITION_CLASS = "condition_class"
ATTR_CONDITION_TEMPERATURE = "temperature"
ATTR_CONDITION_HUMIDITY = "humidity"


async def async_setup_entry(hass, entry, add_entities):
    """Async somnofy sensor setup entry."""
    serial = entry.data[CONF_DEVICE_ID]
    _LOGGER.debug("LOOK HERE %s", serial)

    topic_environment = str(entry.data["user_input"]["topic_environment"])
    topic_environment = topic_environment.replace("[SN]", serial)
    topic_presence = str(entry.data["user_input"]["topic_presence"])
    topic_presence = topic_presence.replace("[SN]", serial)

    _LOGGER.debug("Listening to environment topic %s", topic_environment)
    _LOGGER.debug("Listening to presence topic %s", topic_presence)

    for entity in DEFINITIONS:
        _LOGGER.debug("Add entity for topic: %s", entity)
        add_entities([SomnofySensor(serial, entity, topic_environment, topic_presence)])

    return True


class SomnofySensor(Entity):
    """Representation of a Somnofy sensor that is updated via MQTT."""

    def __init__(self, serial, entity, topic_e, topic_p):
        """Initialize the sensor."""

        self._env_id = serial + "-" + entity
        self._entity_id = slugify(serial.replace("/", "_"))
        self._entity = entity
        self._topic = "somnofy/" + serial + "/#"
        self._id = serial
        self._name = "Somnofy_" + entity
        self._device_class = None
        self._enable_default = None
        self._unit_of_measurement = None
        self._icon = None
        self._transform = None
        self._state = None
        self._temperature = 0
        self._humidity = 0
        self._pressure = 0
        self._indoor_air_quality = 0
        self._light_ambient = 0
        self._light_red = 0
        self._light_green = 0
        self._light_blue = 0
        self._sound_amplitude = 0
        self._presence = False
        self._duration = 0
        self._value = None
        self._device_class = None
        self._friendly_name = None
        self._unit = None
        self._topic_e = topic_e
        self._topic_p = topic_p

    async def async_added_to_hass(self):
        """Subscribe to MQTT events."""

        _LOGGER.debug("Somnofy got mqtt %s", self._topic)

        @callback
        def message_received(message):
            """Handle new MQTT messages."""

            if self._transform is not None:
                self._state = self._transform(message.payload)
            else:
                self._state = message.payload

            states = json.loads(message.payload)

            _LOGGER.debug("Waiting for %s", self._entity)
            if self._entity in states:
                self._name = DEFINITIONS[self._entity]["name"]
                self._value = states[self._entity]
                if self._entity == "presence":
                    self._icon = DEFINITIONS[self._entity]["icon"][bool(self._entity)]
                else:
                    self._icon = DEFINITIONS[self._entity]["icon"]

                self._device_class = DEFINITIONS[self._entity]["device_class"]
                self._friendly_name = DEFINITIONS[self._entity]["name"]
                self._unit = DEFINITIONS[self._entity]["unit"]

                _LOGGER.debug("New value is %s", self._value)

            if id in states:
                self._duration = states[id]

            self.async_write_ha_state()

        await mqtt.async_subscribe(self.hass, self._topic_e, message_received, 1)
        await mqtt.async_subscribe(self.hass, self._topic_p, message_received, 1)

    @property
    def state(self):
        """Return the current state."""
        return self._value

    @property
    def name(self):
        """Return the current state."""
        return self._friendly_name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._env_id

    @property
    def device_id(self):
        """Return the ID of the physical device this sensor is part of."""
        return self._id

    @property
    def device_info(self):
        """Return the device_info of the device."""
        device_info = {
            "identifiers": {(DOMAIN, self._id)},
            "name": self._id,
            "manufacturer": "Somnofy",
            "model": "Non-Contact Smart Sleep Monitor",
        }
        return device_info

    @property
    def icon(self):
        """Return the icon of this sensor."""
        return self._icon

    @property
    def device_class(self):
        """Return the device_class of this sensor."""
        return self._device_class

    @property
    def unit_of_measurement(self):
        """Return the unit_of_measurement of this sensor."""
        return self._unit


@property
def entity_id(self):
    """Return the entity ID for this sensor."""
    return f"sensor.{self._entity_id}"


@property
def entity_registry_enabled_default(self) -> bool:
    """Return if the entity should be enabled when first added to the entity registry."""
    return self._enable_default
