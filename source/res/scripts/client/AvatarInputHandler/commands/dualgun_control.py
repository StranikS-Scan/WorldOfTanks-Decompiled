# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/commands/dualgun_control.py
import logging
import BigWorld
import CommandMapping
from AvatarInputHandler.commands.input_handler_command import InputHandlerCommand
from constants import DUAL_GUN
from gui.battle_control import event_dispatcher as gui_event_dispatcher
from helpers.CallbackDelayer import CallbackDelayer
_logger = logging.getLogger(__name__)

class ShotStates(object):
    PREPARING = 0
    DISABLED = 1


class ShotController(CallbackDelayer):
    __slots__ = ('__state', '__singleShotThreshold')
    __SINGLE_SHOT_THRESHOLD_DEFAULT = 0.5
    __PRE_CHARGE_INDICATION_DEFAULT = 0.25

    def __init__(self, threshold=__SINGLE_SHOT_THRESHOLD_DEFAULT, preChargeIndication=__PRE_CHARGE_INDICATION_DEFAULT):
        super(ShotController, self).__init__()
        self.__state = ShotStates.DISABLED
        self.__singleShotThreshold = threshold
        self.__preChargeIndicationDelay = preChargeIndication

    def shootKeyEvent(self, isDown):
        wasInCharging = self.__state == ShotStates.DISABLED if not isDown else False
        BigWorld.player().shootDualGun(isDown, wasInCharging)
        preChargeStartTime = self.__singleShotThreshold - self.__preChargeIndicationDelay
        if preChargeStartTime > 0:
            if isDown:
                self.delayCallback(preChargeStartTime, gui_event_dispatcher.dualGunPreCharge)
        else:
            _logger.error('Incorrect pre-charge delay configuration %d', self.__preChargeIndicationDelay)
        if not isDown:
            gui_event_dispatcher.chargeReleased(keyDown=False)
        if isDown and self.__state == ShotStates.DISABLED:
            self.delayCallback(self.__singleShotThreshold, self.__disable)
            self.__state = ShotStates.PREPARING
        if not isDown and self.__state == ShotStates.PREPARING:
            self.__applyShoot()
            self.__disable(direct=True)

    def __applyShoot(self):
        BigWorld.player().shoot()
        self.stopCallback(gui_event_dispatcher.dualGunPreCharge)

    def __disable(self, direct=False):
        self.stopCallback(self.__disable)
        self.__state = ShotStates.DISABLED
        if not direct:
            gui_event_dispatcher.chargeReleased(keyDown=True)


class DualGunController(InputHandlerCommand):
    __slots__ = ('__activeGun', '__shotControl', '__afterShootDelay')

    def __init__(self, typeDescr):
        self.__activeGun = DUAL_GUN.ACTIVE_GUN.LEFT
        dualGunParams = typeDescr.gun.dualGun
        singleShotTreshold = None
        preChargeDelay = None
        if dualGunParams is not None:
            singleShotTreshold = typeDescr.gun.dualGun.chargeThreshold
            preChargeDelay = typeDescr.gun.dualGun.preChargeIndication
        self.__shotControl = ShotController(singleShotTreshold, preChargeDelay)
        return

    def activeGun(self):
        return self.__activeGun

    def handleKeyEvent(self, isDown, key, mods, event=None):
        vehicle = BigWorld.player().getVehicleAttached()
        if vehicle is None or not vehicle.isPlayerVehicle or not vehicle.isAlive():
            return False
        elif vehicle.typeDescriptor is None or not vehicle.typeDescriptor.hasCharge:
            return False
        cmdMap = CommandMapping.g_instance
        if cmdMap.isFired(CommandMapping.CMD_CM_SHOOT, key):
            self.__shotControl.shootKeyEvent(isDown)
            return True
        else:
            return False
