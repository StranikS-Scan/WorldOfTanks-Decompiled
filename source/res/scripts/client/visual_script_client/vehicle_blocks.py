# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/vehicle_blocks.py
import weakref
import BigWorld
from visual_script.block import Block
from visual_script.slot_types import SLOT_TYPE
from visual_script.misc import ASPECT, errorVScript
from visual_script.tunable_event_block import TunableEventBlock
from visual_script.vehicle_blocks import VehicleMeta

class GetVehicleLabel(Block, VehicleMeta):

    def __init__(self, *args, **kwargs):
        super(GetVehicleLabel, self).__init__(*args, **kwargs)
        self._vehicle = self._makeDataInputSlot('vehicle', SLOT_TYPE.VEHICLE)
        self._label = self._makeDataOutputSlot('label', SLOT_TYPE.STR, self._getLabel)

    def _getLabel(self):
        label = self._vehicle.getValue().label
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
        BigWorld.player().arena.onVehicleKilled -= self.__onVehicleKilled

    @TunableEventBlock.eventProcessor
    def __onVehicleKilled(self, targetID, attackerID, equipmentID, reason):
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
        extra = v.typeDescriptor.extrasDict['fire']
        res = extra is not None and extra.isRunningFor(v)
        self._res.setValue(res)
        return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]
