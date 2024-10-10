# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/auto_shoot_guns/auto_burst_controller.py
import BigWorld
import CommandMapping
from AutoShootGunController import getPlayerVehicleAutoShootGunController
from auto_shoot_guns.auto_shoot_guns_common import BURST_VERIFYING_DELTA, BURST_CONFIRMATION_DELTA
from gui.battle_control.arena_info.interfaces import IAutoShootGunController
from helpers.CallbackDelayer import CallbackDelayer

class BurstController(IAutoShootGunController.IBurstController, CallbackDelayer):
    __slots__ = ('__burstPredictor',)

    def __init__(self, burstPredictor):
        super(BurstController, self).__init__()
        self.__burstPredictor = burstPredictor

    def isBurstActive(self):
        ctrl = getPlayerVehicleAutoShootGunController()
        isBurstActive = self.hasDelayedCallback(self.__scheduledBurstVerification)
        isBurstActive = isBurstActive or self.__burstPredictor.isShootingProcess()
        return isBurstActive or ctrl is not None and ctrl.isShooting()

    def processShootCmd(self):
        if not self.hasDelayedCallback(self.__scheduledBurstVerification):
            self.delayCallback(BURST_VERIFYING_DELTA, self.__scheduledBurstVerification)
            self.__verifyBurst()

    def __cancelBurst(self):
        self.stopCallback(self.__scheduledBurstConfirmation)
        self.__sendBurstCancellation()
        BigWorld.player().dropStopUntilFireMode()

    def __verifyBurst(self, isRepeat=False):
        player = BigWorld.player()
        burstPredictor = self.__burstPredictor
        if player is None or not player.isOnArena or not player.isVehicleAlive:
            self.stopCallback(self.__scheduledBurstConfirmation)
            burstPredictor.killShooting()
            return
        elif not player.verifyShooting(isRepeat):
            self.stopCallback(self.__scheduledBurstConfirmation)
            burstPredictor.setShootingPossible(False)
            return BURST_VERIFYING_DELTA
        burstPredictor.setShootingPossible(True)
        if burstPredictor.canConfirmShooting() and not self.hasDelayedCallback(self.__scheduledBurstConfirmation):
            self.delayCallback(BURST_CONFIRMATION_DELTA, self.__scheduledBurstConfirmation)
            self.__sendBurstConfirmation()
            return BURST_VERIFYING_DELTA
        else:
            return BURST_VERIFYING_DELTA

    def __scheduledBurstConfirmation(self):
        self.__sendBurstConfirmation()
        return BURST_CONFIRMATION_DELTA

    def __scheduledBurstVerification(self):
        isBurst = CommandMapping.g_instance.isActive(CommandMapping.CMD_CM_SHOOT)
        return self.__verifyBurst(isRepeat=True) if isBurst else self.__cancelBurst()

    def __sendBurstCancellation(self):
        ctrl = getPlayerVehicleAutoShootGunController()
        if ctrl is not None:
            self.__burstPredictor.deactivateShooting()
            ctrl.cell.deactivateShooting()
        return

    def __sendBurstConfirmation(self):
        ctrl = getPlayerVehicleAutoShootGunController()
        if ctrl is not None:
            self.__burstPredictor.activateShooting()
            ctrl.cell.activateShooting()
        return


class BurstReplayController(BurstController):

    def processShootCmd(self):
        pass


def createBurstController(setup, burstPredictor):
    controllerCls = BurstReplayController if setup.isReplayPlaying else BurstController
    return controllerCls(burstPredictor)
