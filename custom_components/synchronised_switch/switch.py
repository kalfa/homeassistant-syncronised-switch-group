"""Synchronised Switch group"""
from .synchronised_switch import *


from homeassistant.components.light import PLATFORM_SCHEMA as SWITCH_PLATFORM_SCHEMA

SWITCH_PLATFORM_SCHEMA = SWITCH_PLATFORM_SCHEMA.extend(schema=DOMAIN_PLATFORM_SCHEMA)
