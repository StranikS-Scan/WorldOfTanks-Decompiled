# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/shared_utils/avatar_helpers/DualGun.py
from math import ceil
import BigWorld
from OwnVehicleBase import Cooldowns
from ReloadEffect import ReloadType
from constants import DUAL_GUN
from gui.battle_control.battle_constants import CANT_SHOOT_ERROR

def createDualGunHelper(vehicle):
    if vehicle.typeDescriptor.isDualgunVehicle:
        if vehicle.typeDescriptor.isAutoReloadGun or vehicle.typeDescriptor.isClipGun:
            return DualGunClipAutoReloadHelper(vehicle.typeDescriptor.gun.dualGun.autoloadWithClip)
        return DualGunHelper()
    return DualGunHelper()


class IDualGunHelper(object):

    def updateGunReloadTime(self, avatar, vehicleID, activeGun, gunStates, cooldownTimes, ammoCtrl=None):
        raise NotImplementedError

    def updateClipReloadTime(self, avatar, vehicleID, timeLeft, baseTime, firstTime, stunned, isBoostApplicable, ammoCtrl=None):
        raise NotImplementedError


class DualGunHelper(IDualGunHelper):

    def __init__(self):
        self.__debuffTrigger = False

    def updateGunReloadTime(self, avatar, vehicleID, activeGun, gunStates, cooldownTimes, ammoCtrl=None):

        def __callReloadTimeWrapper(leftTime, baseTime):
            avatar.updateVehicleGunReloadTime(vehicleID, -1, baseTime)
            avatar.updateVehicleGunReloadTime(vehicleID, leftTime, baseTime)
            if leftTime > 0:
                ammoCtrl.triggerReloadEffect(leftTime, baseTime)

        if activeGun == DUAL_GUN.ACTIVE_GUN.LEFT:
            secondGun = DUAL_GUN.ACTIVE_GUN.RIGHT
        else:
            secondGun = DUAL_GUN.ACTIVE_GUN.LEFT
        if ammoCtrl is not None:
            ammoCtrl.setDualGunShellChangeTime(cooldownTimes[activeGun].baseTime, cooldownTimes[activeGun].baseTime, activeGun)
            ammoCtrl.setDualGunState(*gunStates)
            reloadingGun = None
            if gunStates[activeGun] == DUAL_GUN.GUN_STATE.RELOADING:
                reloadingGun = activeGun
            if gunStates[secondGun] == DUAL_GUN.GUN_STATE.RELOADING:
                reloadingGun = secondGun
            if reloadingGun is not None:
                ammoCtrl.triggerReloadEffect(cooldownTimes[reloadingGun].leftTime, cooldownTimes[reloadingGun].baseTime, ReloadType.DUALGUN)
        if gunStates[activeGun] == DUAL_GUN.GUN_STATE.RELOADING:
            if not self.__debuffTrigger:
                __callReloadTimeWrapper(cooldownTimes[activeGun].leftTime, cooldownTimes[activeGun].baseTime)
            if self.__debuffTrigger:
                if ammoCtrl is not None:
                    ammoCtrl.debuffFinish()
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
            if debuff.leftTime > 0 and error is not None and error != CANT_SHOOT_ERROR.NO_AMMO:
                self.__debuffTrigger = True
                totalDebuffTime = cooldownTimes[activeGun].baseTime + debuff.leftTime
                if ammoCtrl is not None:
                    ammoCtrl.debuffStart(debuff.leftTime)
                __callReloadTimeWrapper(totalDebuffTime, cooldownTimes[activeGun].baseTime + debuff.baseTime)
            else:
                avatar.updateVehicleGunReloadTime(vehicleID, -1, cooldownTimes[activeGun].baseTime)
        return

    def updateClipReloadTime(self, avatar, vehicleID, timeLeft, baseTime, firstTime, stunned, isBoostApplicable, ammoCtrl=None):
        pass


