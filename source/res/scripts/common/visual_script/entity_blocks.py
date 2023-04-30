# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/entity_blocks.py
import BigWorld
import weakref
import Math
import items
from visual_script.block import Meta, Block, InitParam, buildStrKeysValue, EDITOR_TYPE
from visual_script.slot_types import SLOT_TYPE, arrayOf
from visual_script.misc import ASPECT, errorVScript

class EntityMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass


class CreateEntity(Block, EntityMeta):

    def __init__(self, *args, **kwargs):
        super(CreateEntity, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._arena = self._makeDataInputSlot('arena', SLOT_TYPE.ARENA)
        self._type = self._makeDataInputSlot('type', SLOT_TYPE.STR)
        self._position = self._makeDataInputSlot('position', SLOT_TYPE.VECTOR3)
        self._direction = self._makeDataInputSlot('direction', SLOT_TYPE.VECTOR3)
        self._out = self._makeEventOutputSlot('out')
        self._entity = self._makeDataOutputSlot('entity', SLOT_TYPE.ENTITY, None)
        return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.SERVER]

    def validate(self):
        if not self._arena.hasValue():
            return 'Arena value is required'
        if not self._type.hasValue():
            return 'Type value is required'
        return 'Position value is required' if not self._position.hasValue() else ''

    def _execute(self):
        mat = Math.Matrix()
        direction = self._direction.getValue() if self._direction.hasValue() else Math.Vector3(1.0, 0.0, 0.0)
        mat.lookAt(Math.Vector3(0.0, 0.0, 0.0), direction, Math.Vector3(0.0, 1.0, 0.0))
        entity = BigWorld.createEntity(self._type.getValue(), self._arena.getValue().spaceID, self._position.getValue(), (mat.roll, mat.pitch, mat.yaw), {})
        self._entity.setValue(weakref.proxy(entity))
        self._out.call()


class CreateApplicationPoint(Block, EntityMeta):

    def __init__(self, *args, **kwargs):
        super(CreateApplicationPoint, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._arena = self._makeDataInputSlot('arena', SLOT_TYPE.ARENA)
        self._vehicle = self._makeDataInputSlot('vehicle', SLOT_TYPE.VEHICLE)
        self._equipmentName = self._makeDataInputSlot('equipmentName', SLOT_TYPE.STR)
        self._position = self._makeDataInputSlot('position', SLOT_TYPE.VECTOR3)
        self._direction = self._makeDataInputSlot('direction', SLOT_TYPE.VECTOR3)
        self._level = self._makeDataInputSlot('level', SLOT_TYPE.INT)
        self._out = self._makeEventOutputSlot('out')
        self._entity = self._makeDataOutputSlot('entity', SLOT_TYPE.ENTITY, None)
        return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.SERVER]

    def validate(self):
        if not self._arena.hasValue():
            return 'Arena value is required'
        if not self._vehicle.hasValue():
            return 'Vehicle value is required'
        if not self._equipmentName.hasValue():
            return 'EquipmentName value is required'
        return 'Position value is required' if not self._position.hasValue() else ''

    def _execute(self):
        mat = Math.Matrix()
        direction = self._direction.getValue() if self._direction.hasValue() else Math.Vector3(1.0, 0.0, 0.0)
        mat.lookAt(Math.Vector3(0.0, 0.0, 0.0), direction, Math.Vector3(0.0, 1.0, 0.0))
        vehicle = self._vehicle.getValue()
        equipmentName = self._equipmentName.getValue()
        equipmentID = items.vehicles.g_cache.equipmentIDs().get(equipmentName)
        if equipmentID is None:
            errorVScript(self, 'Unknown equipment [{}]'.format(equipmentName))
            return
        else:
            entity = BigWorld.createEntity('ApplicationPoint', self._arena.getValue().spaceID, self._position.getValue(), (mat.roll, mat.pitch, mat.yaw), {'vehicleID': vehicle.id,
             'equipmentID': equipmentID,
             'launchTime': BigWorld.time(),
             'level': self._level.getValue()})
            self._entity.setValue(weakref.proxy(entity))
            self._out.call()
            return


