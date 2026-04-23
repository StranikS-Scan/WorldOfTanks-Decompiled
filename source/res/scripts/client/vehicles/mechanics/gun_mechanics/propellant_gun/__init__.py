# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/gun_mechanics/propellant_gun/__init__.py
from __future__ import absolute_import
from constants import PROPELLANT_GUN_STATE, SERVER_TICK_LENGTH
from events_containers.common.container_wrappers import activateEventsContainer
from vehicles.mechanics.gun_mechanics.propellant_gun.mechanic_interfaces import IPropellantGunComponentParams, IPropellantGunMechanicState
from vehicles.mechanics.gun_mechanics.propellant_gun.mechanic_models import PropellantGunComponentParams, PropellantGunMechanicState
from vehicles.mechanics.gun_mechanics.propellant_gun.mechanic_events import PropellantStatesEvents
__all__ = ('IPropellantGunComponentParams', 'IPropellantGunMechanicState', 'PropellantGunComponentParams', 'PropellantGunMechanicState', 'PropellantStatesEvents', 'DEFAULT_PROPELLANT_GUN_PARAMS', 'DEFAULT_PROPELLANT_GUN_MECHANIC_STATE', 'createPropellantStatesEvents')
DEFAULT_PROPELLANT_GUN_PARAMS = PropellantGunComponentParams(10.0, 10.0, 100.0, 200.0, [], set())
DEFAULT_PROPELLANT_GUN_MECHANIC_STATE = PropellantGunMechanicState(state=PROPELLANT_GUN_STATE.IDLE, stageID=0, chargeProgress=0.0, isOvercharge=False, isSwitchCooldownActive=False, updateTime=0.0, isForbiddenShell=False, lastShotTimestamp=0.0, lastShotCharge=0.0, params=DEFAULT_PROPELLANT_GUN_PARAMS)

@activateEventsContainer()
def createPropellantStatesEvents(component, tickInterval=SERVER_TICK_LENGTH, **_):
    return PropellantStatesEvents(component, tickInterval)
