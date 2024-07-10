# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/auto_shoot_guns/shooting_events.py
import weakref
import typing
import BigWorld
from auto_shoot_guns.auto_shoot_guns_common import AutoShootGunState
from constants import SERVER_TICK_LENGTH
from Event import EventManager, Event, LateEvent
from helpers.CallbackDelayer import CallbackDelayer
from vehicle_systems.auto_shoot_guns.system_interfaces import IAutoShootingEvents
if typing.TYPE_CHECKING:
    from AutoShootGunController import AutoShootGunController
    from vehicle_systems.auto_shoot_guns.system_interfaces import IAutoShootingListener
CONTINUOUS_ACTIVATION_DELTA = 0.0

class AutoShootingEvents(CallbackDelayer, IAutoShootingEvents):

    def __init__(self, controller):
        super(AutoShootingEvents, self).__init__()
        self.__controller = weakref.proxy(controller)
        self.__isAppearanceReady = self.__isBurstInProgress = False
        self.__lastDiscreteShotTime = 0.0
        self.__eventsManager = EventManager()
        self.onDestroy = Event(self.__eventsManager)
        self.onAppearanceReady = LateEvent(self.__lateAppearanceReady, self.__eventsManager)
        self.onBurstActivation = LateEvent(self.__lateBurstActivation, self.__eventsManager)
        self.onContinuousBurstActivation = LateEvent(self.__lateContinuousBurstActivation, self.__eventsManager)
        self.onShotRateUpdate = LateEvent(self.__lateShotRateUpdate, self.__eventsManager)
        self.onBurstDeactivation = Event(self.__eventsManager)
        self.onContinuousBurstDeactivation = Event(self.__eventsManager)
        self.onContinuousBurstUpdate = Event(self.__eventsManager)
        self.onDiscreteShot = Event(self.__eventsManager)

    def destroy(self):
        self.onDestroy(self)
        self.__controller = None
        self.__eventsManager.clear()
        self.__lastDiscreteShotTime = 0.0
        super(AutoShootingEvents, self).destroy()
        return

    def lateSubscribe(self, listener):
        self.__lateAppearanceReady(listener.onAppearanceReady)
        self.__lateShotRateUpdate(listener.onShotRateUpdate)
        self.__lateContinuousBurstActivation(listener.onContinuousBurstActivation)
        self.__lateBurstActivation(listener.onBurstActivation)
        listener.subscribe(self)

    def processAppearanceReady(self):
        self.__isAppearanceReady = True
        self.onAppearanceReady()

    def processDiscreteShot(self):
        self.__lastDiscreteShotTime = BigWorld.time()
        self.onShotRateUpdate(self.__controller.getShotRatePerSecond())
        self.onDiscreteShot()

    def updateAutoShootingStatus(self, stateStatus):
        isBurstInProgress = self.__isBurstInProgress
        state = stateStatus.state if stateStatus else AutoShootGunState.NONE
        isContinuousInProgress = self.hasDelayedCallback(self.__updateContinuousBurst)
        if isBurstInProgress and state not in AutoShootGunState.SHOOTING_STATES:
            self.__deactivateBurst(isContinuousInProgress)
            self.__isBurstInProgress = False
            return
        isContinuousBurst = state == AutoShootGunState.CONTINUOUS_SHOOTING
        if not isBurstInProgress and state in AutoShootGunState.SHOOTING_STATES:
            self.__activateBurst(isContinuousBurst)
            self.__isBurstInProgress = True
            return
        if isContinuousInProgress != isContinuousBurst:
            self.__switchBurstPhase(isContinuousBurst)

    def __activateBurst(self, isContinuousBurst):
        if isContinuousBurst:
            self.__activateContinuousBurst()
        self.onBurstActivation()

    def __activateContinuousBurst(self):
        self.__lastDiscreteShotTime = BigWorld.time()
        self.stopCallback(self.__tryActivateContinuousBurst)
        self.delayCallback(SERVER_TICK_LENGTH, self.__updateContinuousBurst)
        self.onShotRateUpdate(self.__controller.getShotRatePerSecond())
        self.onContinuousBurstActivation()

    def __deactivateBurst(self, isContinuousInProgress):
        self.stopCallback(self.__tryActivateContinuousBurst)
        if isContinuousInProgress:
            self.__deactivateContinuousBurst()
        self.onBurstDeactivation()

    def __deactivateContinuousBurst(self):
        self.__lastDiscreteShotTime = BigWorld.time()
        self.stopCallback(self.__updateContinuousBurst)
        self.onContinuousBurstDeactivation()

    def __switchBurstPhase(self, isContinuousBurst):
        if isContinuousBurst:
            if self.__needDelayContinuousBurst():
                self.delayCallback(CONTINUOUS_ACTIVATION_DELTA, self.__tryActivateContinuousBurst)
            else:
                self.__activateContinuousBurst()
        else:
            self.__deactivateContinuousBurst()

    def __updateContinuousBurst(self):
        self.onShotRateUpdate(self.__controller.getShotRatePerSecond())
        self.onContinuousBurstUpdate()
        return SERVER_TICK_LENGTH

    def __needDelayContinuousBurst(self):
        return self.__lastDiscreteShotTime + self.__controller.getGroupShotInterval() > BigWorld.time()

    def __tryActivateContinuousBurst(self):
        return CONTINUOUS_ACTIVATION_DELTA if self.__needDelayContinuousBurst() else self.__activateContinuousBurst()

    def __lateAppearanceReady(self, handler):
        if self.__isAppearanceReady:
            handler()

    def __lateBurstActivation(self, handler):
        if self.__isBurstInProgress:
            handler()

    def __lateContinuousBurstActivation(self, handler):
        if self.hasDelayedCallback(self.__updateContinuousBurst):
            handler()

    def __lateShotRateUpdate(self, handler):
        if self.__controller is not None:
            handler(self.__controller.getShotRatePerSecond())
        return
