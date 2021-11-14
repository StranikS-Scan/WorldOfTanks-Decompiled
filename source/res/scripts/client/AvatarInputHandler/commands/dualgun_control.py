# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/commands/dualgun_control.py
import logging
import BigWorld
import CommandMapping
from AvatarInputHandler.commands.input_handler_command import InputHandlerCommand
from constants import DUAL_GUN, DUALGUN_CHARGER_ACTION_TYPE, DUALGUN_CHARGER_STATUS
from gui.battle_control import event_dispatcher as gui_event_dispatcher
from helpers.CallbackDelayer import CallbackDelayer
_logger = logging.getLogger(__name__)

class ShotStates(object):
    PREPARING = 0
    DISABLED = 1


class ShotController(CallbackDelayer):
    __SINGLE_SHOT_THRESHOLD_DEFAULT = 0.5
    __PRE_CHARGE_INDICATION_DEFAULT = 0.25
    __CHARGE_CANCEL_TIME_DEFAULT = 0.18
    isLocked = property(lambda self: self.__shotUnavailable)

    def __init__(self, threshold=__SINGLE_SHOT_THRESHOLD_DEFAULT, preChargeIndication=__PRE_CHARGE_INDICATION_DEFAULT, chargeCancelTime=__CHARGE_CANCEL_TIME_DEFAULT):
        super(ShotController, self).__init__()
        self.__state = ShotStates.DISABLED
        self.__singleShotThreshold = threshold
        self.__preChargeIndicationDelay = preChargeIndication
        self.__chargeCancelTime = chargeCancelTime
        self.__shotUnavailable = False

    def updateState(self, state, value):
        if state == DUALGUN_CHARGER_STATUS.CANCELED:
            cancelTime = value[0] if value else 0.0
            if cancelTime > 0.0:
                self.__shotUnavailable = True
                self.stopCallback(self.__setShootAvailable)
                self.delayCallback(cancelTime, self.__setShootAvailable)
            else:
                self.__setShootAvailable()
        elif state == DUALGUN_CHARGER_STATUS.APPLIED:
            self.clearCallbacks()
            self.__setShootAvailable()

    def shootKeyEvent(self, actionType):
        if actionType == DUALGUN_CHARGER_ACTION_TYPE.CANCEL:
            wasInCharging = self.__state == ShotStates.DISABLED
        else:
            wasInCharging = False
        BigWorld.player().shootDualGun(actionType, wasInCharging)
        if actionType == DUALGUN_CHARGER_ACTION_TYPE.START_IMMEDIATELY:
            gui_event_dispatcher.chargeReleased(keyDown=True)
        elif actionType == DUALGUN_CHARGER_ACTION_TYPE.START_WITH_DELAY:
            if self.__state == ShotStates.DISABLED:
                self.delayCallback(self.__singleShotThreshold, self.__disable)
                self.__state = ShotStates.PREPARING
            preChargeStartTime = self.__singleShotThreshold - self.__preChargeIndicationDelay
            if preChargeStartTime > 0:
                self.delayCallback(preChargeStartTime, gui_event_dispatcher.dualGunPreCharge)
            else:
                _logger.error('Incorrect pre-charge delay configuration %d', self.__preChargeIndicationDelay)
        elif actionType == DUALGUN_CHARGER_ACTION_TYPE.CANCEL:
            if self.__state == ShotStates.PREPARING:
                self.__applyShoot()
                self.__disable(direct=True)
                if self.__shotUnavailable:
                    self.__setShootAvailable()
            else:
                self.__shotUnavailable = True
                self.delayCallback(self.__chargeCancelTime, self.__setShootAvailable)
            gui_event_dispatcher.chargeReleased(keyDown=False)

    def __applyShoot(self):
        if not self.__shotUnavailable:
            BigWorld.player().shoot()
        self.stopCallback(gui_event_dispatcher.dualGunPreCharge)

    def __setShootAvailable(self):
        self.__shotUnavailable = False

    def __disable(self, direct=False):
        self.stopCallback(self.__disable)
        self.__state = ShotStates.DISABLED
        if not direct:
            gui_event_dispatcher.chargeReleased(keyDown=True)


class DualGunController(InputHandlerCommand):
    isShotLocked = property(lambda self: self.__shotControl.isLocked)

    def __init__(self, typeDescr):
        self.__activeGun = DUAL_GUN.ACTIVE_GUN.LEFT
        dualGunParams = typeDescr.gun.dualGun
        if dualGunParams is not None:
            self.__shotControl = ShotController(dualGunParams.chargeThreshold, dualGunParams.preChargeIndication, dualGunParams.chargeCancelTime)
        else:
            self.__shotControl = ShotController()
        return

    def updateChargeState(self, state, value):
        self.__shotControl.updateState(state, value)

    def handleKeyEvent(self, isDown, key, mods, event=None):
        vehicle = BigWorld.player().getVehicleAttached()
        if vehicle is None or not vehicle.isPlayerVehicle or not vehicle.isAlive():
            return False
        elif vehicle.typeDescriptor is None or not vehicle.typeDescriptor.hasCharge:
            return False
        cmdMap = CommandMapping.g_instance
        if cmdMap.isFiredList((CommandMapping.CMD_CM_CHARGE_SHOT, CommandMapping.CMD_CM_SHOOT), key, True):
            status = DUALGUN_CHARGER_ACTION_TYPE.START_WITH_DELAY if isDown else DUALGUN_CHARGER_ACTION_TYPE.CANCEL
            self.__shotControl.shootKeyEvent(status)
            return True
        elif cmdMap.isFired(CommandMapping.CMD_CM_CHARGE_SHOT, key):
            status = DUALGUN_CHARGER_ACTION_TYPE.START_IMMEDIATELY if isDown else DUALGUN_CHARGER_ACTION_TYPE.CANCEL
            self.__shotControl.shootKeyEvent(status)
            return True
        else:
            return False

    def cancelShootKeyEvent(self):
        self.__shotControl.shootKeyEvent(DUALGUN_CHARGER_ACTION_TYPE.CANCEL)
