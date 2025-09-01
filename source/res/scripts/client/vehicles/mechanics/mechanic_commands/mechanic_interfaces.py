# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/mechanic_commands/mechanic_interfaces.py
import typing
from vehicles.components.component_events import IComponentEvents, IComponentListener
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


class IMechanicCommandsEvents(IComponentEvents, IMechanicCommandsEventsLogic):
    pass


class IMechanicCommandsListenerLogic(object):

    def onMechanicCommand(self, command):
        pass


class IMechanicCommandsListener(IComponentListener, IMechanicCommandsListenerLogic):
    pass
