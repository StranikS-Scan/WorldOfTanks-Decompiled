# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/shared_utils/avatar_helpers/DualGun.py
from constants import DUAL_GUN

class DualGunHelper(object):

    def __init__(self):
        self.__debuffTrigger = False

    def updateGunReloadTime(self, avatar, vehicleID, activeGun, gunStates, cooldownTimes, ammoCtrl=None):

        def __callReloadTimeWrapper(leftTime, baseTime):
            avatar.updateVehicleGunReloadTime(vehicleID, -1, baseTime)
            avatar.updateVehicleGunReloadTime(vehicleID, leftTime, baseTime)

        if activeGun == DUAL_GUN.ACTIVE_GUN.LEFT:
            secondGun = DUAL_GUN.ACTIVE_GUN.RIGHT
        else:
            secondGun = DUAL_GUN.ACTIVE_GUN.LEFT
        if ammoCtrl is not None:
            reloadingGun = None
            if gunStates[activeGun] == DUAL_GUN.GUN_STATE.RELOADING:
                reloadingGun = activeGun
            if gunStates[secondGun] == DUAL_GUN.GUN_STATE.RELOADING:
                reloadingGun = secondGun
            if reloadingGun is not None:
                ammoCtrl.triggerReloadEffect(cooldownTimes[reloadingGun].leftTime, cooldownTimes[reloadingGun].baseTime, directTrigger=True)
        if gunStates[activeGun] == DUAL_GUN.GUN_STATE.RELOADING:
            if not self.__debuffTrigger:
                __callReloadTimeWrapper(cooldownTimes[activeGun].leftTime, cooldownTimes[activeGun].baseTime)
            if self.__debuffTrigger:
                self.__debuffTrigger = False
        elif gunStates[activeGun] == DUAL_GUN.GUN_STATE.READY:
            switchCD = cooldownTimes[DUAL_GUN.COOLDOWNS.SWITCH]
            if switchCD.leftTime > 0:
                __callReloadTimeWrapper(switchCD.leftTime, switchCD.baseTime)
            elif gunStates[secondGun] == DUAL_GUN.GUN_STATE.READY:
                __callReloadTimeWrapper(0, switchCD.baseTime)
            else:
                __callReloadTimeWrapper(0, cooldownTimes[activeGun].baseTime)
        else:
            debuff = cooldownTimes[DUAL_GUN.COOLDOWNS.DEBUFF]
            error = None
            if ammoCtrl is not None:
                _, error = ammoCtrl.canShoot()
            if debuff.leftTime > 0 and error is not None and error != 'no_ammo':
                self.__debuffTrigger = True
                totalDebuffTime = cooldownTimes[activeGun].baseTime + debuff.leftTime
                ammoCtrl.onDebuffStarted(debuff.leftTime)
                __callReloadTimeWrapper(totalDebuffTime, cooldownTimes[activeGun].baseTime + debuff.baseTime)
            else:
                avatar.updateVehicleGunReloadTime(vehicleID, -1, cooldownTimes[activeGun].baseTime)
        if ammoCtrl is not None:
            ammoCtrl.setDualGunShellChangeTime(cooldownTimes[activeGun].baseTime, cooldownTimes[activeGun].baseTime, activeGun)
        return

    def reset(self):
        self.__debuffTrigger = False
