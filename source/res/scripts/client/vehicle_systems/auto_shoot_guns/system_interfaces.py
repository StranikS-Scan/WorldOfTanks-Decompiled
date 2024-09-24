# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/auto_shoot_guns/system_interfaces.py
import typing
from events_handler import EventsHandler, eventHandler

class IAutoShootingEvents(object):
    onDestroy = None
    onAppearanceReady = None
    onBurstActivation = None
    onBurstDeactivation = None
    onContinuousBurstActivation = None
    onContinuousBurstDeactivation = None
    onContinuousBurstUpdate = None
    onDiscreteShot = None
    onShotRateUpdate = None

    def destroy(self):
        pass

    def lateSubscribe(self, listener):
        raise NotImplementedError

    def processAppearanceReady(self):
        raise NotImplementedError

    def processDiscreteShot(self):
        raise NotImplementedError

    def updateAutoShootingStatus(self, stateStatus):
        raise NotImplementedError


class IAutoShootingListener(EventsHandler):

    def subscribe(self, events):
        self._subscribeToEvents(events)

    @eventHandler
    def onDestroy(self, events):
        self._unsubscribeFromEvents(events)

    def onAppearanceReady(self):
        pass

    def onBurstActivation(self):
        pass

    def onBurstDeactivation(self):
        pass

    def onContinuousBurstActivation(self):
        pass

    def onContinuousBurstDeactivation(self):
        pass

    def onContinuousBurstUpdate(self):
        pass

    def onDiscreteShot(self):
        pass

    def onShotRateUpdate(self, rate):
        pass
