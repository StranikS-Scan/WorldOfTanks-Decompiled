# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/mechanic_states/mechanic_interfaces.py
from __future__ import absolute_import
from events_containers.common.containers import IClientEventsContainer, IClientEventsContainerListener

class IMechanicState(object):

    def isTransition(self, other):
        raise NotImplementedError


class IMechanicStatesComponent(object):

    @property
    def statesEvents(self):
        raise NotImplementedError

    def getMechanicState(self):
        raise NotImplementedError


class IMechanicStatesEventsLogic(object):
    onStatePrepared = None
    onStateObservation = None
    onStateTransition = None
    onStateTick = None

    def processStatePrepared(self):
        raise NotImplementedError

    def updateMechanicState(self, state):
        raise NotImplementedError


class IMechanicStatesEvents(IClientEventsContainer, IMechanicStatesEventsLogic):
    pass


class IMechanicStatesListenerLogic(object):

    def onStatePrepared(self, state):
        pass

    def onStateObservation(self, state):
        pass

    def onStateTransition(self, prevState, newState):
        pass

    def onStateTick(self, state):
        pass


class IMechanicStatesListener(IClientEventsContainerListener, IMechanicStatesListenerLogic):
    pass
