"""Synchronised Switch group"""
import sys
from copy import deepcopy
from functools import partial
import logging
from typing import Any, Iterable, Optional

from homeassistant.components.switch import SwitchEntity
from homeassistant.components.group.entity import GroupEntity

from homeassistant.helpers import entity_registry as er
from homeassistant.core import Event, EventStateChangedData, callback, HomeAssistant

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
)
from homeassistant.helpers.entity import async_generate_entity_id

#from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
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
    DOMAIN,
    PLATFORM_SCHEMA as DOMAIN_PLATFORM_SCHEMA,
)

_LOGGER = logging.getLogger(__name__)


class SyncSwitchGroup(GroupEntity, SwitchEntity):
    """A Synchronised Group of Switches"""

    _attr_available = False
    _attr_should_poll = False

    def __init__(
        self,
        unique_id: Optional[str],
        name: Optional[str],
        master: str,
        entity_ids: list[str],
    ) -> None:
        _LOGGER.info(
            "instantiating SyncSwitchGroup synchronised switch with %s %s %s %s",
            unique_id,
            name,
            master,
            entity_ids,
        )
        self.mode = all
        self._entity_ids = entity_ids
        self._master_id = master

        self._attr_name = name
        self._attr_extra_state_attributes = {ATTR_ENTITY_ID: [master] + entity_ids[:]}
        self._attr_unique_id = unique_id

        # ToggleEntity which is the parent of SwitchEntity defines
        # self._attr_is_on: bool|None
        # self._attr_available: bool
    
    @property
    def name(self):
        return self._attr_name
        

    @property
    def extra_state_attributes(self):
        return deepcopy(self._attr_extra_state_attributes)
    
        


    def turn_off(self, **kwargs):
        ...


    def turn_on(self, **kwargs):
        ...

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Forward the turn_on command to all switches in the group."""

        _LOGGER.debug(
            "Forwarded turn_on command to master %s and slaves %s",
            self._master_id,
            self._entity_ids,
        )

        await self.hass.services.async_call(
            LIGHT_DOMAIN,
            SERVICE_TURN_ON,
            {ATTR_ENTITY_ID: [self._master_id] + self._entity_ids},
            blocking=True,
            context=self._context,
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Forward the turn_of command to all switches in the group."""

        _LOGGER.debug(
            "Forwarded turn_off command to master %s and slaves %s",
            self._master_id,
            self._entity_ids,
        )

        await self.hass.services.async_call(
            LIGHT_DOMAIN,
            SERVICE_TURN_OFF,
            {ATTR_ENTITY_ID: [self._master_id] + self._entity_ids},
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
        if (state := self.hass.states.get(self._master_id)) is not None:
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
            for entity_id in self._entity_ids
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



@callback
def _master_changed(group_entity: SyncSwitchGroup, event: Event[EventStateChangedData]) -> None:
    entity_id = event.data["entity_id"]
    old_state = event.data["old_state"]
    new_state = event.data["new_state"]
    
    print('master chaged:', entity_id, old_state, new_state, file=sys.stderr)


@callback
def _slave_changed(group_entity: SyncSwitchGroup, event: Event[EventStateChangedData]) -> None:
    entity_id = event.data["entity_id"]
    old_state = event.data["old_state"]
    new_state = event.data["new_state"]
    
    print('a slave chaged:', entity_id, old_state, new_state, file=sys.stderr)


def _subscribe_group_to_change_of_state_events(hass: HomeAssistant, sync_group_entity: SyncSwitchGroup, master: str, entities: Iterable[str]):
    async_track_state_change_event(hass, entity_ids=master, action=partial(_master_changed, sync_group_entity))
    async_track_state_change_event(hass, entity_ids=entities, action=partial(_slave_changed, sync_group_entity))

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: Optional[DiscoveryInfoType] = None,  # pylint: disable=unused-argument
) -> None:
    """Setup platform via config yaml"""
    
    _LOGGER.info(
        "async_setup_platform synchronised switch with %s %s %s %s",
        config.get(CONF_UNIQUE_ID, "not-present-id"),
        config.get(CONF_NAME, "not-present-name"),
        config[CONF_MASTER],
        config[CONF_SLAVES],
    )

    setup_entity = SyncSwitchGroup(
                name=config[CONF_NAME],
                unique_id=config.get(CONF_UNIQUE_ID, None),
                master=config[CONF_MASTER],
                entity_ids=config[CONF_SLAVES],
            )

    attrs: ConfigType[str, str | None] = {'name': setup_entity.name}
           
    entity_id = async_generate_entity_id(entity_id_format=LIGHT_DOMAIN+'.{}',
                                         name=config[CONF_NAME],
                                         hass=hass)
    hass.states.async_set(entity_id=entity_id, new_state=setup_entity.state,
                          attributes=attrs)
    async_add_entities([setup_entity], update_before_add=True)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize Synchronised Switch Group entities, from UI added configuraitons
    
    https://developers.home-assistant.io/docs/config_entries_index/
    """
    raise Exception("sync_group.async_setup_entry called")
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
    setup_entity = SyncSwitchGroup(
                unique_id=config_entry.entry_id,
                name=config_entry.title,
                master=master,
                entity_ids=entities,
            )
    attrs: ConfigType[str, str | None] = {'name': setup_entity.name}
    attrs.update(setup_entity.extra_state_attributes)

    print('foo', setup_entity.extra_state_attributes)             
    hass.states.async_set(entity_id=f'{DOMAIN}.{setup_entity.name}', new_state=setup_entity.state,
                          attributes=attrs)
    
    _subscribe_group_to_change_of_state_events(hass=hass, sync_group_entity=setup_entity,
                                               master=master, entities=entities)

    async_add_entities([setup_entity], update_before_add=True)
