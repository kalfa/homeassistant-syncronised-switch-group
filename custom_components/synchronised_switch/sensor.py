"""Synchronised Switch group"""

import logging
from typing import Optional, Any

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA


from homeassistant.helpers.entity import ToggleEntity
# from homeassistant.components.light import LightEntity
# from homeassistant.components.group.entity import GroupEntity


from homeassistant.helpers import config_validation as cv, entity_registry as er

from homeassistant.config_entries import ConfigEntry

from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback


from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from homeassistant.const import (
    CONF_NAME,
    CONF_UNIQUE_ID,
    ATTR_ENTITY_ID,
    SERVICE_TURN_ON,
    SERVICE_TURN_OFF,
    STATE_UNKNOWN,
    STATE_UNAVAILABLE,
    STATE_ON,
)

from .const import (
    CONF_MASTER,
    CONF_SLAVES,
    DEFAULT_NAME,
)

_LOGGER = logging.getLogger(__name__)


# schema is the same of the GroupSwitch schema, with the addition of
# master_entity
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_UNIQUE_ID): cv.string,
        vol.Required(CONF_MASTER): cv.entity_domain([SWITCH_DOMAIN, LIGHT_DOMAIN]),
        vol.Required(CONF_SLAVES): cv.entities_domain([SWITCH_DOMAIN, LIGHT_DOMAIN]),
    }
)


class SyncSwitchGroup(ToggleEntity):
    """A Synchronised Group of Switches"""

    def __init__(
        self,
        unique_id: Optional[str],
        name: Optional[str],
        master: str,
        entity_ids: list[str],
    ) -> None:
        _LOGGER.info(
            "instantiatingSyncSwitchGroup synchronised switch with %s %s %s %s",
            unique_id,
            name,
            master,
            entity_ids,
        )
        self.__entity_ids = entity_ids
        self.__master_id = master

        self._attr_name = name
        self._attr_extra_state_attributes = {ATTR_ENTITY_ID: [master] + entity_ids[:]}
        self._attr_unique_id = unique_id

        # ToggleEntity which is the parent of SwitchEntity defines
        # self._attr_is_on: bool|None
        # self._attr_available: bool

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Forward the turn_on command to all switches in the group."""

        _LOGGER.debug(
            "Forwarded turn_on command to master %s and slaves %s",
            self.__master_id,
            self.__entity_ids,
        )

        await self.hass.services.async_call(
            LIGHT_DOMAIN,
            SERVICE_TURN_ON,
            {ATTR_ENTITY_ID: [self.__master_id] + self.__entity_ids},
            blocking=True,
            context=self._context,
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Forward the turn_of command to all switches in the group."""

        _LOGGER.debug(
            "Forwarded turn_off command to master %s and slaves %s",
            self.__master_id,
            self.__entity_ids,
        )

        await self.hass.services.async_call(
            LIGHT_DOMAIN,
            SERVICE_TURN_OFF,
            {ATTR_ENTITY_ID: [self.__master_id] + self.__entity_ids},
            blocking=True,
            context=self._context,
        )

    @callback
    def async_update_group_state(self) -> None:
        """Query all members and determine the switch group state.

        The state of the entity is always the state of the defined master
        entity, independently from the other "slave" entities.

        Sync all avail entities to the state of the master, if they are
        not already in sync with it.

        An entity can be out of sync if they are switched as entity
        i.e. not using this group entity
        """
        if (state := self.hass.states.get(self.__master_id)) is not None:
            master_state = state.state
        else:
            # Set group as unavailable if the master is unavail
            self._attr_is_on = None
            self._attr_available = master_state == STATE_UNAVAILABLE
            return

        if master_state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            self._attr_is_on = None
        else:
            self._attr_is_on = master_state == STATE_ON

        # entities that have their state not agreeing with the master entity
        # and are not unavail/unknown either
        not_in_sync_entities = [
            entity_id
            for entity_id in self.__entity_ids
            if (state := self.hass.states.get(entity_id)) is not None
            and state.state not in (STATE_UNAVAILABLE, STATE_UNAVAILABLE)
            and state.state != master_state
        ]

        # resync all avail entities which are not in sync
        self.hass.services.call(
            LIGHT_DOMAIN,
            SERVICE_TURN_ON if master_state == STATE_ON else SERVICE_TURN_OFF,
            {ATTR_ENTITY_ID: not_in_sync_entities},
            blocking=True,
            context=self._context,
        )


async def async_setup_platform(
    hass: HomeAssistant,  # pylint: disable=unused-argument
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: Optional[DiscoveryInfoType] = None,  # pylint: disable=unused-argument
) -> None:
    """Set up the sensor platform."""
    _LOGGER.info(
        "async_setup_platform synchronised switch with %s %s %s %s",
        config.get(CONF_UNIQUE_ID, "non present id"),
        config.get(CONF_NAME, "non present name"),
        config[CONF_MASTER],
        config[CONF_SLAVES],
    )

    async_add_entities(
        [
            SyncSwitchGroup(
                name=config[CONF_NAME],
                unique_id=config.get(CONF_UNIQUE_ID, None),
                master=config[CONF_MASTER],
                entity_ids=config[CONF_SLAVES],
            )
        ],
        update_before_add=True,
    )


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize Switch Group config entry."""
    registry = er.async_get(hass)
    entities = er.async_validate_entity_ids(registry, config_entry.options[CONF_SLAVES])
    master = er.async_validate_entity_id(registry, config_entry.options[CONF_MASTER])

    _LOGGER.info(
        "async_setup_entry synchronised switch %s %s %s %s",
        config_entry.entry_id,
        config_entry.title,
        master,
        entities,
    )
    async_add_entities(
        [
            SyncSwitchGroup(
                unique_id=config_entry.entry_id,
                name=config_entry.title,
                master=master,
                entity_ids=entities,
            )
        ]
    )
