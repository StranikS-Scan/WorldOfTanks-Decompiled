# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/auto_shoot_guns/auto_shoot_ctrl.py
import BigWorld
import CommandMapping
from AutoShootGunController import getPlayerVehicleAutoShootGunController
from auto_shoot_guns.auto_shoot_guns_common import BURST_VERIFYING_DELTA, BURST_CONFIRMATION_DELTA
from debug_utils import LOG_WARNING
from gui.battle_control.arena_info.interfaces import IAutoShootController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.auto_shoot_guns.auto_shoot_helpers import AUTO_SHOOT_DEV_KEYS, AUTO_SHOOT_DEV_BURST_CLAMP, AutoShootDevCommand
from helpers.CallbackDelayer import CallbackDelayer
from math_common import isAlmostEqual
from math_utils import clamp
from shared_utils import findFirst

class AutoShootController(IAutoShootController, CallbackDelayer):

    def stopControl(self):
        self.clearCallbacks()

    def isBurstActive(self):
        ctrl = getPlayerVehicleAutoShootGunController()
        isBurstActive = self.hasDelayedCallback(self.__scheduledBurstVerification)
        return isBurstActive or ctrl is not None and ctrl.isShooting()

    def getControllerID(self):
        return BATTLE_CTRL_ID.AUTO_SHOOT_CTRL

    def processShootCmd(self):
        if not self.hasDelayedCallback(self.__scheduledBurstVerification):
            self.delayCallback(BURST_VERIFYING_DELTA, self.__scheduledBurstVerification)
            self.__verifyBurst()

    def _isShootingCmdActive(self):
        return CommandMapping.g_instance.isActive(CommandMapping.CMD_CM_SHOOT)

    def _sendBurstCancellation(self):
        ctrl = getPlayerVehicleAutoShootGunController()
        if ctrl is not None:
            ctrl.cell.deactivateShooting()
        return

    def _sendBurstConfirmation(self):
        ctrl = getPlayerVehicleAutoShootGunController()
        if ctrl is not None:
            ctrl.cell.activateShooting()
        return

    def __cancelBurst(self):
        self.stopCallback(self.__scheduledBurstConfirmation)
        self._sendBurstCancellation()
        BigWorld.player().dropStopUntilFireMode()

    def __scheduledBurstConfirmation(self):
        self._sendBurstConfirmation()
        return BURST_CONFIRMATION_DELTA

    def __scheduledBurstVerification(self):
        return self.__verifyBurst(isRepeat=True) if self._isShootingCmdActive() else self.__cancelBurst()

    def __verifyBurst(self, isRepeat=False):
        player = BigWorld.player()
        if player is None or not player.isOnArena or not player.isVehicleAlive:
            self.stopCallback(self.__scheduledBurstConfirmation)
            return
        elif not player.verifyShooting(isRepeat):
            self.stopCallback(self.__scheduledBurstConfirmation)
            return BURST_VERIFYING_DELTA
        elif not self.hasDelayedCallback(self.__scheduledBurstConfirmation):
            self.delayCallback(BURST_CONFIRMATION_DELTA, self.__scheduledBurstConfirmation)
            self._sendBurstConfirmation()
            return BURST_VERIFYING_DELTA
        else:
            return BURST_VERIFYING_DELTA


