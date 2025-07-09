# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/spin_guns/system_interfaces.py
from events_handler import EventsHandler, eventHandler

class IGunSpinningEvents(object):
    onDestroy = None
    onSpinFactorUpdate = None
    onSpinningActivation = None
    onSpinningDeactivation = None

    def destroy(self):
        pass

    def lateSubscribe(self, listener):
        raise NotImplementedError

    def processTick(self):
        raise NotImplementedError

    def updateSpinningActiveStatus(self, isActive):
        raise NotImplementedError


class IGunSpinningListener(EventsHandler):

    def subscribe(self, events):
        self._subscribeToEvents(events)

    @eventHandler
    def onDestroy(self, events):
        self._unsubscribeFromEvents(events)

    def onSpinFactorUpdate(self, spinFactor):
        pass

    def onSpinningActivation(self):
        pass

    def onSpinningDeactivation(self):
        pass
