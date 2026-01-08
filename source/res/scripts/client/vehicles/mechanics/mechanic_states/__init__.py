# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/mechanic_states/__init__.py
from __future__ import absolute_import
import typing
from constants import SERVER_TICK_LENGTH
from events_containers.common.container_wrappers import activateEventsContainer
from vehicles.mechanics.mechanic_states.mechanic_events import MechanicStatesEvents
from vehicles.mechanics.mechanic_states.mechanic_interfaces import IMechanicState, IMechanicStatesComponent, IMechanicStatesEvents, IMechanicStatesListener, IMechanicStatesListenerLogic
__all__ = ('IMechanicState', 'IMechanicStatesComponent', 'IMechanicStatesEvents', 'IMechanicStatesListener', 'IMechanicStatesListenerLogic', 'MechanicStatesEvents', 'createMechanicStatesEvents')

@activateEventsContainer()
def createMechanicStatesEvents(component, tickInterval=SERVER_TICK_LENGTH, **_):
    return MechanicStatesEvents(component, tickInterval)
