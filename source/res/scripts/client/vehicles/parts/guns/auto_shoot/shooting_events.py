# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/parts/guns/auto_shoot/shooting_events.py
from __future__ import absolute_import
import typing
import BigWorld
import math_utils
from cgf_events import gun_events
from constants import SERVER_TICK_LENGTH
from events_handler import eventHandler
from helpers.CallbackDelayer import CallbackDelayer
from vehicles.parts.guns.auto_shoot.guns_interfaces import IAutoShootingEventsLogic, IAutoShootingListenerLogic
from vehicles.parts.guns.common import GunShootingEvents, GunShootingCGFIntegration, GunShootingEventsDebugger
if typing.TYPE_CHECKING:
    from vehicles.parts.guns.auto_shoot.guns_interfaces import IAutoShootGunComponent, IAutoShootGunComponentState
CONTINUOUS_ACTIVATION_DELTA = 0.0

class AutoShootingEvents(GunShootingEvents, IAutoShootingEventsLogic):

    def __init__(self, component):
        super(AutoShootingEvents, self).__init__(component)
        self.__componentState = None
        self.__lastDiscreteShotTime = 0.0
        self.__callbackDelayer = CallbackDelayer()
        self.onBurstActivation = self._createLateEvent(self.__lateBurstActivation)
        self.onContinuousBurstActivation = self._createLateEvent(self.__lateContinuousBurstActivation)
        self.onShotRateUpdate = self._createLateEvent(self.__lateShotRateUpdate)
        self.onBurstDeactivation = self._createEvent()
        self.onContinuousBurstDeactivation = self._createEvent()
        self.onContinuousBurstUpdate = self._createEvent()
        return

    def destroy(self):
        self.__destroyBurst()
        self.__callbackDelayer.destroy()
        self.__lastDiscreteShotTime = 0.0
        super(AutoShootingEvents, self).destroy()

    def processAppearanceReady(self):
        super(AutoShootingEvents, self).processAppearanceReady()
        self.__componentState = self._getComponent().getComponentState()
        self.onShotRateUpdate(self.__componentState.getShotRatePerSecond())

    def processDiscreteShot(self, gunIndex):
        self.__lastDiscreteShotTime = BigWorld.time()
        super(AutoShootingEvents, self).processDiscreteShot(gunIndex)

    def updateAutoShootingState(self, componentState):
        newShotRatePerSecond = componentState.getShotRatePerSecond()
        prevComponentState, self.__componentState = self.__componentState, componentState
        if not math_utils.almostEqual(newShotRatePerSecond, prevComponentState.getShotRatePerSecond()):
            self.onShotRateUpdate(newShotRatePerSecond)
        isContinuousInProgress = self.__callbackDelayer.hasDelayedCallback(self.__updateContinuousBurst)
        if prevComponentState.isShooting() and not componentState.isShooting():
            self.__deactivateBurst(isContinuousInProgress)
            return
        isContinuousBurst = componentState.isContinuousShooting()
        if not prevComponentState.isShooting() and componentState.isShooting():
            self.__activateBurst(isContinuousBurst)
            return
        if isContinuousInProgress != isContinuousBurst:
            self.__switchBurstPhase(isContinuousBurst)

    def _createCGFIntegration(self):
        return AutoShootingCGFIntegration(self, self._getComponent())

    def _createEventsDebugger(self):
        return AutoShootingEventsDebugger(self, self._getComponent())

    def _lateSubscribe(self, listener):
        super(AutoShootingEvents, self)._lateSubscribe(listener)
        self.__lateShotRateUpdate(listener.onShotRateUpdate)
        self.__lateContinuousBurstActivation(listener.onContinuousBurstActivation)
        self.__lateBurstActivation(listener.onBurstActivation)

    def __activateBurst(self, isContinuousBurst):
        if isContinuousBurst:
            self.__activateContinuousBurst()
        self.onBurstActivation()

    def __activateContinuousBurst(self):
        self.__lastDiscreteShotTime = BigWorld.time()
        self.__callbackDelayer.stopCallback(self.__tryActivateContinuousBurst)
        self.__callbackDelayer.delayCallback(SERVER_TICK_LENGTH, self.__updateContinuousBurst)
        self.onContinuousBurstActivation()

    def __deactivateBurst(self, isContinuousInProgress):
        self.__callbackDelayer.stopCallback(self.__tryActivateContinuousBurst)
        if isContinuousInProgress:
            self.__deactivateContinuousBurst()
        self.onBurstDeactivation()

    def __deactivateContinuousBurst(self):
        self.__lastDiscreteShotTime = BigWorld.time()
        self.__callbackDelayer.stopCallback(self.__updateContinuousBurst)
        self.onContinuousBurstDeactivation()

    def __destroyBurst(self):
        if self.__componentState is not None and self.__componentState.isShooting():
            self.__deactivateBurst(self.__callbackDelayer.hasDelayedCallback(self.__updateContinuousBurst))
        return

    def __switchBurstPhase(self, isContinuousBurst):
        if isContinuousBurst:
            if self.__needDelayContinuousBurst():
                self.__callbackDelayer.delayCallback(CONTINUOUS_ACTIVATION_DELTA, self.__tryActivateContinuousBurst)
            else:
                self.__activateContinuousBurst()
        else:
            self.__deactivateContinuousBurst()

    def __updateContinuousBurst(self):
        self.onContinuousBurstUpdate()
        return SERVER_TICK_LENGTH

    def __needDelayContinuousBurst(self):
        return self.__lastDiscreteShotTime + self.__componentState.getGroupShotInterval() > BigWorld.time()

    def __tryActivateContinuousBurst(self):
        return CONTINUOUS_ACTIVATION_DELTA if self.__needDelayContinuousBurst() else self.__activateContinuousBurst()

    def __lateBurstActivation(self, handler):
        if self.__componentState is not None and self.__componentState.isShooting():
            handler()
        return

    def __lateContinuousBurstActivation(self, handler):
        if self.__callbackDelayer.hasDelayedCallback(self.__updateContinuousBurst):
            handler()

    def __lateShotRateUpdate(self, handler):
        if self.__componentState is not None:
            handler(self.__componentState.getShotRatePerSecond())
        return


class AutoShootingCGFIntegration(GunShootingCGFIntegration, IAutoShootingListenerLogic):

    @eventHandler
    def onContinuousBurstActivation(self):
        gun_events.postVehicularContinuousBurstEvent(self._spaceID, self._vehicleID, self._slotName, True)

    @eventHandler
    def onContinuousBurstDeactivation(self):
        gun_events.postVehicularContinuousBurstEvent(self._spaceID, self._vehicleID, self._slotName, False)

    @eventHandler
    def onShotRateUpdate(self, rate):
        gun_events.postVehicularFireRateChangedEvent(self._spaceID, self._vehicleID, self._slotName, rate)


class AutoShootingEventsDebugger(GunShootingEventsDebugger):
    IGNORED_EVENTS = GunShootingEventsDebugger.IGNORED_EVENTS + ('onContinuousBurstUpdate',)
    _EVENTS_DEBUG_PREFIX = 'AUTO_GUN'
