"""Config Flow definitions for Synchronised Switch group
"""

from typing import Any

from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import SUPPORTED_DOMAINS, DOMAIN

# pylint: disable=unused-argument,abstract-method,fixme

DATA_FORM_SCHEMA = vol.Schema(
    {
        vol.Required("name"): cv.string,
        vol.Required("master_entity"): cv.entities_domain(SUPPORTED_DOMAINS),
        vol.Required("entities"): cv.entities_domain(SUPPORTED_DOMAINS),
    }
)


class SynchronisedSwitchGroupConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Synchronised Switch Group config flow."""

    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(self, info: dict[str, Any] | None = None):
        if info is not None:
            # TODO: user input should be processed here
            pass

        return self.async_show_form(step_id="user", data_schema=DATA_FORM_SCHEMA)

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        """Recongiguration step for ConfigFlow"""
        # https://developers.home-assistant.io/blog/2024/03/21/config-entry-reconfigure-step/
        # TODO: user input should be processed here
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=DATA_FORM_SCHEMA,
        )
