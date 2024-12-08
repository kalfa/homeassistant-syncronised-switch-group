"""Constants for Synchronised Switch Group"""


from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from homeassistant.helpers import config_validation as cv

from homeassistant.const import (
    CONF_NAME,
    CONF_UNIQUE_ID,
)


import voluptuous as vol





DOMAIN = "synchronised_switch"
PLATFORM_NAME = "synchronised_switch"
CONF_MASTER = "master_entity"
CONF_SLAVES = "entities"
DEFAULT_NAME= "Synchronised Switch Group"


# schema is the same of the GroupSwitch schema, with the addition of
# master_entity
PLATFORM_SCHEMA =     {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_UNIQUE_ID): cv.string,
        vol.Required(CONF_MASTER): cv.entity_domain([SWITCH_DOMAIN, LIGHT_DOMAIN]),
        vol.Required(CONF_SLAVES): cv.entities_domain([SWITCH_DOMAIN, LIGHT_DOMAIN]),
    }

