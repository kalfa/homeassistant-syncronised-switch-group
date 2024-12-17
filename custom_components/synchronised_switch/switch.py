"""Synchronised Switch group"""

import logging
from typing import Optional

from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN, PLATFORM_SCHEMA
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import async_generate_entity_id
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import (
    CONF_NAME,
    CONF_ENTITIES,
    DOMAIN,
    PLATFORM_SCHEMA as DOMAIN_PLATFORM_SCHEMA,
)
from .synchronised_switch import SyncSwitchGroup

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(DOMAIN_PLATFORM_SCHEMA)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: Optional[  # pylint: disable=unused-argument
        DiscoveryInfoType
    ] = None,
) -> None:
    """Setup platform via config yaml"""

    _LOGGER.info(
        f"{DOMAIN} platform setup with name=%s entities=%s",
        config[CONF_NAME],
        config[CONF_ENTITIES],
    )

    # being a virtual entity, grouping other entities,
    # this can work both as entity-id and unique-id
    entity_id = async_generate_entity_id(
        entity_id_format=SWITCH_DOMAIN + ".{}", name=config[CONF_NAME], hass=hass
    )

    setup_entity = SyncSwitchGroup(
        name=config[CONF_NAME],
        unique_id=entity_id,
        entity_ids=config[CONF_ENTITIES],
    )

    async_add_entities([setup_entity], update_before_add=False)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize Synchronised Switch Group entities, from UI added configuraitons

    https://developers.home-assistant.io/docs/config_entries_index/
    """
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

    async_add_entities([setup_entity], update_before_add=True)
