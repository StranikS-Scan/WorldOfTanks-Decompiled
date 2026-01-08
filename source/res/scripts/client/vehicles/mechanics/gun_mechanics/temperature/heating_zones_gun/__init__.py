# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/gun_mechanics/temperature/heating_zones_gun/__init__.py
from __future__ import absolute_import
from constants import HEATING_ZONES_GUN_STATE
from vehicles.mechanics.gun_mechanics.temperature.heating_zones_gun.mechanic_interfaces import IHeatingZonesGunComponentParams, IHeatingZonesGunMechanicState
from vehicles.mechanics.gun_mechanics.temperature.heating_zones_gun.mechanic_models import HeatingZonesGunComponentParams, HeatingZonesGunMechanicState
__all__ = ('IHeatingZonesGunComponentParams', 'IHeatingZonesGunMechanicState', 'HeatingZonesGunComponentParams', 'HeatingZonesGunMechanicState', 'DEFAULT_HEATING_ZONES_COMPONENT_PARAMS', 'DEFAULT_HEATING_ZONES_MECHANIC_STATE')
DEFAULT_HEATING_ZONES_COMPONENT_PARAMS = HeatingZonesGunComponentParams(1.0, 1.0)
DEFAULT_HEATING_ZONES_MECHANIC_STATE = HeatingZonesGunMechanicState(HEATING_ZONES_GUN_STATE.IDLE, DEFAULT_HEATING_ZONES_COMPONENT_PARAMS)
