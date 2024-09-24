# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/twin_guns/system_interfaces.py
import typing
from events_handler import EventsHandler, eventHandler

class ITwinGunShootingEvents(object):
    onDestroy = None
    onAppearanceReady = None
    onActiveGunsUpdate = None
    onAnimatedGunsUpdate = None
    onDiscreteShot = None
    onDoubleShot = None

    def destroy(self):
        pass

    def lateSubscribe(self, listener):
        raise NotImplementedError

    def processAppearanceReady(self):
        raise NotImplementedError

    def processNextGunsUpdate(self, gunIndexes):
        raise NotImplementedError

    def processDiscreteShot(self, gunIndex):
        raise NotImplementedError

    def processDoubleShot(self):
        raise NotImplementedError


class ITwinShootingListener(EventsHandler):

    def subscribe(self, events):
        self._subscribeToEvents(events)

    @eventHandler
    def onDestroy(self, events):
        self._unsubscribeFromEvents(events)

    def onAppearanceReady(self):
        pass

    def onActiveGunsUpdate(self, gunIndexes):
        pass

    def onAnimatedGunsUpdate(self, gunIndexes):
        pass

    def onDiscreteShot(self, gunIndex):
        pass

    def onDoubleShot(self, gunIndexes):
        pass
