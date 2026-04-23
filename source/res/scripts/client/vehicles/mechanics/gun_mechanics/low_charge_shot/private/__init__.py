# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/gun_mechanics/low_charge_shot/private/__init__.py
from __future__ import absolute_import
from constants import LowChargeShotReloadingState
from vehicles.mechanics.gun_mechanics.low_charge_shot.private.mechanic_models import LowChargeShotMechanicState, LowChargeShotAmmoState
from vehicles.mechanics.gun_mechanics.low_charge_shot.private.mechanic_logging import LowChargeShotUILogging
__all__ = ('LowChargeShotMechanicState', 'LowChargeShotAmmoState', 'LowChargeShotUILogging')
DEFAULT_MECHANIC_STATE = LowChargeShotMechanicState(LowChargeShotReloadingState.EMPTY, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
