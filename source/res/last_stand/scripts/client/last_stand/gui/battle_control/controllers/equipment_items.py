# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/battle_control/controllers/equipment_items.py
from __future__ import absolute_import, division
import BigWorld
import time
from math import ceil
from math_common import decimal_round
from future.utils import viewitems
from DynComponentsGroup import DynComponentsGroup
from helpers import dependency
from last_stand_common.last_stand_constants import BOOSTER_FACTOR_NAMES
from last_stand_common.ls_utils.boosters import getVehicleBoosterFactorsComponent
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control import avatar_getter, vehicle_getter
from gui.battle_control.controllers.consumables.equipment_ctrl import _ActivationError, DynComponentsGroupItem, DynComponentsGroupReplayItem
from gui.battle_control.battle_constants import DEVICE_STATE_DESTROYED
from constants import SERVER_TICK_LENGTH, EQUIPMENT_STAGES
from vehicles.mechanics.mechanic_constants import VehicleMechanic

class LSSituationalEquipmentItem(DynComponentsGroupItem):

    def canActivate(self, entityName=None, avatar=None):
        return (True, None)


class LSEquipmentItemBase(DynComponentsGroupItem):

    def inCriticalCondition(self, avatar=None):
        avatar = avatar or BigWorld.player()
        return (True, _ActivationError('LS_vehicleIsDrowning', {'name': self._descriptor.userString})) if avatar.isVehicleDrowning else (False, None)


class LSEquipmentItem(LSEquipmentItemBase):

    def canActivate(self, entityName=None, avatar=None):
        vehicle = BigWorld.entities.get(avatar_getter.getPlayerVehicleID())
        result, error = super(LSEquipmentItem, self).canActivate(entityName, avatar)
        if not result:
            return (result, error)
        inCritical, error = self.inCriticalCondition(avatar)
        if inCritical:
            return (False, error)
        return (False, _ActivationError('LS_notEnoughSouls', {'name': self._descriptor.userString})) if vehicle.lsSoulsContainer.souls < self._getUsageCost(vehicle) else (result, error)

    def _getUsageCost(self, vehicle):
        count = self._descriptor.getVariant(vehicle.typeDescriptor).usageCost
        factorsComponent = getVehicleBoosterFactorsComponent(vehicle)
        return max(0, int(factorsComponent.applyFactors(count, BOOSTER_FACTOR_NAMES.ABILITY_COST))) if factorsComponent else count

    def _getDurationSeconds(self):
        vehicle = avatar_getter.getPlayerVehicle()
        duration = int((self._descriptor.getVariant(vehicle.typeDescriptor) if vehicle else self._descriptor.fallbackVariant).durationSeconds)
        if duration > 0:
            factorsComponent = getVehicleBoosterFactorsComponent(vehicle)
            result = int(ceil(factorsComponent.applyFactors(duration, BOOSTER_FACTOR_NAMES.ABILITY_DURATION))) if factorsComponent else duration
            return max(1, result)
        return duration


class LSEquipmentReplayItem(LSEquipmentItemBase, DynComponentsGroupReplayItem):

    def __init__(self, descriptor, quantity, stage, timeRemaining, totalTime, tags=None):
        super(LSEquipmentReplayItem, self).__init__(descriptor, quantity, stage, timeRemaining, totalTime, tags)
        self._stage = stage

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(LSEquipmentReplayItem, self).update(quantity, stage, timeRemaining, totalTime)
        self._stage = stage

    def getCooldownPercents(self):
        totalTime = self.getTotalTime()
        timeRemaining = self.getReplayTimeRemaining()
        if totalTime > 0:
            percents = decimal_round(float(totalTime - timeRemaining) / totalTime * 100.0)
            if self._stage == EQUIPMENT_STAGES.ACTIVE:
                return 100 - percents
            return percents

    def canActivate(self, entityName=None, avatar=None):
        vehicle = BigWorld.entities.get(avatar_getter.getPlayerVehicleID())
        inCritical, error = self.inCriticalCondition(avatar)
        if inCritical:
            return (False, error)
        result, error = super(LSEquipmentReplayItem, self).canActivate(entityName, avatar)
        if not result:
            return (result, error)
        return (False, _ActivationError('LS_notEnoughSouls', {'name': self._descriptor.userString})) if vehicle.lsSoulsContainer.souls < self._getUsageCost(vehicle) else (result, error)

    def _getUsageCost(self, vehicle):
        count = self._descriptor.getVariant(vehicle.typeDescriptor).usageCost
        factorsComponent = getVehicleBoosterFactorsComponent(vehicle)
        return max(0, int(factorsComponent.applyFactors(count, BOOSTER_FACTOR_NAMES.ABILITY_COST))) if factorsComponent else count

    def _getDurationSeconds(self):
        vehicle = avatar_getter.getPlayerVehicle()
        durationSeconds = (self._descriptor.getVariant(vehicle.typeDescriptor) if vehicle else self._descriptor.fallbackVariant).durationSeconds
        if durationSeconds > 0:
            factorsComponent = getVehicleBoosterFactorsComponent(vehicle)
            applyFactor = ceil(factorsComponent.applyFactors(durationSeconds, BOOSTER_FACTOR_NAMES.ABILITY_DURATION)) if factorsComponent else durationSeconds
            return max(1, int(applyFactor))
        return durationSeconds


