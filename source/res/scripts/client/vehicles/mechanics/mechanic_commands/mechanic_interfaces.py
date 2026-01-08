# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/mechanic_commands/mechanic_interfaces.py
from __future__ import absolute_import
import typing
from events_containers.common.containers import IClientEventsContainer, IClientEventsContainerListener
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_constants import VehicleMechanicCommand

class IMechanicCommandsComponent(object):

    @property
    def commandsEvents(self):
        raise NotImplementedError


class IMechanicCommandsEventsLogic(object):
    onMechanicCommand = None

    def processMechanicCommand(self, command):
        raise NotImplementedError


class IMechanicCommandsEvents(IClientEventsContainer, IMechanicCommandsEventsLogic):
    pass


class IMechanicCommandsListenerLogic(object):

    def onMechanicCommand(self, command):
        pass


class IMechanicCommandsListener(IClientEventsContainerListener, IMechanicCommandsListenerLogic):
    pass
