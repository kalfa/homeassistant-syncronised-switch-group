"""Component initialisation"""
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry, ConfigType
from homeassistant.helpers.entity import async_generate_entity_id
from homeassistant.helpers.discovery import async_load_platform
from .const import DOMAIN, CONF_NAME

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Anova from a config entry."""
    raise Exception('debug: __init__.async_setup_entry called')
    await hass.config_entries.async_forward_entry_setups(entry, [DOMAIN])
    return True




async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Setup the component."""
    
    if DOMAIN not in config:
        raise Exception(f'debug: yaml has no {DOMAIN}')
        return True
    
    entity_config = config[DOMAIN]
    entity_id = async_generate_entity_id(entity_id_format=DOMAIN+'.{}',
                                         name=entity_config[CONF_NAME],
                                         hass=hass)
    hass.states.async_set(entity_id=entity_id, new_state=STATE_UNKNOWN)
    
    #await async_load_platform(hass=hass, component=DOMAIN, platform=DOMAIN, discovered={}, hass_config=config)
    
    return True