class _HpRepairAndCrewHeal(LSEquipmentItem):

    def canActivate(self, entityName=None, avatar=None):
        vehicle = BigWorld.entities.get(avatar_getter.getPlayerVehicleID())
        deviceStates = avatar_getter.getVehicleDeviceStates(avatar)
        return (False, _ActivationError('LS_selfRepair', {'name': self._descriptor.userString})) if vehicle.health >= vehicle.maxHealth and not deviceStates and not avatar_getter.isVehicleStunned() else super(_HpRepairAndCrewHeal, self).canActivate(entityName, avatar)


class _AbilityWithDuration(LSEquipmentItem):

    def canActivate(self, entityName=None, avatar=None):
        avatar = avatar or BigWorld.player()
        vehicle = BigWorld.entities.get(avatar.playerVehicleID)
        if not vehicle:
            return (False, _ActivationError('equipmentAlreadyActivated', {'name': self._descriptor.userString}))
        hasActiveBuff = any((isinstance(g, DynComponentsGroup) and name in self._descriptor.dynComponentsGroups for name, g in viewitems(vehicle.dynamicComponents)))
        return (False, _ActivationError('equipmentAlreadyActivated', {'name': self._descriptor.userString})) if hasActiveBuff else super(_AbilityWithDuration, self).canActivate(entityName, avatar)


class LSDamageShield(_AbilityWithDuration):
    _BLOCKED_COMPONENT = ('LS_obeliskShield',)

    def canActivate(self, entityName=None, avatar=None):
        avatar = avatar or BigWorld.player()
        vehicle = BigWorld.entities.get(avatar.playerVehicleID)
        return (False, _ActivationError('equipmentAlreadyActivated', {'name': self._descriptor.userString})) if any((component in vehicle.dynamicComponents for component in self._BLOCKED_COMPONENT)) else super(LSDamageShield, self).canActivate(entityName, avatar)


class _NitroEquipmentItemBase(LSEquipmentItemBase, DynComponentsGroupItem):

    def inCriticalCondition(self, avatar=None):
        avatar = avatar or BigWorld.player()
        inCritical, error = super(_NitroEquipmentItemBase, self).inCriticalCondition(avatar)
        if inCritical:
            return (inCritical, error)
        elif avatar.fireInVehicle:
            return (True, _ActivationError('LS_vehicleIsOnFire', {'name': self._descriptor.userString}))
        vehicle = BigWorld.entities[avatar.playerVehicleID]
        if 'lsFire' in vehicle.dynamicComponents:
            return (True, _ActivationError('LS_vehicleIsOnLSFire', {'name': self._descriptor.userString}))
        else:
            return (True, _ActivationError('LS_vehicleIsOverturned', {'name': self._descriptor.userString})) if avatar.isVehicleOverturned else (False, None)


class _NitroEquipmentItem(_NitroEquipmentItemBase, _AbilityWithDuration):

    def canActivate(self, entityName=None, avatar=None):
        inCritical, error = self.inCriticalCondition(avatar)
        return (False, error) if inCritical else super(_NitroEquipmentItem, self).canActivate(entityName, avatar)


