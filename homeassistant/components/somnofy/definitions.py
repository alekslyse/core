"""Definitions for Somnofy sensors added to MQTT."""
from homeassistant.const import (
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_TEMPERATURE,
    LIGHT_LUX,
    PERCENTAGE,
    PRESSURE_HPA,
    TEMP_CELSIUS,
)

from .const import SOUND_AMPLITUDE

DEFINITIONS = {
    "temperature": {
        "name": "Templerature",
        "device_class": DEVICE_CLASS_TEMPERATURE,
        "unit": TEMP_CELSIUS,
        "icon": "mdi:thermometer",
    },
    "humidity": {
        "name": "Relative humidity",
        "device_class": DEVICE_CLASS_HUMIDITY,
        "unit": PERCENTAGE,
        "icon": "mdi:water-percent",
    },
    "pressure": {
        "name": "Atmospheric pressure",
        "device_class": PRESSURE_HPA,
        "unit": PRESSURE_HPA,
        "icon": "mdi:gauge",
    },
    "indoor_air_quality": {
        "name": "Indoor air quality index",
        "device_class": None,
        "unit": None,
        "icon": "mdi:gauge",
        "range": {
            tuple([0, 50]): "Excellent",
            tuple([51, 100]): "Good",
            tuple([101, 150]): "Lightly polluted",
            tuple([151, 200]): "Moderately polluted",
            tuple([201, 250]): "Heavily polluted",
            tuple([251, 350]): "Severly polluted",
            tuple([351, 500]): "Extremely polluted",
        },
    },
    "light_red": {
        "name": "Red light",
        "device_class": LIGHT_LUX,
        "unit": LIGHT_LUX,
        "icon": "mdi:brightness-percent",
    },
    "light_green": {
        "name": "Green light",
        "device_class": LIGHT_LUX,
        "unit": LIGHT_LUX,
        "icon": "mdi:brightness-percent",
    },
    "light_blue": {
        "name": "Blue light",
        "device_class": LIGHT_LUX,
        "unit": LIGHT_LUX,
        "icon": "mdi:brightness-percent",
    },
    "sound_amplitude": {
        "name": "Sound amplitude",
        "device_class": SOUND_AMPLITUDE,
        "unit": SOUND_AMPLITUDE,
        "icon": "mdi:brightness-percent",
    },
    "presence": {
        "name": "Current presence state",
        "device_class": None,
        "unit": None,
        "icon": {True: "mdi:bed", False: "mdi:bed-empty"},
    },
    "duration": {
        "name": "Current presence state duration",
        "device_class": None,
        "unit": None,
        "icon": "mdi:clock",
    },
}
