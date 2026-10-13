# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/battle_control/controllers/equipment_items.py
from __future__ import absolute_import
import BigWorld
import math
from DynComponentsGroup import DynComponentsGroup
from HWBuffDrainLifeComponent import HWBuffDrainLifeComponent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.shared.system_factory import registerEquipmentItem
from gui.battle_control import avatar_getter, vehicle_getter
from gui.battle_control.controllers.consumables.equipment_ctrl import _ActivationError, DynComponentsGroupItem, DynComponentsGroupReplayItem
from gui.battle_control.battle_constants import DEVICE_STATE_DESTROYED
from constants import SERVER_TICK_LENGTH
from halloween_common.halloween_constants import HWVehicleModifiers

class HWEquipmentItem(DynComponentsGroupItem):

    def canActivate(self, entityName=None, avatar=None):
        result, error = super(HWEquipmentItem, self).canActivate(entityName, avatar)
        if not result:
            return (result, error)
        return (False, _ActivationError('hwNotEnoughSouls', {'name': self._descriptor.userString})) if self.vehicle.hwSoulsContainer.souls < self._getUsageCost() else (result, error)

    def getUsageCost(self):
        return self._getUsageCost()

    def getDurationSeconds(self):
        return self._getDurationSeconds()

    def getCooldownSeconds(self):
        return self._getCooldownSeconds()

    @property
    def vehicle(self):
        return avatar_getter.getPlayerVehicle()

    @property
    def variant(self):
        vehicle = self.vehicle
        return self._descriptor.getVariant(vehicle.typeDescriptor) if vehicle else self._descriptor.fallbackVariant

    def _getUsageCost(self):
        return math.ceil(self._applyModifiers(HWVehicleModifiers.EQUIPMENT_USAGE_COST, self.variant.usageCost))

    def _getDurationSeconds(self):
        return self._applyModifiers(HWVehicleModifiers.EQUIPMENT_DURATION, self.variant.durationSeconds)

    def _getCooldownSeconds(self):
        return self._applyModifiers(HWVehicleModifiers.EQUIPMENT_COOLDOWN, self.variant.cooldownSeconds)

    def _applyModifiers(self, key, value):
        vehicle = self.vehicle
        return vehicle.hwModifiers.calc(key, value, self._descriptor.name) if vehicle and hasattr(vehicle, 'hwModifiers') else value


class HWEquipmentReplayItemBase(DynComponentsGroupReplayItem):

    def getUsageCost(self):
        return self._getUsageCost()

    def getDurationSeconds(self):
        return self._getDurationSeconds()

    def getCooldownSeconds(self):
        return self._getCooldownSeconds()

    @property
    def vehicle(self):
        return avatar_getter.getPlayerVehicle()

    @property
    def variant(self):
        vehicle = self.vehicle
        return self._descriptor.getVariant(vehicle.typeDescriptor) if vehicle else self._descriptor.fallbackVariant

    def _getUsageCost(self):
        return math.ceil(self._applyModifiers(HWVehicleModifiers.EQUIPMENT_USAGE_COST, self.variant.usageCost))

    def _getDurationSeconds(self):
        return self._applyModifiers(HWVehicleModifiers.EQUIPMENT_DURATION, self.variant.durationSeconds)

    def _getCooldownSeconds(self):
        return self._applyModifiers(HWVehicleModifiers.EQUIPMENT_COOLDOWN, self.variant.cooldownSeconds)

    def _applyModifiers(self, key, value):
        vehicle = self.vehicle
        return vehicle.hwModifiers.calc(key, value, self._descriptor.name) if vehicle and hasattr(vehicle, 'hwModifiers') else value


class HWEquipmentReplayItem(HWEquipmentReplayItemBase):

    def canActivate(self, entityName=None, avatar=None):
        vehicle = BigWorld.entities.get(avatar_getter.getPlayerVehicleID())
        result, error = super(HWEquipmentReplayItem, self).canActivate(entityName, avatar)
        if not result:
            return (result, error)
        return (False, _ActivationError('hwNotEnoughSouls', {'name': self._descriptor.userString})) if vehicle.hwSoulsContainer.souls < self._descriptor.getVariant(vehicle.typeDescriptor).usageCost else (result, error)


class _HpRepairAndCrewHeal(HWEquipmentItem):

    def canActivate(self, entityName=None, avatar=None):
        vehicle = BigWorld.entities.get(avatar_getter.getPlayerVehicleID())
        deviceStates = avatar_getter.getVehicleDeviceStates(avatar)
        return (False, _ActivationError('hpRepairAndCrewHeal', {'name': self._descriptor.userString})) if vehicle.health >= vehicle.maxHealth and not deviceStates and not avatar_getter.isVehicleStunned() else super(_HpRepairAndCrewHeal, self).canActivate(entityName, avatar)