class DualGunClipAutoReloadHelper(IDualGunHelper):

    def __init__(self, autoloadWithClip):
        super(DualGunClipAutoReloadHelper, self).__init__()
        self.__debuffTrigger = False
        self.__reloadingFirstShellOrFullClip = True
        self.__activeGun = None
        self.__gunStates = None
        self.__cooldownTimes = None
        self.__stateFixTime = None
        self.__firstShellInClipTime = None
        self.__autoloadWithClip = autoloadWithClip
        return

    @staticmethod
    def __callReloadTimeWrapper(avatar, vehicleID, leftTime, baseTime):
        avatar.updateVehicleGunReloadTime(vehicleID, -1, baseTime)
        avatar.updateVehicleGunReloadTime(vehicleID, leftTime, baseTime)
        if leftTime > 0:
            ammoCtrl = avatar.guiSessionProvider.shared.ammo
            if ammoCtrl:
                ammoCtrl.triggerReloadEffect(leftTime, baseTime)

    def updateGunReloadTime(self, avatar, vehicleID, activeGun, gunStates, cooldownTimes, ammoCtrl=None):
        if activeGun == DUAL_GUN.ACTIVE_GUN.LEFT:
            secondGun = DUAL_GUN.ACTIVE_GUN.RIGHT
        else:
            secondGun = DUAL_GUN.ACTIVE_GUN.LEFT
        self.__activeGun = activeGun
        self.__gunStates = gunStates
        self.__cooldownTimes = cooldownTimes
        self.__stateFixTime = BigWorld.timeExact()
        activeGunReloadBaseTime = cooldownTimes[activeGun].baseTime
        debuffBaseTime = cooldownTimes[DUAL_GUN.COOLDOWNS.DEBUFF].baseTime
        debuffLeftTime = cooldownTimes[DUAL_GUN.COOLDOWNS.DEBUFF].leftTime
        canShotState = None
        shellChangeTime = 0
        shellsInClip = 0
        firstAvailableShell = None
        if ammoCtrl is not None:
            ammoCtrl.setDualGunShellChangeTime(cooldownTimes[activeGun].baseTime, cooldownTimes[activeGun].baseTime, activeGun)
            ammoCtrl.setDualGunState(*gunStates)
            shellChangeTime = ammoCtrl.getShellChangeTime()
            reloadingGun = None
            if gunStates[activeGun] == DUAL_GUN.GUN_STATE.RELOADING:
                reloadingGun = activeGun
            if gunStates[secondGun] == DUAL_GUN.GUN_STATE.RELOADING:
                reloadingGun = secondGun
            if reloadingGun is not None:
                ammoCtrl.triggerReloadEffect(cooldownTimes[reloadingGun].leftTime, cooldownTimes[reloadingGun].baseTime, ReloadType.DUALGUN)
            _, canShotState = ammoCtrl.canShoot()
            _, shellsInClip = ammoCtrl.getCurrentShells()
            burstSize = ammoCtrl.getGunSettings().burst.size
            if burstSize > 1:
                shellsInClip = int(ceil(float(shellsInClip) / burstSize))
            firstAvailableShell = ammoCtrl.getFirstAvailableShell()
            if shellsInClip <= 0:
                self.__reloadingFirstShellOrFullClip = True
            elif gunStates[activeGun] == DUAL_GUN.GUN_STATE.READY:
                self.__reloadingFirstShellOrFullClip = False
        if debuffLeftTime <= 0:
            if self.__debuffTrigger:
                if ammoCtrl is not None:
                    ammoCtrl.debuffFinish()
                self.__debuffTrigger = False
                if gunStates[activeGun] in (DUAL_GUN.GUN_STATE.EMPTY, DUAL_GUN.GUN_STATE.RELOADING):
                    return
        switchCD = cooldownTimes[DUAL_GUN.COOLDOWNS.SWITCH]
        if gunStates[activeGun] == DUAL_GUN.GUN_STATE.RELOADING:
            if debuffLeftTime <= 0:
                activeGunLeftTime = cooldownTimes[activeGun].leftTime
                if switchCD.leftTime > activeGunLeftTime:
                    baseTime, leftTime = switchCD.baseTime, switchCD.leftTime
                else:
                    baseTime, leftTime = activeGunReloadBaseTime, activeGunLeftTime
                    if self.__reloadingFirstShellOrFullClip:
                        baseTime += shellChangeTime
                self.__callReloadTimeWrapper(avatar, vehicleID, leftTime, baseTime)
        elif gunStates[activeGun] == DUAL_GUN.GUN_STATE.READY:
            if switchCD.leftTime > 0:
                self.__callReloadTimeWrapper(avatar, vehicleID, switchCD.leftTime, switchCD.baseTime)
            elif gunStates[secondGun] == DUAL_GUN.GUN_STATE.READY:
                self.__callReloadTimeWrapper(avatar, vehicleID, 0, switchCD.baseTime)
            else:
                totalBaseTime = cooldownTimes[activeGun].baseTime
                if shellsInClip <= 1:
                    if self.__autoloadWithClip:
                        totalBaseTime = 0
                    totalBaseTime += shellChangeTime
                self.__callReloadTimeWrapper(avatar, vehicleID, 0, totalBaseTime)
        else:
            if self.__reloadingFirstShellOrFullClip and self.__autoloadWithClip:
                activeGunReloadBaseTime = 0
            if canShotState == CANT_SHOOT_ERROR.WAITING:
                avatar.updateVehicleGunReloadTime(vehicleID, -1, activeGunReloadBaseTime + shellChangeTime)
                return
            totalBaseTime = totalLeftTime = activeGunReloadBaseTime
            if canShotState is None or canShotState == CANT_SHOOT_ERROR.NO_AMMO and firstAvailableShell is None:
                avatar.updateVehicleGunReloadTime(vehicleID, -1, 0)
                return
            if debuffLeftTime > 0:
                self.__debuffTrigger = True
                if ammoCtrl is not None:
                    ammoCtrl.debuffStart(debuffLeftTime)
            if self.__debuffTrigger:
                totalBaseTime += debuffBaseTime
                totalLeftTime += debuffLeftTime
            if self.__reloadingFirstShellOrFullClip:
                totalBaseTime += shellChangeTime
                leftTimeAdd = shellChangeTime
                if ammoCtrl is not None and not self.__debuffTrigger:
                    leftTimeAdd = ammoCtrl.getAutoReloadingState().getTimeLeft()
                totalLeftTime += leftTimeAdd
            self.__callReloadTimeWrapper(avatar, vehicleID, totalLeftTime, totalBaseTime)
        return

    def updateClipReloadTime(self, avatar, vehicleID, timeLeft, baseTime, firstTime, stunned, isBoostApplicable, ammoCtrl=None):
        if self.__stateFixTime is None:
            return
        else:
            if self.__firstShellInClipTime != firstTime:
                self.__firstShellInClipTime = firstTime
                self.updateGunReloadTime(avatar, vehicleID, self.__activeGun, self.__gunStates, self.__correctCooldownTimes(self.__cooldownTimes, self.__stateFixTime), ammoCtrl)
            elif self.__reloadingFirstShellOrFullClip:
                self.updateGunReloadTime(avatar, vehicleID, self.__activeGun, self.__gunStates, self.__correctCooldownTimes(self.__cooldownTimes, self.__stateFixTime), ammoCtrl)
            _, shellsInClip = ammoCtrl.getCurrentShells()
            if shellsInClip == 0 or timeLeft <= 0:
                ammoCtrl.triggerReloadEffect(timeLeft, baseTime, ReloadType.CLIP)
            return

    @staticmethod
    def __correctCooldownTimes(cooldownTimes, fixStateTime):
        correctedCooldownTimes = []
        if fixStateTime is None:
            return cooldownTimes
        else:
            passedTime = max(0.0, BigWorld.timeExact() - fixStateTime)
            for cooldownTime in cooldownTimes:
                leftTime = max(0.0, cooldownTime.leftTime - passedTime)
                correctedCooldownTimes.append(Cooldowns(cooldownTime.id, leftTime, cooldownTime.baseTime))

            return correctedCooldownTimes
