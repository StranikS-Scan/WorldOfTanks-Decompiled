# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/generic_mechanics/sight_pointer/__init__.py
from __future__ import absolute_import
import typing
from constants import SERVER_TICK_LENGTH
from events_containers.common.container_wrappers import activateEventsContainer
from vehicles.mechanics.generic_mechanics.sight_pointer.mechanic_events import SightPointerStatesEvents
from vehicles.mechanics.mechanic_states.mechanic_interfaces import IMechanicStatesComponent
__all__ = ('SightPointerStatesEvents', 'createSightPointerStatesEvents')

@activateEventsContainer()
def createSightPointerStatesEvents(component, tickInterval=SERVER_TICK_LENGTH, **_):
    return SightPointerStatesEvents(component, tickInterval)