class DevAutoShootController(AutoShootController):
    _MIN_RATE = 12
    _MAX_RATE = 12000
    _MIN_RATE_SPEED = 0
    _MAX_RATE_SPEED = 100
    _RATE_UPDATE_INTERVAL = 0.2
    _RATES_SEQUENCE = (_MIN_RATE,
     60,
     120,
     360,
     660,
     1200,
     1800,
     2400,
     3600,
     6000,
     9000,
     _MAX_RATE)
    _RATE_SPEEDS_SEQUENCE = (_MIN_RATE_SPEED,
     2,
     5,
     10,
     20,
     50,
     _MAX_RATE_SPEED)

    def __init__(self):
        super(DevAutoShootController, self).__init__()
        self.__burstStartTime = None
        self.__burstClampActive = False
        self.__desiredRate = self._MIN_RATE
        self.__desiredRateSpeed = self._MIN_RATE_SPEED
        self.__desiredRateInited = False
        self.__commandHandlers = {}
        return

    def startControl(self, *_):
        self.__commandHandlers = {AutoShootDevCommand.RATE_UP: self.__increaseRate,
         AutoShootDevCommand.RATE_DOWN: self.__decreaseRate,
         AutoShootDevCommand.RATE_SPEED_UP: self.__increaseRateSpeed,
         AutoShootDevCommand.RATE_SPEED_DOWN: self.__decreaseRateSpeed,
         AutoShootDevCommand.CLAMP_BURST: self.__toggleBurstClamping,
         AutoShootDevCommand.RESET: self.__resetParams}
        self.delayCallback(self._RATE_UPDATE_INTERVAL, self._tickRateCallback)

    def stopControl(self):
        self.__commandHandlers.clear()
        super(DevAutoShootController, self).stopControl()

    def processAutoShootDevCmd(self, command):
        ctrl = getPlayerVehicleAutoShootGunController()
        if command in self.__commandHandlers and ctrl is not None:
            self.__commandHandlers[command](ctrl)
        return

    def _isShootingCmdActive(self):
        burstStartTime = self.__burstStartTime or BigWorld.time()
        isClamping = self.__burstClampActive and burstStartTime + AUTO_SHOOT_DEV_BURST_CLAMP < BigWorld.time()
        return False if isClamping else super(DevAutoShootController, self)._isShootingCmdActive()

    def _sendBurstConfirmation(self):
        super(DevAutoShootController, self)._sendBurstConfirmation()
        self.__burstStartTime = self.__burstStartTime or BigWorld.time()

    def _sendBurstCancellation(self):
        self.__burstStartTime = None
        super(DevAutoShootController, self)._sendBurstCancellation()
        return

    def _tickRateCallback(self):
        self.__tickRate()
        return self._RATE_UPDATE_INTERVAL

    def __increaseRate(self, *_):
        self.__updateDesiredRate(findFirst(lambda rate: rate > self.__desiredRate, self._RATES_SEQUENCE, self._MIN_RATE))

    def __decreaseRate(self, *_):
        self.__updateDesiredRate(findFirst(lambda rate: rate < self.__desiredRate, reversed(self._RATES_SEQUENCE), self._MAX_RATE))

    def __increaseRateSpeed(self, *_):
        self.__updateRateSpeed(findFirst(lambda speed: speed > self.__desiredRateSpeed, self._RATE_SPEEDS_SEQUENCE, self._MIN_RATE_SPEED))

    def __decreaseRateSpeed(self, *_):
        self.__updateRateSpeed(findFirst(lambda speed: speed < self.__desiredRateSpeed, reversed(self._RATE_SPEEDS_SEQUENCE), self._MAX_RATE_SPEED))

    def __toggleBurstClamping(self, *_, **kwargs):
        value = kwargs.get('value')
        self.__burstClampActive = value if value is not None else not self.__burstClampActive
        LOG_WARNING('[AutoShoot][DEV] burst clamp mode: ', self.__burstClampActive)
        return

    def __resetParams(self, ctrl):
        self.__toggleBurstClamping(value=False)
        clipRate = ctrl.entity.typeDescriptor.gun.clip[1]
        desiredShootRate = int(60.0 / clipRate if clipRate > 0.0 else self.__desiredRate)
        self.__updateDesiredRate(desiredShootRate)
        self.__updateRateSpeed(self._MIN_RATE_SPEED)
        self.__updateServerRate(desiredShootRate)

    def __tickRate(self):
        ctrl = getPlayerVehicleAutoShootGunController()
        if ctrl is None:
            return
        else:
            currentRate = int(round(ctrl.getShotRatePerSecond() * 60.0))
            if isAlmostEqual(currentRate, self.__desiredRate, epsilon=0.5):
                self.__desiredRateInited = True
                return
            if not self.__desiredRateInited:
                self.__updateDesiredRate(currentRate)
                return
            if self.__desiredRateSpeed <= 0:
                self.__updateServerRate(self.__desiredRate)
                return
            if self.__desiredRate > currentRate:
                nextRate = clamp(self._MIN_RATE, self.__desiredRate, currentRate + self.__desiredRateSpeed)
            else:
                nextRate = clamp(self.__desiredRate, self._MAX_RATE, currentRate - self.__desiredRateSpeed)
            self.__updateServerRate(nextRate)
            return

    def __updateDesiredRate(self, desiredRate):
        self.__desiredRate = clamp(self._MIN_RATE, self._MAX_RATE, desiredRate)
        LOG_WARNING('[AutoShoot][DEV] desired shoot rate: ', self.__desiredRate)

    def __updateRateSpeed(self, desiredRateSpeed):
        self.__desiredRateSpeed = clamp(self._MIN_RATE_SPEED, self._MAX_RATE_SPEED, desiredRateSpeed)
        LOG_WARNING('[AutoShoot][DEV] desired shoot rate speed: ', self.__desiredRateSpeed)

    def __updateServerRate(self, requestedRate):
        serverCommand = 'autoShootGunController/set_auto_shoot_rate'
        BigWorld.player().base.setDevelopmentFeature(0, serverCommand, requestedRate, '')
        LOG_WARNING('[AutoShoot][DEV] requested shoot rate: ', requestedRate)


class AutoShootReplayController(AutoShootController):

    def processShootCmd(self):
        pass


class DevAutoShootReplayController(DevAutoShootController):

    def processAutoShootDevCmd(self, command):
        pass

    def processShootCmd(self):
        pass

    def _tickRateCallback(self):
        pass


class AutoShootControllerFactory(object):
    _AUTO_SHOOT_CONTROLLERS_MAP = {(False, False): AutoShootController,
     (False, True): AutoShootReplayController,
     (True, False): DevAutoShootController,
     (True, True): DevAutoShootReplayController}

    @classmethod
    def createAutoShootController(cls, setup):
        return cls._AUTO_SHOOT_CONTROLLERS_MAP[AUTO_SHOOT_DEV_KEYS, setup.isReplayPlaying]()
