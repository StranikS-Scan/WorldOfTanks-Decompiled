# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/mechanic_commands/__init__.py
from vehicles.mechanics.mechanic_commands.custom_integrations import MechanicCommandsLogger
from vehicles.mechanics.mechanic_commands.mechanic_events import MechanicCommandsEvents
from vehicles.mechanics.mechanic_commands.mechanic_interfaces import IMechanicCommandsComponent, IMechanicCommandsEvents, IMechanicCommandsListener, IMechanicCommandsListenerLogic
__all__ = ('IMechanicCommandsComponent', 'IMechanicCommandsEvents', 'IMechanicCommandsListener', 'IMechanicCommandsListenerLogic', 'MechanicCommandsEvents', 'MechanicCommandsLogger', 'createMechanicCommandsEvents')

def createMechanicCommandsEvents():
    mechanicCommandsEvents = MechanicCommandsEvents()
    MechanicCommandsLogger().subscribeTo(mechanicCommandsEvents)
    return mechanicCommandsEvents
