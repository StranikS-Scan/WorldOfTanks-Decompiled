# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/gun_mechanics/low_charge_shot/public/__init__.py
from __future__ import absolute_import
from constants import SERVER_TICK_LENGTH, LowChargeShotReloadingState
from events_containers.common.container_wrappers import activateEventsContainer
from vehicles.mechanics.gun_mechanics.low_charge_shot.public.mechanic_models import LowChargeShotPublicMechanicState
from vehicles.mechanics.gun_mechanics.low_charge_shot.public.mechanic_events import LowChargeShotPublicStatesEvents
__all__ = ('LowChargeShotPublicMechanicState', 'LowChargeShotPublicStatesEvents', 'createLowChargeShotPublicStatesEvents')
DEFAULT_MECHANIC_STATE = LowChargeShotPublicMechanicState(LowChargeShotReloadingState.EMPTY, 0.0, 0.0)

@activateEventsContainer()
def createLowChargeShotPublicStatesEvents(component, tickInterval=SERVER_TICK_LENGTH, **_):
    return LowChargeShotPublicStatesEvents(component, tickInterval)
