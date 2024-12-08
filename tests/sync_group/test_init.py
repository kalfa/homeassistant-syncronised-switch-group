"""Test component setup."""
#from typing import Any
#from homeassistant.setup import async_setup_component
from homeassistant import core, setup

#from .utils import MockConfigEntry
from homeassistant.components.light import LightEntity
from homeassistant.helpers import entity_registry as er

from custom_components.synchronised_switch.const import DOMAIN
from custom_components.synchronised_switch.synchronised_switch import SyncSwitchGroup

from homeassistant.const import (
    ATTR_ENTITY_ID,
    STATE_ON,
    STATE_UNKNOWN
)
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.components.group import DOMAIN as GROUP_DOMAIN



async def test_setup_component_with_no_config(hass: core.HomeAssistant) -> None:
    """The component won't be setup if there is not config for the doamin"""
    assert await setup.async_setup_component(hass, DOMAIN, {}) is True

    # No flows started
    assert len(hass.config_entries.flow.async_progress()) == 0

    # No configs stored
    assert DOMAIN not in hass.data



async def test_default_state2(
    hass: core.HomeAssistant, entity_registry: er.EntityRegistry
) -> None:
    """Test switch group default state."""
    hass.states.async_set("switch.tv", "on")
    await setup.async_setup_component(
        hass,
        SWITCH_DOMAIN,
        {
            SWITCH_DOMAIN: {
                "platform": GROUP_DOMAIN,
                "entities": ["switch.tv", "switch.soundbar"],
                "name": "Multimedia Group",
                "unique_id": "unique_identifier",
                "all": "false",
            }
        },
    )
    await hass.async_block_till_done()
    await hass.async_start()
    await hass.async_block_till_done()
   
    #ids = hass.states.async_entity_ids()
    ids: list[State] = hass.states.async_all()
    print(ids)
    raise Exception()

    state = hass.states.get("switch.multimedia_group")
    assert state is not None
    assert state.state == STATE_ON
    assert state.attributes.get(ATTR_ENTITY_ID) == ["switch.tv", "switch.soundbar"]

    entry = entity_registry.async_get("switch.multimedia_group")
    assert entry
    assert entry.unique_id == "unique_identifier"

from homeassistant.helpers.entity import async_generate_entity_id

async def test_default_state3(
    hass: core.HomeAssistant, entity_registry: er.EntityRegistry
) -> None:
    """Test switch group default state."""
    GROUP_NAME = "Sync Group"
    MASTER_ENTITY = "switch.master"
    SECONDARY_ENTITIY = "switch.secondary"

    hass.states.async_set("switch.tv", "on")

    await setup.async_setup_component(
        hass,
        domain=DOMAIN,
        config={
            DOMAIN: {
                "platform": DOMAIN,
                "name": GROUP_NAME,
                "unique_id": "unique_identifier",
                "master-entity": MASTER_ENTITY,
                "entities": [SECONDARY_ENTITIY],
            }
        },
    )

    await hass.async_block_till_done()
    await hass.async_start()
    await hass.async_block_till_done()

    # ensure the entity-id is generated from name (is this a good behaviour?)
    entity_id = async_generate_entity_id(entity_id_format=DOMAIN+'.{}', name=GROUP_NAME, hass=hass)
    state = hass.states.get(entity_id=entity_id)
    assert state is not None, hass.states.async_all()
    assert state.state == STATE_UNKNOWN, hass.states.async_all()
    assert state.attributes.get(ATTR_ENTITY_ID) == [MASTER_ENTITY, SECONDARY_ENTITIY], hass.states.async_all()

    entry = entity_registry.async_get("switch.multimedia_group")
    assert entry
    assert entry.unique_id == "unique_identifier"


    raise Exception()

async def test_sync_group_updates_state_on_mater_change(hass: core.HomeAssistant):
    master = LightEntity(name='master')
    entity = LightEntity(name='slave1')
    s = SyncSwitchGroup(unique_id='fake-group',
                    name='fake-group',
                    master=master.name,
                    entity_ids=[entity.name])
    
    
    await master.async_turn_on()
    await s.async_update_group_state()
    assert s.state == 'on'

    await master.async_turn_off()
    await s.async_update_group_state()
    assert s.state == 'off'


async def test_master_change_state_all_entities_are_updated(hass: core.HomeAssistant):
    ...