class _NitroEquipmentReplayItem(_NitroEquipmentItemBase, LSEquipmentReplayItem):

    def canActivate(self, entityName=None, avatar=None):
        inCritical, error = self.inCriticalCondition(avatar)
        if inCritical:
            return (False, error)
        avatar = avatar or BigWorld.player()
        vehicle = BigWorld.entities.get(avatar.playerVehicleID)
        if not vehicle:
            return (False, _ActivationError('equipmentAlreadyActivated', {'name': self._descriptor.userString}))
        hasActiveBuff = any((isinstance(g, DynComponentsGroup) and name in self._descriptor.dynComponentsGroups for name, g in viewitems(vehicle.dynamicComponents)))
        return (False, _ActivationError('equipmentAlreadyActivated', {'name': self._descriptor.userString})) if hasActiveBuff else super(_NitroEquipmentReplayItem, self).canActivate(entityName, avatar)


class _FastReload(_AbilityWithDuration):
    INSTANT_RELOAD = 'LS_instantReload'
    DEVICES = ('gun',)
    ERROR_NAME = 'LS_gunDestroyed'
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def getEntitiesIterator(self, avatar=None):
        return vehicle_getter.VehicleDeviceStatesIterator(avatar_getter.getVehicleDeviceStates(avatar), avatar_getter.getVehicleTypeDescriptor(avatar))

    def canActivate(self, entityName=None, avatar=None):
        vehicle = BigWorld.entities.get(avatar_getter.getPlayerVehicleID())
        return self._canActivateInstant(entityName, avatar) if self._descriptor.getVariant(vehicle.typeDescriptor).equipmentItem == self.INSTANT_RELOAD else self._canActivateFast(entityName, avatar)

    def _canActivateFast(self, entityName=None, avatar=None):
        isGunDestroyed = any((name in self.DEVICES and state == DEVICE_STATE_DESTROYED for name, state in self.getEntitiesIterator()))
        return (False, _ActivationError(self.ERROR_NAME, {'name': self._descriptor.userString})) if isGunDestroyed else super(_FastReload, self).canActivate(entityName, avatar)

    def _canActivateInstant(self, entityName=None, avatar=None):
        avatar = avatar or BigWorld.player()
        result, error = super(_FastReload, self).canActivate(entityName, avatar)
        if not result:
            return (result, error)
        else:
            ammoCtrl = self.guiSessionProvider.shared.ammo
            quantity, quantityInClip = ammoCtrl.getCurrentShells()
            if not quantity:
                return (False, None)
            isGunReloading = ammoCtrl.isGunReloading()
            if isGunReloading:
                return (True, None)
            if ammoCtrl.getGunSettings().isDualGun:
                reloadingState = ammoCtrl.getGunReloadingState()
                dualGunShellChangeTime = ammoCtrl.getDualGunShellChangeTime()
                if reloadingState.getBaseValue() >= min(dualGunShellChangeTime.left, dualGunShellChangeTime.right):
                    return (True, None)
            if ammoCtrl.getGunSettings().isCassetteClip:
                clipCapacity = ammoCtrl.getGunSettings().clip.size
                if quantityInClip >= quantity:
                    return (False, _ActivationError('LS_instantReload', {'name': self._descriptor.userString}))
                if clipCapacity > quantityInClip:
                    return (True, None)
            if ammoCtrl.getGunSettings().isUnlimitedClip and 'autoShoot' in ammoCtrl.getGunSettings().tags:
                ammoStatesInfo = ammoCtrl.ammoStatesInfo
                overHeatState = ammoStatesInfo.ammoStates.get(VehicleMechanic.OVERHEAT_GUN.value)
                if overHeatState:
                    canShoot, _ = overHeatState.canShootValidation()
                    if not canShoot:
                        return (True, None)
            return (False, _ActivationError('LS_instantReload', {'name': self._descriptor.userString}))


class _LSInstantShot(LSEquipmentItem):
    _COOLDOWN = SERVER_TICK_LENGTH * 0.5

    def __init__(self, *args, **kwargs):
        super(_LSInstantShot, self).__init__(*args, **kwargs)
        self._lastTimeActive = None
        return

    def activate(self, entityName=None, avatar=None):
        if self.isInCooldown(time.time()):
            return
        BigWorld.player().startWaitingForShot(SERVER_TICK_LENGTH * 2.0)
        super(_LSInstantShot, self).activate(entityName, avatar)

    def isInCooldown(self, now):
        isCooldown = self._lastTimeActive is not None and now - self._lastTimeActive < self._COOLDOWN
        self._lastTimeActive = now
        return isCooldown
