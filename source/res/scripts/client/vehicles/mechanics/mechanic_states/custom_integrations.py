# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/mechanic_states/custom_integrations.py
import typing
import logging
from events_handler import eventHandler
from vehicles.components.component_events import ComponentListener
from vehicles.mechanics.mechanic_states.mechanic_interfaces import IMechanicStatesListenerLogic
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_states.mechanic_interfaces import IMechanicState, IMechanicStatesEvents
_logger = logging.getLogger(__name__)

class MechanicStatesLogger(ComponentListener, IMechanicStatesListenerLogic):

    @eventHandler
    def onComponentEventsDestroy(self, events):
        _logger.debug('onComponentEventsDestroy %s', events)
        super(MechanicStatesLogger, self).onComponentEventsDestroy(events)

    @eventHandler
    def onStatePrepared(self, state):
        _logger.debug('onStatePrepared %s', state)

    @eventHandler
    def onStateObservation(self, state):
        _logger.debug('onStateObservation %s', state)

    @eventHandler
    def onStateTransition(self, prevState, newState):
        _logger.debug('onStateTransition %s %s', prevState, newState)
