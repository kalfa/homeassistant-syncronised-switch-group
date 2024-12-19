"""Synchronised Switch group"""

from html import entities
import logging

from typing import Any, Literal
from functools import partial

from propcache import cached_property

from homeassistant.core import (
    Event,
    EventStateChangedData,
    State,
    callback,
)

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.event import async_track_state_change_event

from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_ON,
    SERVICE_TURN_OFF,
    STATE_ON,
    STATE_OFF,
)

from .const import SUPPORTED_DOMAINS

_LOGGER = logging.getLogger(__name__)


class SyncSwitchGroup(SwitchEntity):  # pylint: disable=abstract-method
    """A Synchronised Group of Switches"""

    _attr_available: bool = True
    _attr_is_on: bool | None = False
    _attr_should_poll: bool = False
    _attr_has_entity_name: bool = True
    # _attr_state: StateType = STATE_UNKNOWN

    def __init__(
        self,
        unique_id: str,
        name: str,
        entity_ids: list[str],
    ) -> None:
        assert (
            len(entity_ids) > 1
        ), f"group should have at least two entities ({len(entity_ids)})"

        _LOGGER.info(
            (
                "instantiating %s synchronised switch with "
                "unique-id='%s' name='%s' master='%s' entities='%s'"
            ),
            self.__class__.__name__,
            unique_id,
            name,
            entity_ids[0],
            entity_ids[1:],
        )
        # internally the first entity is elected master, and the state is synchronised around it.
        self._master_id = entity_ids[0]
        self._entity_ids = entity_ids[1:]

        self._attr_name = name
        # self._attr_extra_state_attributes = {ATTR_ENTITY_ID: [master] + entity_ids}
        self._attr_unique_id = unique_id
        self._attr_entity_id = unique_id

        # callable to unsubscribe from event handlers. by default a NOOP.
        self.__unsubscribe = lambda: None

    @cached_property
    def name(self):
        return self._attr_name

    @cached_property
    def entity_id(self) -> str:
        """The entity-id of the entity object"""
        return self.unique_id

    # @property
    # def extra_state_attributes(self):
    #    return deepcopy(self._attr_extra_state_attributes)

    async def async_added_to_hass(self):

        unsub_master = async_track_state_change_event(
            self.hass,
            entity_ids=self._master_id,
            action=partial(_master_changed, self),
        )
        unsub_entities = async_track_state_change_event(
            self.hass, entity_ids=self._entity_ids, action=partial(_slave_changed, self)
        )

        # change the group state to the master's state and udpate the other entities.
        await self.__async_initialize_state()
        await self.async_update()

        def unsubscribe():
            _LOGGER.debug("Unsubscribing master and slaves entities events handlers")
            unsub_master()
            unsub_entities()

        self.__unsubscribe = unsubscribe

        _LOGGER.debug("%s added to hass", self.entity_id)

    async def async_will_remove_from_hass(self):
        self.hass.states.async_remove(self.entity_id, self._context)
        self.__unsubscribe()

        _LOGGER.debug(
            "%s about to be removed from hass. subscriptions un-registered.",
            self.entity_id,
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Forward the turn_on command to all switches in the group."""

        _LOGGER.debug(
            "turn_on command to group entities %s, %s",
            self._master_id,
            ", ".join(self._entity_ids),
        )

        await self.async_master_switch(to_state=STATE_ON)
        await self.async_update()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Forward the turn_of command to all switches in the group."""

        _LOGGER.debug(
            "turn_off command to group entities %s, %s",
            self._master_id,
            ", ".join(self._entity_ids),
        )

        await self.async_master_switch(to_state=STATE_OFF)
        await self.async_update()

    async def async_master_switch(
        self, to_state: Literal["on"] | Literal["off"]
    ) -> None:
        """Change the master entity to the specified state and update group state.

        A call to async_update() is necessary to change the state of all the
        other entities in the group.
        """
        _LOGGER.debug(
            "Changing master %s to %s",
            self._master_id,
            to_state,
        )

        if to_state == self.state:
            return

        if to_state == STATE_ON:
            service_name = SERVICE_TURN_ON
        elif to_state == STATE_OFF:
            service_name = SERVICE_TURN_OFF
        else:
            _LOGGER.debug(
                "Unsupported to update states to %s (%s). Skipping update.",
                self.state,
                type(self.state),
            )
            return

        await self.hass.services.async_call(
            domain=self._master_id.split(".", 1)[0],
            service=service_name,
            service_data={ATTR_ENTITY_ID: [self._master_id]},
            blocking=True,
        )

        self._attr_is_on = to_state == STATE_ON
        # self._attr_state = to_state

    async def __async_initialize_state(self):
        """[Internal] Called only once in object lifecycle, when entity is added to HASS

        Initialises its state according to the master's state.

        From this moment, the two states are in sync.

        A call to async_update() is necessary to change the state of all the
        other entities in the group.
        """
        state = self.hass.states.get(self._master_id)
        self._attr_is_on = state.state == STATE_ON if state is not None else STATE_OFF

    async def async_update(self):
        """Update entities according to group's state.

        The update won't happen if the current group state is not 'on' or 'off'.

        Update HA state after the udpate.
        """
        # It has been initialised to a non none state.
        assert self.state is not None, "group state should be on or off, never None"

        master_state = self.hass.states.get(self._master_id)
        if master_state is None:
            _LOGGER.error("master %s is in None state", self._master_id)
            return

        if self.state != master_state.state:
            _LOGGER.error(
                "group %s state and master %s state differ. this should not happen.",
                self.entity_id,
                self._master_id,
            )

        _LOGGER.debug(
            "Synchronise group's entities %s to current group's state (%s)",
            ", ".join(self._entity_ids),
            self.state,
        )

        if self.state == STATE_ON:
            service_name = SERVICE_TURN_ON
        elif self.state == STATE_OFF:
            service_name = SERVICE_TURN_OFF
        else:
            _LOGGER.debug(
                "Unsupported group's state '%s' (type:%s) for async_update(). Skipping update.",
                self.state,
                type(self.state),
            )
            return

        for supported_domain in SUPPORTED_DOMAINS:
            await self.hass.services.async_call(
                domain=supported_domain,
                service=service_name,
                service_data={
                    ATTR_ENTITY_ID: [
                        entity
                        for entity in self._entity_ids
                        if entity.startswith(f"{supported_domain}.")
                    ]
                },
                blocking=True,
            )

        self.async_write_ha_state()


@callback
def _master_changed(
    group_entity: SyncSwitchGroup, event: Event[EventStateChangedData]
) -> None:
    """Update the group's state as consequence of a change of the master entity status"""
    entity_id = event.data["entity_id"]
    old_state: State | None = event.data["old_state"]
    new_state: State = event.data["new_state"]

    if old_state is None:
        # <https://www.home-assistant.io/docs/configuration/events/#state_changed>
        # state set for the first time
        # this does not need to trigger a change of state for this object
        return

    if old_state and new_state.state == old_state.state:
        # no change
        _LOGGER.debug(
            "%s, old state and new state are the same: %s. ignore.",
            entity_id,
            new_state.state,
        )
        return

    if new_state.state == group_entity.state:
        _LOGGER.debug(
            "master %s already in %s state. skip update triggered by %s",
            entity_id,
            new_state.state,
            new_state.context.id,
        )
        return

    _LOGGER.debug(
        "master entity %s changed state from=%s to=%s triggered by %s. Updating group state",
        entity_id,
        old_state.state if old_state else old_state,
        new_state.state,
        new_state.context.id if new_state.context else "uknown-event",
    )

    async_change_group_state = getattr(group_entity, f"async_turn_{new_state.state}")

    if async_change_group_state is not None:
        group_entity.hass.create_task(async_change_group_state())
    else:
        _LOGGER.fatal(
            "master %s changed to unrecognised state '%s': it should be on/off only",
            entity_id,
            new_state.state,
        )


@callback
def _slave_changed(
    group_entity: SyncSwitchGroup, event: Event[EventStateChangedData]
) -> None:
    """Update the group's state as consequence of a change of the master entity status

    To avoid useless events and loops, skip when there is no change
    from the old to the new state, or from the current group state to the new state.

    Otherwise, update the master state, to trigger the update.
    The event handler for master will manage the rest of the update flow.
    """
    entity_id = event.data["entity_id"]
    old_state: State | None = event.data["old_state"]
    new_state: State | None = event.data["new_state"]

    if old_state is None:
        # <https://www.home-assistant.io/docs/configuration/events/#state_changed>
        # state set for the first time
        # this does not need to trigger a change of state for this object
        return

    assert new_state.state in [STATE_OFF, STATE_ON], "state should be on/off only"

    if old_state and old_state.state == new_state.state:
        # no change
        _LOGGER.debug(
            "%s, old state and new state are the same: %s. ignore.",
            entity_id,
            new_state.state,
        )
        return

    # This check avoid infinite loops and useless events in general:
    # slave sends event which changes master, which updates slaves
    # which sends event which changes master...
    if new_state.state == group_entity.state:
        # the entity moved to the same state of the group, ignore
        _LOGGER.debug(
            "%s change to state %s, but group is already in this state. ignore",
            entity_id,
            new_state.state,
        )
        return

    _LOGGER.debug(
        "entity %s chaged state from=%s to=%s. updating group master entity.",
        entity_id,
        old_state.state if old_state else old_state,
        new_state.state,
    )
    # trigger a change of state for master, triggering master's state change events
    group_entity.hass.create_task(
        group_entity.async_master_switch(to_state=new_state.state)
    )
