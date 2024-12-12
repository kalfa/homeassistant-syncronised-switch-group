"""Constants for Synchronised Switch Group"""


from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from homeassistant.helpers import config_validation as cv

from homeassistant.const import (
    CONF_NAME
)

import voluptuous as vol

DOMAIN = "synchronised_switch"
PLATFORM_NAME = "synchronised_switch"
CONF_MASTER = "master_entity"
CONF_SLAVES = "entities"



# schema is the same of the GroupSwitch schema, with the addition of
# master_entity
PLATFORM_SCHEMA =     {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_MASTER): cv.entity_domain([SWITCH_DOMAIN, LIGHT_DOMAIN]),
        vol.Required(CONF_SLAVES): cv.entities_domain([SWITCH_DOMAIN, LIGHT_DOMAIN]),
    }

