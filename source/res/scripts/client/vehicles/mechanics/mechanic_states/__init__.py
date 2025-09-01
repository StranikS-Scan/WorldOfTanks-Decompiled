# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/mechanic_states/__init__.py
from constants import SERVER_TICK_LENGTH
from vehicles.mechanics.mechanic_states.custom_integrations import MechanicStatesLogger
from vehicles.mechanics.mechanic_states.mechanic_events import MechanicStatesEvents
from vehicles.mechanics.mechanic_states.mechanic_interfaces import IMechanicState, IMechanicStatesComponent, IMechanicStatesEvents, IMechanicStatesListener, IMechanicStatesListenerLogic
__all__ = ('IMechanicState', 'IMechanicStatesComponent', 'IMechanicStatesEvents', 'IMechanicStatesListener', 'IMechanicStatesListenerLogic', 'MechanicStatesEvents', 'MechanicStatesLogger', 'createMechanicStatesEvents')

def createMechanicStatesEvents(component, tickInterval=SERVER_TICK_LENGTH):
    mechanicStatesEvents = MechanicStatesEvents(component, tickInterval)
    MechanicStatesLogger().subscribeTo(mechanicStatesEvents)
    return mechanicStatesEvents
