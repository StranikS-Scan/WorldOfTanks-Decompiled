# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/gun_mechanics/temperature/overheat_gun/__init__.py
from __future__ import absolute_import
from constants import OVERHEAT_GUN_STATE
from vehicles.mechanics.gun_mechanics.temperature.overheat_gun.mechanic_interfaces import IOverheatGunComponentParams, IOverheatGunMechanicState
from vehicles.mechanics.gun_mechanics.temperature.overheat_gun.mechanic_models import OverheatGunComponentParams, OverheatGunMechanicState, OverheatGunAmmoState
__all__ = ('IOverheatGunComponentParams', 'IOverheatGunMechanicState', 'OverheatGunComponentParams', 'OverheatGunMechanicState', 'OverheatGunAmmoState', 'DEFAULT_OVERHEAT_COMPONENT_PARAMS', 'DEFAULT_OVERHEAT_MECHANIC_STATE')
DEFAULT_OVERHEAT_COMPONENT_PARAMS = OverheatGunComponentParams(1.0, 0.0, 0.0)
DEFAULT_OVERHEAT_MECHANIC_STATE = OverheatGunMechanicState(OVERHEAT_GUN_STATE.IDLE, DEFAULT_OVERHEAT_COMPONENT_PARAMS)
