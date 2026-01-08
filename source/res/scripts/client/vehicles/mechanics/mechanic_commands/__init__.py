# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/mechanic_commands/__init__.py
from __future__ import absolute_import
import typing
from events_containers.common.container_wrappers import activateEventsContainer
from vehicles.mechanics.mechanic_commands.mechanic_events import MechanicCommandsEvents
from vehicles.mechanics.mechanic_commands.mechanic_interfaces import IMechanicCommandsComponent, IMechanicCommandsEvents, IMechanicCommandsListener, IMechanicCommandsListenerLogic
__all__ = ('IMechanicCommandsComponent', 'IMechanicCommandsEvents', 'IMechanicCommandsListener', 'IMechanicCommandsListenerLogic', 'MechanicCommandsEvents', 'createMechanicCommandsEvents')

@activateEventsContainer()
def createMechanicCommandsEvents(component, **_):
    return MechanicCommandsEvents(component)
