"""Utilities for tests"""
from typing import Any

from homeassistant import core
from homeassistant import config_entries

import homeassistant.util.ulid as ulid_util



class MockConfigEntry(config_entries.ConfigEntry):
    """Helper for creating config entries that adds some defaults."""

    def __init__(
        self,
        *,
        data=None,
        disabled_by=None,
        discovery_keys=None,
        domain="test",
        entry_id=None,
        minor_version=1,
        options=None,
        pref_disable_new_entities=None,
        pref_disable_polling=None,
        reason=None,
        source=config_entries.SOURCE_USER,
        state=None,
        title="Mock Title",
        unique_id=None,
        version=1,
    ) -> None:
        """Initialize a mock config entry."""
        discovery_keys = discovery_keys or {}
        kwargs = {
            "data": data or {},
            "disabled_by": disabled_by,
            "discovery_keys": discovery_keys,
            "domain": domain,
            "entry_id": entry_id or ulid_util.ulid_now(),
            "minor_version": minor_version,
            "options": options or {},
            "pref_disable_new_entities": pref_disable_new_entities,
            "pref_disable_polling": pref_disable_polling,
            "title": title,
            "unique_id": unique_id,
            "version": version,
        }
        if source is not None:
            kwargs["source"] = source
        if state is not None:
            kwargs["state"] = state
        super().__init__(**kwargs)
        if reason is not None:
            object.__setattr__(self, "reason", reason)

    def add_to_hass(self, hass: core.HomeAssistant) -> None:
        """Test helper to add entry to hass."""
        hass.config_entries._entries[self.entry_id] = self

    def add_to_manager(self, manager: config_entries.ConfigEntries) -> None:
        """Test helper to add entry to entry manager."""
        manager._entries[self.entry_id] = self

    def mock_state(
        self,
        hass: core.HomeAssistant,
        state: config_entries.ConfigEntryState,
        reason: str | None = None,
    ) -> None:
        """Mock the state of a config entry to be used in tests.

        Currently this is a wrapper around _async_set_state, but it may
        change in the future.

        It is preferable to get the config entry into the desired state
        by using the normal config entry methods, and this helper
        is only intended to be used in cases where that is not possible.

        When in doubt, this helper should not be used in new code
        and is only intended for backwards compatibility with existing
        tests.
        """
        self._async_set_state(hass, state, reason)

    async def start_reauth_flow(
        self,
        hass: core.HomeAssistant,
        context: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Start a reauthentication flow."""
        if self.entry_id not in hass.config_entries._entries:
            raise ValueError("Config entry must be added to hass to start reauth flow")
        return await start_reauth_flow(hass, self, context, data)

    async def start_reconfigure_flow(
        self,
        hass: core.HomeAssistant,
        *,
        show_advanced_options: bool = False,
    ) -> config_entries.ConfigFlowResult:
        """Start a reconfiguration flow."""
        if self.entry_id not in hass.config_entries._entries:
            raise ValueError(
                "Config entry must be added to hass to start reconfiguration flow"
            )
        return await hass.config_entries.flow.async_init(
            self.domain,
            context={
                "source": config_entries.SOURCE_RECONFIGURE,
                "entry_id": self.entry_id,
                "show_advanced_options": show_advanced_options,
            },
        )



async def start_reauth_flow(
    hass: core.HomeAssistant,
    entry: config_entries.ConfigEntry,
    context: dict[str, Any] | None = None,
    data: dict[str, Any] | None = None,
) -> config_entries.ConfigFlowResult:
    """Start a reauthentication flow for a config entry.

    This helper method should be aligned with `ConfigEntry._async_init_reauth`.
    """
    return await hass.config_entries.flow.async_init(
        entry.domain,
        context={
            "source": config_entries.SOURCE_REAUTH,
            "entry_id": entry.entry_id,
            "title_placeholders": {"name": entry.title},
            "unique_id": entry.unique_id,
        }
        | (context or {}),
        data=entry.data | (data or {}),
    )
