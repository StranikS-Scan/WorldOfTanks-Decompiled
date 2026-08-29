# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/gun_mechanics/auxiliary_rocket_launcher/__init__.py
from __future__ import absolute_import
from constants import SERVER_TICK_LENGTH
from events_containers.common.container_wrappers import activateEventsContainer
from vehicles.mechanics.gun_mechanics.auxiliary_rocket_launcher.custom_integrations import AuxiliaryRocketLauncherCustomIntegrations
from vehicles.mechanics.gun_mechanics.auxiliary_rocket_launcher.mechanic_events import AuxiliaryRocketLauncherStatesEvents
from vehicles.mechanics.gun_mechanics.auxiliary_rocket_launcher.mechanic_models import AuxiliaryRocketLauncherState, AuxiliaryRocketLauncherAmmoMode, AuxiliaryRocketLauncherAmmoState
__all__ = ('AuxiliaryRocketLauncherState', 'AuxiliaryRocketLauncherAmmoMode', 'AuxiliaryRocketLauncherAmmoState', 'AuxiliaryRocketLauncherStatesEvents', 'createAuxiliaryRocketLauncherStatesEvents')

@activateEventsContainer()
def createAuxiliaryRocketLauncherStatesEvents(component, tickInterval=SERVER_TICK_LENGTH, **_):
    statesEvents = AuxiliaryRocketLauncherStatesEvents(component, tickInterval)
    AuxiliaryRocketLauncherCustomIntegrations(component).subscribeTo(statesEvents)
    return statesEvents
