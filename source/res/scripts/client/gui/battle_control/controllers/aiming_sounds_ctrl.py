# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/aiming_sounds_ctrl.py
import typing
from helpers import dependency
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.interfaces import IAimingSoundsCtrl
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from skeletons.gui.battle_session import IBattleSessionProvider
_AIMING_SOUND = 'sight_convergence'
_DUAL_ACC_SOUND = 'dual_aiming'
_EMPTY_SOUND = ''

class AimingSoundsCtrl(IAimingSoundsCtrl):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        self.__isAimingEnded = False
        self.__isDualAimingEnded = False

    def getControllerID(self):
        return BATTLE_CTRL_ID.AIMING_SOUNDS_CTRL

    def updateDispersion(self, multFactor, aimingFactor, idealFactor, dualAccMultFactor, dualAccFactor, idealDualAccFactor, hasDualAcc):
        isGunReloading = self.__sessionProvider.shared.ammo.isGunReloading()
        self.__updateDispersion(multFactor, aimingFactor, idealFactor, self.__setAimingEnded, _DUAL_ACC_SOUND if hasDualAcc else _AIMING_SOUND, self.__isAimingEnded or isGunReloading)
        self.__updateDispersion(dualAccMultFactor, dualAccFactor, idealDualAccFactor, self.__setDualAimingEnded, _AIMING_SOUND if hasDualAcc else _EMPTY_SOUND, self.__isDualAimingEnded or isGunReloading)

    def __setAimingEnded(self, value):
        self.__isAimingEnded = value

    def __setDualAimingEnded(self, value):
        self.__isDualAimingEnded = value

    def __playSoundNotification(self, notification):
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications is not None and notification:
            soundNotifications.play(notification)
        return

    def __updateDispersion(self, multFactor, aimingFactor, idealFactor, aimingSetter, notification, skipNotification):
        if aimingFactor < idealFactor:
            if abs(idealFactor - multFactor) < 0.001:
                if not skipNotification:
                    self.__playSoundNotification(notification)
                aimingSetter(True)
            elif idealFactor / multFactor > 1.1:
                aimingSetter(False)
        elif aimingFactor / multFactor > 1.1:
            aimingSetter(False)
