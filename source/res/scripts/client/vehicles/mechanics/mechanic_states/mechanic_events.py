# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/mechanic_states/mechanic_events.py
from __future__ import absolute_import
import typing
import weakref
from events_containers.common.containers import ClientEventsContainer
from events_containers.components.common import ClientComponentEventsDebugger
from vehicles.mechanics.mechanic_states.mechanic_interfaces import IMechanicStatesEventsLogic
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_states.mechanic_interfaces import IMechanicState, IMechanicStatesComponent, IMechanicStatesListener

class MechanicStatesEvents(ClientEventsContainer, IMechanicStatesEventsLogic):

    def __init__(self, component, tickInterval):
        super(MechanicStatesEvents, self).__init__()
        self.__componentRef = weakref.ref(component)
        self.__mechanicState = None
        self.onStatePrepared = self._createLateEvent(self.__lateStatePrepared)
        self.onStateObservation = self._createLateEvent(self.__lateStateObservation)
        self.onStateTransition = self._createEvent()
        self.onStateTick = self._createTimeIntervalEvent(tickInterval, self.__tickState)
        return

    def destroy(self):
        self.__componentRef = self.__mechanicState = None
        super(MechanicStatesEvents, self).destroy()
        return

    def lateSubscribe(self, listener):
        self.__lateStatePrepared(listener.onStatePrepared)
        self.__lateStateObservation(listener.onStateObservation)
        super(MechanicStatesEvents, self).lateSubscribe(listener)

    def processStatePrepared(self):
        self.__mechanicState = self._getComponent().getMechanicState()
        self.onStatePrepared(self.__mechanicState)

    def updateMechanicState(self, state):
        if self._isStateTransition(self.__mechanicState, state):
            self.onStateTransition(self.__mechanicState, state)
        self.__mechanicState = state
        self.onStateObservation(state)

    def _isStateTransition(self, prevState, newState):
        return newState.isTransition(prevState)

    def _getComponent(self):
        return self.__componentRef() if self.__componentRef is not None else None

    def _createEventsDebugger(self):
        return MechanicStatesEventsDebugger(self, self._getComponent())

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


class MechanicStatesEventsDebugger(ClientComponentEventsDebugger):
    IGNORED_EVENTS = ClientComponentEventsDebugger.IGNORED_EVENTS + ('onStateTick', 'onStateTransition')
    _EVENTS_DEBUG_PREFIX = 'MECHANIC_STATE'
