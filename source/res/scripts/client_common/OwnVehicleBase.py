# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/OwnVehicleBase.py
from collections import namedtuple
from functools import partial
import BigWorld
import math
from constants import VEHICLE_SETTING, DAMAGE_INFO_CODES, DAMAGE_INFO_INDICES
from items import vehicles, ITEM_TYPES
from wotdecorators import noexcept
Cooldowns = namedtuple('Cooldows', ['id', 'leftTime', 'baseTime'])
_DO_LOG = False

def noneAccepted(func):
    func.__isNoneAccepted = True
    return func


class OwnVehicleBase(BigWorld.DynamicScriptComponent):

    def __init__(self):
        super(OwnVehicleBase, self).__init__()
        self._doLog('OwnVehicleBase __init__ {}'.format(self.entity.id))
        self.__isInitialUpdated = False
        self.__isAttachingToVehicle = False
        self.initialUpdate()

    def onDestroy(self):
        self._doLog('onDestroy {}'.format(self.entity.id))
        self.__onDestroy()

    def onLeaveWorld(self):
        self._doLog('onLeaveWorld {}'.format(self.entity.id))
        self.__onDestroy()

    def __onDestroy(self):
        if getattr(self, 'targetVehicleID', None):
            self.update_targetVehicleID(None)
        self.__dict__.clear()
        return

    @noexcept
    def update_vehicleAmmoList(self, ammoList):
        avatar = self._avatar()
        if not avatar:
            return
        else:
            for vehicleAmmo in ammoList:
                timeRemaining = vehicleAmmo.endTime
                if timeRemaining > 0:
                    timeRemaining = max(timeRemaining - self._serverTime(), 0)
                avatar.updateVehicleAmmo(self.entity.id, vehicleAmmo.compactDescr, vehicleAmmo.quantity, vehicleAmmo.quantityInClip, None if self.__isAttachingToVehicle else vehicleAmmo.previousStage, math.floor(timeRemaining), vehicleAmmo.totalTime, vehicleAmmo.index)

            return

    @noexcept
    def update_syncVehicleAttrs(self, syncVehicleAttrs):
        avatar = self._avatar()
        if not avatar:
            return
        avatar.syncVehicleAttrs(self.entity.id, syncVehicleAttrs)

    @noexcept
    def update_vehicleGunReloadTime(self, prop):
        avatar = self._avatar()
        if not avatar:
            return
        timeLeft, timeBase = self.__getTimeLeftBaseTime(prop)
        avatar.updateVehicleGunReloadTime(self.entity.id, timeLeft, timeBase)

    @noexcept
    def update_vehicleClipReloadTime(self, prop):
        avatar = self._avatar()
        if not avatar:
            return
        timeLeft, timeBase = self.__getTimeLeftBaseTime(prop)
        avatar.updateVehicleClipReloadTime(self.entity.id, timeLeft, timeBase, prop.firstTime, prop.stunned, prop.isBoostApplicable)

    @noexcept
    def update_vehicleSettings(self, prop):
        avatar = self._avatar()
        if not avatar:
            return
        avatar.updateVehicleSettings(prop)

    @noexcept
    def update_destroyedDevicesIsRepairing(self, deviceList):
        avatar = self._avatar()
        if not avatar:
            return
        for device in deviceList:
            timeLeft = self.__getTimeLeft(device)
            avatar.updateDestroyedDevicesIsRepairing(self.entity.id, device.extraIndex, device.progress, timeLeft, device.repairMode)

    @noexcept
    def update_vehicleDamageInfoList(self, damageInfoList):
        if not damageInfoList:
            return
        avatar = self._avatar()
        if not avatar:
            return
        for damage in damageInfoList:
            damageIndex = damage.damageIndex
            if self.__isAttachingToVehicle:
                if DAMAGE_INFO_CODES[damageIndex].startswith('DEVICE_CRITICAL'):
                    damageIndex = DAMAGE_INFO_INDICES['DEVICE_CRITICAL']
                if DAMAGE_INFO_CODES[damageIndex] == 'DEVICE_REPAIRED_TO_CRITICAL':
                    damageIndex = DAMAGE_INFO_INDICES['DEVICE_CRITICAL']
                if DAMAGE_INFO_CODES[damageIndex].startswith('ENGINE_CRITICAL'):
                    damageIndex = DAMAGE_INFO_INDICES['DEVICE_CRITICAL']
                if DAMAGE_INFO_CODES[damageIndex].startswith('DEVICE_DESTROYED'):
                    damageIndex = DAMAGE_INFO_INDICES['DEVICE_DESTROYED']
            avatar.showVehicleDamageInfo(self.entity.id, damageIndex, damage.extraIndex, damage.entityID, damage.equipmentID, self.__isAttachingToVehicle)

    @noexcept
    def update_vehicleOptionalDeviceStatusList(self, deviceList):
        avatar = self._avatar()
        if not avatar:
            return
        for optDevStatus in deviceList:
            avatar.updateVehicleOptionalDeviceStatus(self.entity.id, optDevStatus.deviceID, optDevStatus.isOn)

    @noexcept
    def update_dualGunState(self, dualGunState):
        if dualGunState is None:
            return
        else:
            avatar = self._avatar()
            if not avatar:
                return
            cooldowns = []
            useEndTime = self.__isAttachingToVehicle
            for cd in dualGunState.cooldowns:
                if cd.endTime > 0 and useEndTime:
                    cooldowns.append(Cooldowns(cd.id, max(0.0, cd.endTime - self._serverTime()), cd.baseTime))
                cooldowns.append(Cooldowns(cd.id, cd.leftTime, cd.baseTime))

            avatar.updateDualGunState(self.entity.id, dualGunState.activeGun, dualGunState.gunStates, cooldowns)
            return

    @noexcept
    def update_dualGunStatus(self, dualGunStatus):
        avatar = self._avatar()
        if not avatar:
            return
        if not dualGunStatus or not avatar.userSeesWorld():
            return
        times = dualGunStatus.times
        timeLeft = self.__getTimeLeft(times)
        avatar.updateDualGunStatus(self.entity.id, dualGunStatus.status, (times.baseTime, timeLeft))

    @noexcept
    def update_siegeStateStatus(self, siegeStateStatus):
        avatar = self._avatar()
        if not avatar:
            return
        timeLeft = self.__getTimeLeft(siegeStateStatus)
        avatar.updateSiegeStateStatus(self.entity.id, siegeStateStatus.status, timeLeft)

    @noexcept
    def update_burnoutWarning(self, burnoutWarning):
        avatar = self._avatar()
        if not avatar:
            return
        avatar.updateBurnoutWarning(self.entity.id, burnoutWarning.status)

    @noexcept
    def update_burnoutUnavailable(self, burnoutUnavailable):
        avatar = self._avatar()
        if not avatar:
            return
        avatar.updateBurnoutUnavailable(self.entity.id, burnoutUnavailable.status)

    @noexcept
    def update_drownLevel(self, drownLevel):
        avatar = self._avatar()
        if not avatar:
            return
        avatar.updateDrownLevel(self.entity.id, drownLevel.level, self.__getDestroyTimes(drownLevel.times))

    @noexcept
    def update_isOtherVehicleDamagedDevicesVisible(self, isOtherVehicleDamagedDevicesVisible):
        avatar = self._avatar()
        if not avatar:
            return
        avatar.updateIsOtherVehicleDamagedDevicesVisible(self.entity.id, isOtherVehicleDamagedDevicesVisible.status)

    @noexcept
    def update_overturnLevel(self, overturnLevel):
        avatar = self._avatar()
        if not avatar:
            return
        avatar.updateOverturnLevel(self.entity.id, overturnLevel.level, self.__getDestroyTimes(overturnLevel.times))

    @noneAccepted
    @noexcept
    def update_smokeInfo(self, smokeInfo):
        avatar = self._avatar()
        if not avatar:
            return
        avatar.onSmoke(smokeInfo)

    @noneAccepted
    @noexcept
    def update_targetVehicleID(self, targetVehicleID):
        avatar = self._avatar()
        if not avatar:
            return
        else:
            avatar.updateTargetVehicleID(targetVehicleID.targetID if targetVehicleID else None)
            return

    @noexcept
    def update_targetingInfo(self, data):
        avatar = self._avatar()
        if not avatar:
            return
        avatar.updateTargetingInfo(self.entity.id, data.turretYaw, data.gunPitch, data.maxTurretRotationSpeed, data.maxGunRotationSpeed, data.shotDispMultiplierFactor, data.gunShotDispersionFactorsTurretRotation, data.chassisShotDispersionFactorsMovement, data.chassisShotDispersionFactorsRotation, data.gunShotDispersionFactorsAfterShot, data.aimingTime)

    @noexcept
    def update_vehicleHealthInfo(self, data):
        avatar = self._avatar()
        if not avatar:
            return
        avatar.updateVehicleHealth(self.entity.id, data.health, data.deathReasonID, data.isCrewActive, data.isRespawnActive)

    @noexcept
    def update_welcomeToSector(self, data):
        avatar = self._avatar()
        if not avatar:
            return
        avatar.welcomeToSector(data.sectorID, data.groupID, data.groupState, data.goodGroup, data.actionTime, data.actionDuration)

    @noexcept
    def update_battleEventsSummary(self, data):
        avatar = self._avatar()
        return None if not avatar else None

    @noexcept
    def update_remoteCamera(self, data):
        avatar = self._avatar()
        if not avatar:
            return
        avatar.setRemoteCamera(data)

    def onBattleEvents(self, battleEvents):
        avatar = self._avatar()
        if not avatar:
            return
        if _DO_LOG:
            self._doLog('onBattleEvents {}'.format(battleEvents))
        avatar.onBattleEvents(battleEvents)

    def onObservedByEnemy(self):
        avatar = self._avatar()
        if not avatar:
            return
        if _DO_LOG:
            self._doLog('onObservedByEnemy')
        avatar.onObservedByEnemy(self.entity.id)

    def onSectorShooting(self, sectorID):
        avatar = self._avatar()
        if not avatar:
            return
        if _DO_LOG:
            self._doLog('onSectorShooting {}'.format(sectorID))
        avatar.onSectorShooting(sectorID)

    def beforeSetupUpdate(self):
        avatar = self._avatar()
        if not avatar:
            return
        avatar.beforeSetupUpdate(self.entity.id)

    def showOwnVehicleHitDirection(self, data):
        avatar = self._avatar()
        if not avatar:
            return
        if _DO_LOG:
            self._doLog('showOwnVehicleHitDirection {}'.format(data))
        avatar.showOwnVehicleHitDirection(data.hitDirYaw, data.attackerID, data.damage, data.crits, data.isBlocked, data.isShellHE, data.damagedID, data.attackReasonID)

    def redrawVehicleOnRespawn(self, vehicleID, newVehCompactDescr, newVehOutfitCompactDescr):
        avatar = self._avatar()
        if not avatar:
            return
        avatar.redrawVehicleOnRespawn(vehicleID, newVehCompactDescr, newVehOutfitCompactDescr)

    def beforeRespawn(self, vehicleID, health):
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle:
            vehicle.onHealthChanged(health, health, 0, 0)

    def getReloadTime(self):
        return self.__getTimeLeftBaseTime(self.vehicleGunReloadTime, True) if self.vehicleGunReloadTime else (0, 0)

    def getSiegeStateTimeLeft(self):
        return self.__getTimeLeft(self.siegeStateStatus, useEndTime=True) if self.siegeStateStatus else 0

    def setNested_vehicleAmmoList(self, path, prev):
        avatar = self._avatar()
        if not avatar:
            return
        changedAmmo = self.vehicleAmmoList[path[0]]
        if changedAmmo.compactDescr != prev.compactDescr:
            timeRemaining = changedAmmo.endTime
            if timeRemaining > 0:
                timeRemaining = max(timeRemaining - self._serverTime(), 0)
            avatar.resetVehicleAmmo(oldCompactDescr=prev.compactDescr, newCompactDescr=changedAmmo.compactDescr, quantity=changedAmmo.quantity, stage=changedAmmo.previousStage, timeRemaining=math.floor(timeRemaining), totalTime=changedAmmo.totalTime, index=changedAmmo.index)
        else:
            self.__setNested(self.update_vehicleAmmoList, 'vehicleAmmoList', path, prev)

    def __getDestroyTimes(self, times):
        startTime = self._serverTime() if self.__isAttachingToVehicle else times[0]
        return (startTime, max(times[1] - startTime, 0.0))

    def __getTimeLeft(self, data, useEndTime=None):
        if useEndTime is None:
            useEndTime = self.__isAttachingToVehicle
        if data.timeLeft <= 0:
            timeLeft = data.timeLeft
        elif useEndTime and data.endTime > 0:
            timeLeft = max(0, data.endTime - self._serverTime())
        else:
            timeLeft = data.timeLeft
        return timeLeft

    def __getTimeLeftBaseTime(self, data, useEndTime=None):
        return (self.__getTimeLeft(data, useEndTime), data.baseTime)

    @property
    def shells(self):
        return self.__getItemsByType(ITEM_TYPES.shell)

    @property
    def equipment(self):
        return self.__getItemsByType(ITEM_TYPES.equipment)

    @property
    def currentShell(self):
        return self.__getVehicleSetting(VEHICLE_SETTING.CURRENT_SHELLS)

    @property
    def nextShell(self):
        return self.__getVehicleSetting(VEHICLE_SETTING.NEXT_SHELLS)

    def __getItemsByType(self, ammoType):
        return [ ammo for ammo in self.vehicleAmmoList if vehicles.parseIntCompactDescr(ammo.compactDescr)[0] == ammoType ]

    def __getVehicleSetting(self, code):
        for item in self.vehicleSettings:
            if item.code == code:
                return item.value

    def initialUpdate(self, force=False):
        if not force:
            if self.__isInitialUpdated or not self.entity.isStarted:
                return
        self.__isInitialUpdated = True
        self.__isAttachingToVehicle = True
        try:
            self.__attachToVehicle()
        finally:
            self.__isAttachingToVehicle = False

    def __attachToVehicle(self):
        self.set_vehicleAmmoList()
        self.set_vehicleGunReloadTime()
        self.set_vehicleClipReloadTime()
        self.set_syncVehicleAttrs()
        self.set_vehicleSettings()
        self.set_destroyedDevicesIsRepairing()
        self.set_vehicleDamageInfoList()
        self.set_vehicleOptionalDeviceStatusList()
        self.set_dualGunState()
        self.set_dualGunStatus()
        self.set_burnoutWarning()
        self.set_burnoutUnavailable()
        self.set_isOtherVehicleDamagedDevicesVisible()
        self.set_overturnLevel()
        self.set_drownLevel()
        self.set_smokeInfo()
        self.set_targetVehicleID()
        self.set_targetingInfo()
        self.set_vehicleHealthInfo()
        self.set_welcomeToSector()
        self.set_siegeStateStatus()

    def __getattr__(self, item):
        if _DO_LOG:
            self._doLog('__getAttr {}'.format(item))
        parts = item.split('_')
        if len(parts) == 2 and (parts[0] == 'set' or parts[0] == 'setNested' or parts[0] == 'setSlice'):
            if hasattr(self, parts[1]):
                fname = 'update_' + parts[1]
                func = getattr(self, fname, None)
                if func:
                    attrFunc = None
                    if parts[0] == 'set':
                        attrFunc = partial(self.__set, func, parts[1])
                    if parts[0] == 'setNested':
                        attrFunc = partial(self.__setNested, func, parts[1])
                    if parts[0] == 'setSlice':
                        attrFunc = partial(self.__setSlice, func, parts[1])
                    self.__dict__[item] = attrFunc
                    return attrFunc
        raise AttributeError('OwnVehicle does not have attrubure {}'.format(item))
        return

    def __set(self, func, propname, oldValue=None):
        if _DO_LOG:
            self._doLog('__set {} {} {}'.format(propname, getattr(self, propname), oldValue))
        prop = getattr(self, propname)
        if prop is not None or getattr(func, '__isNoneAccepted', False):
            func(prop)
        return

    def __setNested(self, func, propname, changePath, oldValue=None):
        if _DO_LOG:
            self._doLog('__setNested {} {} {} {}'.format(propname, getattr(self, propname), changePath, oldValue))
        func(getattr(self, propname)[changePath[0]:changePath[0] + 1])

    def __setSlice(self, func, propname, changePath, oldValue=None):
        if _DO_LOG:
            self._doLog('__setSlice {} {} {} {}'.format(propname, changePath, getattr(self, propname), oldValue))
        if oldValue:
            return
        prop = getattr(self, propname)
        if not prop:
            return
        fromIndex, toIndex = changePath[-1]
        func(prop[fromIndex:toIndex])

    def _doLog(self, msg):
        pass

    def _serverTime(self):
        raise NotImplementedError('_serverTime must be overrided in ownVehicle')

    def _avatar(self):
        raise NotImplementedError('_avatar must be overrided in ownVehicle')
