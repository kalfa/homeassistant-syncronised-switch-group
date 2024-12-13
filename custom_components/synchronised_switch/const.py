"""Constants for Synchronised Switch Group"""

from typing import Any
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from homeassistant.helpers import config_validation as cv

from homeassistant.const import CONF_NAME

import voluptuous as vol


PLATFORM_NAME = "synchronised_switch"
CONF_MASTER = "master_entity"
CONF_SLAVES = "entities"


DOMAIN = "synchronised_switch"
# The list of DOMAINs supported for entities managed by the group.
# e.g. 'master_entity' and 'entities'
SUPPORTED_DOMAINS = [SWITCH_DOMAIN, LIGHT_DOMAIN]


# schema is the same of the GroupSwitch schema, with the addition of
# master_entity
PLATFORM_SCHEMA: dict[vol.Marker, Any] = {
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_MASTER): cv.entity_domain(SUPPORTED_DOMAINS),
    vol.Required(CONF_SLAVES): cv.entities_domain(SUPPORTED_DOMAINS),
}