class DestroyEntity(Block, EntityMeta):

    def __init__(self, *args, **kwargs):
        super(DestroyEntity, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._entity = self._makeDataInputSlot('entity', SLOT_TYPE.ENTITY)
        self._ignoreIfMissing = self._makeDataInputSlot('ignoreIfMissing', SLOT_TYPE.BOOL)
        self._ignoreIfMissing.setDefaultValue(False)
        self._out = self._makeEventOutputSlot('out')

    @classmethod
    def blockAspects(cls):
        return [ASPECT.SERVER]

    def _execute(self):
        entity = self._entity.getValue()
        try:
            entity.destroy()
        except (AttributeError, ReferenceError):
            if not self._ignoreIfMissing.getValue():
                errorVScript(self, 'Cannot destroy entity: entity is None')

        self._out.call()


class IsEntityOfType(Block, EntityMeta):
    _types = ('EmptyEntity', 'Vehicle')

    def __init__(self, *args, **kwargs):
        super(IsEntityOfType, self).__init__(*args, **kwargs)
        self._entity = self._makeDataInputSlot('entity', SLOT_TYPE.ENTITY)
        self._type = self._getInitParams()
        self._res = self._makeDataOutputSlot('res', SLOT_TYPE.BOOL, self._execute)

    @classmethod
    def initParams(cls):
        return super(IsEntityOfType, cls).initParams() + [InitParam('Type', SLOT_TYPE.STR, buildStrKeysValue(*cls._types), EDITOR_TYPE.STR_KEY_SELECTOR)]

    def captionText(self):
        return 'Is Entity ' + self._type

    def _execute(self):
        self._res.setValue(self._entity.getValue().className == self._type)


class BoardEntity(Block, EntityMeta):

    def __init__(self, *args, **kwargs):
        super(BoardEntity, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._exec)
        self._entity = self._makeDataInputSlot('entity', SLOT_TYPE.ENTITY)
        self._vehicle = self._makeDataInputSlot('vehicle', SLOT_TYPE.ENTITY)
        self._out = self._makeEventOutputSlot('out')

    @classmethod
    def blockAspects(cls):
        return [ASPECT.SERVER]

    def _exec(self):
        entity = self._entity.getValue()
        vehicle = self._vehicle.getValue()
        entity.boardVehicle(vehicle.id)
        self._out.call()


class Teleport(Block, EntityMeta):

    def __init__(self, *args, **kwargs):
        super(Teleport, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._exec)
        self._entity = self._makeDataInputSlot('entity', SLOT_TYPE.ENTITY)
        self._position = self._makeDataInputSlot('position', SLOT_TYPE.VECTOR3)
        self._direction = self._makeDataInputSlot('direction', SLOT_TYPE.VECTOR3)
        self._out = self._makeEventOutputSlot('out')

    @classmethod
    def blockAspects(cls):
        return [ASPECT.SERVER]

    def validate(self):
        if not self._entity.hasValue():
            return 'Entity value is required'
        return 'Position value is required' if not self._position.hasValue() else ''

    def _exec(self):
        entity = self._entity.getValue()
        position = self._position.getValue()
        if self._direction.hasValue():
            direction = self._direction.getValue()
        else:
            direction = (entity.yaw, entity.pitch, entity.roll)
        entity.teleport(None, position, direction)
        self._out.call()
        return


class GetEntityId(Block, EntityMeta):

    def __init__(self, *args, **kwargs):
        super(GetEntityId, self).__init__(*args, **kwargs)
        self._entity = self._makeDataInputSlot('entity', SLOT_TYPE.ENTITY)
        self._res = self._makeDataOutputSlot('id', SLOT_TYPE.INT, self._exec)

    def _exec(self):
        entity = self._entity.getValue()
        if entity:
            self._res.setValue(entity.id)


class GetEntityTransform(Block, EntityMeta):

    def __init__(self, *args, **kwargs):
        super(GetEntityTransform, self).__init__(*args, **kwargs)
        self._entity = self._makeDataInputSlot('entity', SLOT_TYPE.ENTITY)
        self._position = self._makeDataOutputSlot('position', SLOT_TYPE.VECTOR3, self._exec)
        self._direction = self._makeDataOutputSlot('direction', SLOT_TYPE.VECTOR3, self._exec)
        self._yaw = self._makeDataOutputSlot('yaw', SLOT_TYPE.FLOAT, self._exec)
        self._pitch = self._makeDataOutputSlot('pitch', SLOT_TYPE.FLOAT, self._exec)
        self._roll = self._makeDataOutputSlot('roll', SLOT_TYPE.FLOAT, self._exec)

    def _exec(self):
        entity = self._entity.getValue()
        if entity:
            self._position.setValue(entity.position)
            self._direction.setValue(entity.direction)
            self._yaw.setValue(entity.yaw)
            self._pitch.setValue(entity.pitch)
            self._roll.setValue(entity.roll)


class IsEntityDestroyed(Block, EntityMeta):

    def __init__(self, *args, **kwargs):
        super(IsEntityDestroyed, self).__init__(*args, **kwargs)
        self._entity = self._makeDataInputSlot('entity', SLOT_TYPE.ENTITY)
        self._isDestroyed = self._makeDataOutputSlot('isDestroyed', SLOT_TYPE.BOOL, self._exec)

    @classmethod
    def blockAspects(cls):
        return [ASPECT.SERVER]

    def _exec(self):
        entity = self._entity.getValue()
        if entity:
            self._isDestroyed.setValue(entity.isDestroyed)
        else:
            self._isDestroyed.setValue(True)
