
from typing import Any
from homeassistant import config_entries

from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import DOMAIN

from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN

DATA_FORM_SCHEMA = vol.Schema(
            {
                vol.Required('name'): cv.string,
                vol.Required("master_entity"): cv.entities_domain([SWITCH_DOMAIN, LIGHT_DOMAIN]),
                vol.Required("entities"): cv.entities_domain([SWITCH_DOMAIN, LIGHT_DOMAIN])
             }
            )

class SynchronisedSwitchGroupConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Synchronised Switch Group config flow."""
    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(self, info):
        if info is not None:
            pass  # TODO: process info

        return self.async_show_form(
            step_id="user", data_schema=DATA_FORM_SCHEMA)

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=DATA_FORM_SCHEMA,
        )