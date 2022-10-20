# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/battle_control/controllers/hw_equipment_ctrl.py
import BigWorld
from gui.shared.system_factory import registerEquipmentItem
from gui.battle_control import avatar_getter
from constants import EQUIPMENT_STAGES
from gui.battle_control import vehicle_getter
from gui.battle_control.controllers.consumables.equipment_ctrl import _TriggerItem, _ReplayItem, _ActivationError, NeedEntitySelection, NotApplyingError, IgnoreEntitySelection, EquipmentSound
from items import vehicles
from buffs_helpers import makeBuffName

class EventEquipmentSound(EquipmentSound):

    @staticmethod
    def playActive(item):
        equipment = vehicles.g_cache.equipments()[item.getEquipmentID()]
        if equipment is not None:
            if equipment.soundNotificationActive is not None:
                avatar_getter.getSoundNotifications().play(equipment.soundNotificationActive)
        return


class _EventItem(_TriggerItem):

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_EventItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage in (EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.READY):
            self._totalTime = self._descriptor.cooldownSeconds
        elif stage == EQUIPMENT_STAGES.ACTIVE:
            self._totalTime = timeRemaining

    def getEntitiesIterator(self, avatar=None):
        return []

    def getGuiIterator(self, avatar=None):
        return []

    def _soundUpdate(self, prevQuantity, quantity):
        super(_EventItem, self)._soundUpdate(prevQuantity, quantity)
        if self._stage == EQUIPMENT_STAGES.ACTIVE and self._serverPrevStage == EQUIPMENT_STAGES.READY:
            EventEquipmentSound.playActive(self)


class _EventBuffItem(_EventItem):
    pass


class _EventPassiveBuffItem(_EventItem):

    def canActivate(self, entityName=None, avatar=None):
        return (False, None)


class _SuperShellItem(_EventItem):

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_SuperShellItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.READY:
            self._timeRemaining = 0
            self._totalTime = totalTime
        if stage == EQUIPMENT_STAGES.ACTIVE:
            self._timeRemaining = -2
            self._totalTime = totalTime


class _HpRepairAndCrewHeal(_EventItem):

    def canActivate(self, entityName=None, avatar=None):
        avatar = avatar or BigWorld.player()
        result, error = super(_HpRepairAndCrewHeal, self).canActivate(entityName, avatar)
        if not result:
            return (result, error)
        elif avatar_getter.isVehicleInFire(avatar):
            return (True, None)
        else:
            vehicle = BigWorld.entities.get(avatar.playerVehicleID)
            if not vehicle:
                return (False, _ActivationError('hpRepairAndCrewHeal', {'name': self._descriptor.userString}))
            elif vehicle.maxHealth > vehicle.health:
                return (True, None)
            result, error = self._checkCrew(avatar)
            return (result, error) if result else (False, _ActivationError('hpRepairAndCrewHeal', {'name': self._descriptor.userString}))

    def _checkCrew(self, avatar):
        result = False
        error = None
        deviceStates = avatar_getter.getVehicleDeviceStates(avatar)
        for item in self._getCrewIterator():
            if item[0] in deviceStates:
                isEntityNotRequired = not self.isEntityRequired()
                result = isEntityNotRequired
                error = None if isEntityNotRequired else NeedEntitySelection('', None)
                break

        return (True, IgnoreEntitySelection('', None)) if not result and not isinstance(error, (NeedEntitySelection, NotApplyingError)) and avatar_getter.isVehicleStunned() and self.isReusable else (False, None)

    @staticmethod
    def _getCrewIterator(avatar=None):
        return vehicle_getter.TankmenStatesIterator(avatar_getter.getVehicleDeviceStates(avatar), avatar_getter.getVehicleTypeDescriptor(avatar))

    @staticmethod
    def _getDevicesIterator(avatar=None):
        return vehicle_getter.VehicleDeviceStatesIterator(avatar_getter.getVehicleDeviceStates(avatar), avatar_getter.getVehicleTypeDescriptor(avatar))


class _DamageShield(_EventBuffItem):

    def canActivate(self, entityName=None, avatar=None):
        avatar = avatar or BigWorld.player()
        vehicle = BigWorld.entities.get(avatar.playerVehicleID)
        if not vehicle:
            return (False, _ActivationError('equipmentAlreadyActivated', {'name': self._descriptor.userString}))
        hasAnyBuff = any((vehicle.hwBuffContainer.isBuffActive(makeBuffName(name, vehicle.typeDescriptor)) for name in self.getDescriptor().buffNames))
        return (False, _ActivationError('equipmentAlreadyActivated', {'name': self._descriptor.userString})) if hasAnyBuff else super(_DamageShield, self).canActivate(entityName, avatar)


class _EventReplayItem(_EventItem):
    __slots__ = ('__cooldownTime',)

    def __init__(self, descriptor, quantity, stage, timeRemaining, totalTime, tags=None):
        super(_EventReplayItem, self).__init__(descriptor, quantity, stage, timeRemaining, totalTime, tags)
        self.__cooldownTime = BigWorld.serverTime() + timeRemaining

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_EventReplayItem, self).update(quantity, stage, timeRemaining, totalTime)
        self.__cooldownTime = BigWorld.serverTime() + timeRemaining

    def getReplayTimeRemaining(self):
        return max(0, self.__cooldownTime - BigWorld.serverTime())

    def getCooldownPercents(self):
        totalTime = self.getTotalTime()
        timeRemaining = self.getReplayTimeRemaining()
        return round(float(totalTime - timeRemaining) / totalTime * 100.0) if totalTime > 0 else 0.0


class _ReplayHpRepairAndCrewHeal(_HpRepairAndCrewHeal, _EventReplayItem):
    __slots__ = ()


def registerHWEquipmentCtrls():
    registerEquipmentItem('damageShield', _DamageShield, _EventReplayItem)
    registerEquipmentItem('hpRepairAndCrewHeal', _HpRepairAndCrewHeal, _ReplayHpRepairAndCrewHeal)
    registerEquipmentItem('halloweenNitro', _EventBuffItem, _EventReplayItem)
    registerEquipmentItem('multiplyGunReloadTime', _EventPassiveBuffItem, _ReplayItem)
    registerEquipmentItem('superShellFireball', _SuperShellItem, _EventReplayItem)
    registerEquipmentItem('damageVehicleModules', _SuperShellItem, _EventReplayItem)
    registerEquipmentItem('halloweenRamBoost', _EventPassiveBuffItem, _ReplayItem)
    registerEquipmentItem('enlargeMaxHealth', _EventPassiveBuffItem, _ReplayItem)
    registerEquipmentItem('halloweenBullseye', _EventPassiveBuffItem, _ReplayItem)
