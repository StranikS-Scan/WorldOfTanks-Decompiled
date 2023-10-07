# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/vehicle_blocks.py
import weakref
import random
import BigWorld
import GenericComponents
from visual_script.block import Block, InitParam, buildStrKeysValue
from visual_script.slot_types import SLOT_TYPE
from visual_script.misc import ASPECT, EDITOR_TYPE, errorVScript
from visual_script.tunable_event_block import TunableEventBlock
from visual_script.vehicle_blocks import VehicleMeta
from visual_script.vehicle_blocks_bases import NoCrewCriticalBase, OptionalDevicesBase, VehicleClassBase, GunTypeInfoBase, VehicleForwardSpeedBase, VehicleCooldownEquipmentBase, VehicleClipFullAndReadyBase, GetTankOptDevicesHPModBase, IsInHangarBase, VehicleRadioDistanceBase, NoInnerDeviceDamagedBase
from constants import IS_VS_EDITOR
if not IS_VS_EDITOR:
    from helpers import dependency, isPlayerAccount
    from skeletons.gui.shared import IItemsCache

class GetVehicleLabel(Block, VehicleMeta):

    def __init__(self, *args, **kwargs):
        super(GetVehicleLabel, self).__init__(*args, **kwargs)
        self._vehicle = self._makeDataInputSlot('vehicle', SLOT_TYPE.VEHICLE)
        self._label = self._makeDataOutputSlot('label', SLOT_TYPE.STR, self._getLabel)

    def _getLabel(self):
        vehicle = self._vehicle.getValue()
        label = vehicle.label if hasattr(vehicle, 'label') else None
        if label is None:
            label = ''
        self._label.setValue(label)
        return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class OnAnyVehicleDestroyed(TunableEventBlock, VehicleMeta):
    _EVENT_SLOT_NAMES = ['onDestroyed']

    def __init__(self, *args, **kwargs):
        super(OnAnyVehicleDestroyed, self).__init__(*args, **kwargs)
        self._target = self._makeDataOutputSlot('target', SLOT_TYPE.VEHICLE, None)
        self._attacker = self._makeDataOutputSlot('attacker', SLOT_TYPE.VEHICLE, None)
        return

    @classmethod
    def blockIcon(cls):
        pass

    def onStartScript(self):
        if hasattr(BigWorld.player(), 'arena'):
            BigWorld.player().arena.onVehicleKilled += self.__onVehicleKilled
        else:
            errorVScript(self, 'can not subscribe on event')

    def onFinishScript(self):
        if hasattr(BigWorld.player(), 'arena'):
            BigWorld.player().arena.onVehicleKilled -= self.__onVehicleKilled

    @TunableEventBlock.eventProcessor
    def __onVehicleKilled(self, targetID, attackerID, equipmentID, reason, numVehiclesAffected):
        target = BigWorld.entities.get(targetID)
        if target:
            self._target.setValue(weakref.proxy(BigWorld.entities.get(targetID)))
        else:
            self._target.setValue(None)
        if attackerID > 0:
            attacker = BigWorld.entities.get(attackerID)
            if attacker:
                attacker = weakref.proxy(BigWorld.entities.get(attackerID))
                self._attacker.setValue(attacker)
            else:
                self._attacker.setValue(None)
        else:
            self._attacker.setValue(None)
        return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class OnAnyVehicleDamaged(TunableEventBlock, VehicleMeta):
    _EVENT_SLOT_NAMES = ['onDamaged']

    def __init__(self, *args, **kwargs):
        super(OnAnyVehicleDamaged, self).__init__(*args, **kwargs)
        self._target = self._makeDataOutputSlot('target', SLOT_TYPE.VEHICLE, None)
        self._attacker = self._makeDataOutputSlot('attacker', SLOT_TYPE.VEHICLE, None)
        self._damage = self._makeDataOutputSlot('damage', SLOT_TYPE.INT, None)
        return

    @classmethod
    def blockIcon(cls):
        pass

    def onStartScript(self):
        if hasattr(BigWorld.player(), 'arena'):
            BigWorld.player().arena.onVehicleHealthChanged += self.__onDamageReceived
        else:
            errorVScript(self, 'can not subscribe on event')

    def onFinishScript(self):
        if hasattr(BigWorld.player(), 'arena'):
            BigWorld.player().arena.onVehicleHealthChanged -= self.__onDamageReceived

    @TunableEventBlock.eventProcessor
    def __onDamageReceived(self, vehicleId, attackerId, damage):
        self._damage.setValue(damage)
        vehicle = BigWorld.entities.get(vehicleId)
        if vehicle:
            self._target.setValue(weakref.proxy(vehicle))
        else:
            self._damage.setValue(None)
            self._target.setValue(None)
        if attackerId > 0:
            attacker = BigWorld.entities.get(attackerId)
            if attacker:
                attacker = weakref.proxy(BigWorld.entities.get(attackerId))
                self._attacker.setValue(attacker)
            else:
                self._attacker.setValue(None)
        else:
            self._attacker.setValue(None)
        return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class IsVehicleBurning(Block, VehicleMeta):

    def __init__(self, *args, **kwargs):
        super(IsVehicleBurning, self).__init__(*args, **kwargs)
        self._vehicle = self._makeDataInputSlot('vehicle', SLOT_TYPE.VEHICLE)
        self._res = self._makeDataOutputSlot('res', SLOT_TYPE.BOOL, self._exec)

    def _exec(self):
        v = self._vehicle.getValue()
        self._res.setValue(v.isOnFire())

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class NoCrewCritical(NoCrewCriticalBase):

    def _execute(self):
        self._outSlot.setValue(True)

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class NoInnerDeviceDamaged(NoInnerDeviceDamagedBase):

    def _execute(self):
        self._outSlot.setValue(True)

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class OptionalDevices(OptionalDevicesBase):

    def _execute(self):
        self._outSlot.setValue([])

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class GetTankOptDevicesHPMod(GetTankOptDevicesHPModBase):

    def _execute(self):
        self._outSlot.setValue(1.0)

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class VehicleClass(VehicleClassBase):

    def _execute(self):
        if isPlayerAccount():
            from CurrentVehicle import g_currentVehicle
            itemsCache = dependency.instance(IItemsCache)
            vehicle = self._vehicle.getValue()
            vehId = vehicle.vehicleID
            if g_currentVehicle.item and g_currentVehicle.item.descriptor.type.compactDescr == vehId:
                vehicle = g_currentVehicle.item
            else:
                vehicle = itemsCache.items.getItemByCD(vehId)
            self._outSlot.setValue(next(iter(vehicle.type)))
        else:
            self._outSlot.setValue('')

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class GunTypeInfo(GunTypeInfoBase):

    def _execute(self):
        self._outSlot.setValue([])

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class VehicleForwardSpeed(VehicleForwardSpeedBase):

    def _execute(self):
        self._outSlot.setValue(0.0)

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class VehicleCooldownEquipment(VehicleCooldownEquipmentBase):

    def _execute(self):
        if isPlayerAccount():
            from CurrentVehicle import g_currentVehicle
            itemsCache = dependency.instance(IItemsCache)
            vehicle = self._vehicle.getValue()
            vehIntId = vehicle.vehicleID
            if g_currentVehicle.item and g_currentVehicle.item.descriptor.type.compactDescr == vehIntId:
                vehicle = g_currentVehicle.item
            else:
                vehicle = itemsCache.items.getItemByCD(vehIntId)
            eqs = vehicle.getCooldownEquipment()
            self._outSlot.setValue(eqs)
        else:
            self._outSlot.setValue([])

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class VehicleClipFullAndReady(VehicleClipFullAndReadyBase):

    def _execute(self):
        self._outSlot.setValue(True)

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class GetNearestAliveVehicle(Block, VehicleMeta):
    _settingTypes = ['Ally', 'Enemy', 'Any']

    @classmethod
    def initParams(cls):
        return [InitParam('Vehicle Team', SLOT_TYPE.STR, buildStrKeysValue(*cls._settingTypes), EDITOR_TYPE.STR_KEY_SELECTOR)]

    def __init__(self, *args, **kwargs):
        super(GetNearestAliveVehicle, self).__init__(*args, **kwargs)
        self._settingType = self._getInitParams()
        self._position = self._makeDataInputSlot('position', SLOT_TYPE.VECTOR3)
        self._vehicle = self._makeDataOutputSlot('vehicle', SLOT_TYPE.VEHICLE, self._execute)

    def __checkVehicle(self, vehicle):
        player = BigWorld.player()
        if not hasattr(vehicle, 'isStarted') or not vehicle.isStarted or not vehicle.isAlive():
            return False
        if player.vehicle and vehicle.id == player.vehicle.id:
            return False
        if self._settingType == 'Ally':
            return vehicle.publicInfo.team == player.team
        return vehicle.publicInfo.team != player.team if self._settingType == 'Enemy' else True

    def _execute(self):
        player = BigWorld.player()
        vehicles = (v for v in player.vehicles if self.__checkVehicle(v))
        vehicle = None
        minDist = 99999
        for v in vehicles:
            dist = player.vehicle.position.distTo(v.position)
            if dist < minDist:
                vehicle = v
                minDist = dist

        self._vehicle.setValue(weakref.proxy(vehicle) if vehicle else None)
        return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class GetAnyVehicle(Block, VehicleMeta):
    _settingTypes = ['Ally', 'Enemy', 'Any']

    @classmethod
    def initParams(cls):
        return [InitParam('Vehicle Team', SLOT_TYPE.STR, buildStrKeysValue(*cls._settingTypes), EDITOR_TYPE.STR_KEY_SELECTOR)]

    def __init__(self, *args, **kwargs):
        super(GetAnyVehicle, self).__init__(*args, **kwargs)
        self._settingType = self._getInitParams()
        self._vehicle = self._makeDataOutputSlot('vehicle', SLOT_TYPE.VEHICLE, self._execute)

    def __checkVehicle(self, vehicle):
        player = BigWorld.player()
        if not hasattr(vehicle, 'isStarted') or not vehicle.isStarted or not vehicle.isAlive():
            return False
        if player.vehicle and vehicle.id == player.vehicle.id:
            return False
        if self._settingType == 'Ally':
            return vehicle.publicInfo.team == player.team
        return vehicle.publicInfo.team != player.team if self._settingType == 'Enemy' else True

    def _execute(self):
        player = BigWorld.player()
        vehicles = [ v for v in player.vehicles if self.__checkVehicle(v) ]
        vehicle = random.choice(vehicles) if vehicles else None
        self._vehicle.setValue(weakref.proxy(vehicle) if vehicle else None)
        return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class GameObjectToVehicle(Block, VehicleMeta):

    def __init__(self, *args, **kwargs):
        super(GameObjectToVehicle, self).__init__(*args, **kwargs)
        self._go = self._makeDataInputSlot('gameObject', SLOT_TYPE.GAME_OBJECT)
        self._vehicle = self._makeDataOutputSlot('vehicle', SLOT_TYPE.VEHICLE, self._exec)

    def _exec(self):
        go = self._go.getValue()
        if go is None:
            errorVScript(self, 'Please check input game object.')
            return
        else:
            goSyncComponent = go.findComponentByType(GenericComponents.EntityGOSync)
            if goSyncComponent is None:
                errorVScript(self, "Can't find associated entity. Please check input game object")
                return
            self._vehicle.setValue(weakref.proxy(goSyncComponent.entity))
            return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class IsInHangar(IsInHangarBase):

    def _execute(self):
        self._outSlot.setValue(isPlayerAccount())

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class VehicleRadioDistance(VehicleRadioDistanceBase):

    def _execute(self):
        self._outSlot.setValue(256.0)

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class BattleGetVehicleInsigniaRank(Block, VehicleMeta):

    def __init__(self, *args, **kwargs):
        super(BattleGetVehicleInsigniaRank, self).__init__(*args, **kwargs)
        self._vehicle = self._makeDataInputSlot('vehicle', SLOT_TYPE.VEHICLE)
        self._insigniaRank = self._makeDataOutputSlot('insigniaRank', SLOT_TYPE.INT, self._exec)

    def _exec(self):
        vehicle = self._vehicle.getValue()
        if vehicle is None:
            errorVScript(self, 'Vehicle object is invalid.')
            self._insigniaRank.setValue(0)
            return
        else:
            insigniaRank = vehicle.publicInfo['marksOnGun']
            self._insigniaRank.setValue(insigniaRank)
            return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class HangarGetVehicleInsigniaRank(Block, VehicleMeta):

    def __init__(self, *args, **kwargs):
        super(HangarGetVehicleInsigniaRank, self).__init__(*args, **kwargs)
        self._vehicleObject = self._makeDataInputSlot('hangarVehicleObject', SLOT_TYPE.GAME_OBJECT)
        self._insigniaRank = self._makeDataOutputSlot('insigniaRank', SLOT_TYPE.INT, self._exec)

    def _exec(self):
        vehicleObject = self._vehicleObject.getValue()
        if vehicleObject is None:
            errorVScript(self, 'GameObject is invalid.')
            self._insigniaRank.setValue(0)
            return
        else:
            entityGoSync = vehicleObject.findComponentByType(GenericComponents.EntityGOSync)
            if entityGoSync is None or entityGoSync.entity is None or entityGoSync.entity.appearance is None:
                errorVScript(self, 'Could not find vehicle entity, associated with gameObject')
                self._insigniaRank.setValue(0)
                return
            insigniaRank = entityGoSync.entity.appearance.getThisVehicleDossierInsigniaRank()
            self._insigniaRank.setValue(insigniaRank)
            return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.HANGAR]
