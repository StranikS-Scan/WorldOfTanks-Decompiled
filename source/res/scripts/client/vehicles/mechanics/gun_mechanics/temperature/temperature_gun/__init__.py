# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/gun_mechanics/temperature/temperature_gun/__init__.py
from __future__ import absolute_import
from constants import TEMPERATURE_GUN_STATE
from vehicles.mechanics.gun_mechanics.temperature.temperature_gun.mechanic_interfaces import ITemperatureGunComponentParams, ITemperatureGunMechanicState
from vehicles.mechanics.gun_mechanics.temperature.temperature_gun.mechanic_models import TemperatureGunComponentParams, TemperatureGunMechanicState, TemperatureGunAmmoState
__all__ = ('ITemperatureGunComponentParams', 'ITemperatureGunMechanicState', 'TemperatureGunComponentParams', 'TemperatureGunMechanicState', 'TemperatureGunAmmoState', 'DEFAULT_TEMPERATURE_COMPONENT_PARAMS', 'DEFAULT_TEMPERATURE_MECHANIC_STATE')
DEFAULT_TEMPERATURE_COMPONENT_PARAMS = TemperatureGunComponentParams(100.0, 1.0, 1.0)
DEFAULT_TEMPERATURE_MECHANIC_STATE = TemperatureGunMechanicState(TEMPERATURE_GUN_STATE.IDLE, 0, 0.0, 0.0, 0.0, 1.0, True, DEFAULT_TEMPERATURE_COMPONENT_PARAMS)