class _AbilityWithDuration(HWEquipmentItem):

    def canActivate(self, entityName=None, avatar=None):
        avatar = avatar or BigWorld.player()
        vehicle = BigWorld.entities.get(avatar.playerVehicleID)
        if not vehicle:
            return (False, _ActivationError('equipmentAlreadyActivated', {'name': self._descriptor.userString}))
        hasActiveBuff = any((isinstance(g, DynComponentsGroup) and name in self._descriptor.dynComponentsGroups for name, g in vehicle.dynamicComponents.items()))
        return (False, _ActivationError('equipmentAlreadyActivated', {'name': self._descriptor.userString})) if hasActiveBuff else super(_AbilityWithDuration, self).canActivate(entityName, avatar)


class _NitroEquipmentItem(_AbilityWithDuration):

    def inCriticalCondition(self, avatar=None):
        avatar = avatar or BigWorld.player()
        if avatar.fireInVehicle:
            return (True, _ActivationError('hwVehicleIsOnFire', {'name': self._descriptor.userString}))
        elif avatar.isVehicleOverturned:
            return (True, _ActivationError('hwVehicleIsOverturned', {'name': self._descriptor.userString}))
        else:
            return (True, _ActivationError('hwVehicleIsDrowning', {'name': self._descriptor.userString})) if avatar.isVehicleDrowning else (False, None)

    def canActivate(self, entityName=None, avatar=None):
        inCritical, error = self.inCriticalCondition(avatar)
        return (False, error) if inCritical else super(_NitroEquipmentItem, self).canActivate(entityName, avatar)


class _NitroEquipmentReplayItem(HWEquipmentReplayItemBase):

    def inCriticalCondition(self, avatar=None):
        avatar = avatar or BigWorld.player()
        if avatar.fireInVehicle:
            return (True, _ActivationError('hwVehicleIsOnFire', {'name': self._descriptor.userString}))
        elif avatar.isVehicleOverturned:
            return (True, _ActivationError('hwVehicleIsOverturned', {'name': self._descriptor.userString}))
        else:
            return (True, _ActivationError('hwVehicleIsDrowning', {'name': self._descriptor.userString})) if avatar.isVehicleDrowning else (False, None)


class _FastReload(_AbilityWithDuration):
    INSTANT_RELOAD = 'instantReload'
    DEVICES = ('gun',)
    ERROR_NAME = 'hw_ability_gun_destroyed'
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
                    return (False, None)
                if clipCapacity > quantityInClip:
                    return (True, None)
            return (False, _ActivationError('instantReload', {'name': self._descriptor.userString}))


class _HWInvisibility(HWEquipmentItem):

    def canActivate(self, entityName=None, avatar=None):
        vehicle = BigWorld.entities.get(avatar_getter.getPlayerVehicleID())
        hasActiveBuff = any((isinstance(component, HWBuffDrainLifeComponent) and component.isActive for component in vehicle.dynamicComponents.values()))
        return (False, _ActivationError('hwInvisibility', {'name': self._descriptor.userString})) if hasActiveBuff else super(_HWInvisibility, self).canActivate(entityName, avatar)


class _HWInstantShot(HWEquipmentItem):

    def activate(self, entityName=None, avatar=None):
        BigWorld.player().startWaitingForShot(SERVER_TICK_LENGTH * 2.0)
        super(_HWInstantShot, self).activate(entityName, avatar)


def registerHWEquipmentsItems():
    registerEquipmentItem('nitroRamDamage', _NitroEquipmentItem, _NitroEquipmentReplayItem)
    registerEquipmentItem('hpRepairAndCrewHeal', _HpRepairAndCrewHeal, HWEquipmentReplayItem)
    registerEquipmentItem('teamRepairKit', HWEquipmentItem, HWEquipmentReplayItem)
    registerEquipmentItem('fastReload', _FastReload, HWEquipmentReplayItem)
    registerEquipmentItem('damageShield', _AbilityWithDuration, HWEquipmentReplayItem)
    registerEquipmentItem('hwInvisibility', _HWInvisibility, HWEquipmentReplayItem)
    registerEquipmentItem('hwAoeDamageInstantShot', _HWInstantShot, HWEquipmentReplayItem)
    registerEquipmentItem('hwAoeStunInstantShot', _HWInstantShot, HWEquipmentReplayItem)
    registerEquipmentItem('hwAoeDrainEnemyHpInstantShot', _HWInstantShot, HWEquipmentReplayItem)
