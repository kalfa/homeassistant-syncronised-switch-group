"""Synchronised Switch group"""
from voluptuous import Schema
from .synchronised_switch import *

from homeassistant.components.light import PLATFORM_SCHEMA as LIGHT_PLATFORM_SCHEMA

LIGHT_PLATFORM_SCHEMA = LIGHT_PLATFORM_SCHEMA.extend(schema=DOMAIN_PLATFORM_SCHEMA)
