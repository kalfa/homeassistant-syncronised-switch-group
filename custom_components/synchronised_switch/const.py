"""Constants for Synchronised Switch Group"""

from typing import Any
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from homeassistant.helpers import config_validation as cv

from homeassistant.const import CONF_NAME, CONF_ENTITIES

import voluptuous as vol


PLATFORM_NAME = "synchronised_switch"


DOMAIN = "synchronised_switch"
# The list of DOMAINs supported for entities managed by the group.
SUPPORTED_DOMAINS = [SWITCH_DOMAIN, LIGHT_DOMAIN]

# schema is the same of the GroupSwitch schema
PLATFORM_SCHEMA: dict[vol.Marker, Any] = {
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_ENTITIES): cv.entities_domain(SUPPORTED_DOMAINS),
}
