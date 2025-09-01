# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/mechanic_states/mechanic_events.py
import typing
import weakref
from Event import LateEvent, SafeEvent
from gui.shared.utils.TimeInterval import TimeIntervalEvent
from vehicles.components.component_events import ComponentEvents
from vehicles.mechanics.mechanic_states.mechanic_interfaces import IMechanicStatesEventsLogic
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_states.mechanic_interfaces import IMechanicState, IMechanicStatesComponent, IMechanicStatesListener

class MechanicStatesEvents(ComponentEvents, IMechanicStatesEventsLogic):

    def __init__(self, component, tickInterval):
        super(MechanicStatesEvents, self).__init__()
        self.__component = weakref.proxy(component)
        self.__mechanicState = None
        em = self._eventsManager
        self.onStatePrepared = LateEvent(self.__lateStatePrepared, em)
        self.onStateObservation = LateEvent(self.__lateStateObservation, em)
        self.onStateTransition = SafeEvent(em)
        self.onStateTick = TimeIntervalEvent(tickInterval, self.__tickState, em)
        return

    def destroy(self):
        self.__component = None
        self.__mechanicState = None
        super(MechanicStatesEvents, self).destroy()
        return

    def lateSubscribe(self, listener):
        self.__lateStatePrepared(listener.onStatePrepared)
        self.__lateStateObservation(listener.onStateObservation)
        listener.subscribeTo(self)

    def processStatePrepared(self):
        self.__mechanicState = self.__component.getMechanicState()
        self.onStatePrepared(self.__mechanicState)

    def updateMechanicState(self, state):
        if self._isStateTransition(self.__mechanicState, state):
            self.onStateTransition(self.__mechanicState, state)
        self.__mechanicState = state
        self.onStateObservation(state)

    def _isStateTransition(self, prevState, newState):
        return newState.isTransition(prevState)

    def __lateStatePrepared(self, handler):
        if self.__mechanicState is not None:
            handler(self.__mechanicState)
        return

    def __lateStateObservation(self, handler):
        if self.__mechanicState is not None:
            handler(self.__mechanicState)
        return

    def __tickState(self):
        if self.__mechanicState is not None:
            self.onStateTick(self.__mechanicState)
        return
