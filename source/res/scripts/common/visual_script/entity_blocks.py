# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/entity_blocks.py
import BigWorld
import weakref
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


class Config(Block, EntityMeta):

    def __init__(self, *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)
        params = self._getInitParams()[0]
        self._res = self._makeDataOutputSlot('res', SLOT_TYPE.SCRIPT_OBJECT, self._get)
        self._slots = slots = {}
        for param in params.split(';'):
            param = param.strip()
            if not param:
                continue
            pname, ptype = param.split('=')
            slots[pname] = self._makeDataInputSlot(pname, ptype)

    @classmethod
    def initParams(cls):
        return super(Config, cls).initParams() + [InitParam('Params', SLOT_TYPE.STR, '')]

    def _get(self):
        res = {}
        for name, slot in self._slots.iteritems():
            res[name] = slot.getValue()

        self._res.setValue(res)


class CreateEntity(Block, EntityMeta):

    def __init__(self, *args, **kwargs):
        super(CreateEntity, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._arena = self._makeDataInputSlot('arena', SLOT_TYPE.ARENA)
        self._type = self._makeDataInputSlot('type', SLOT_TYPE.STR)
        self._position = self._makeDataInputSlot('position', SLOT_TYPE.VECTOR3)
        self._out = self._makeEventOutputSlot('out')
        self._entity = self._makeDataOutputSlot('entity', SLOT_TYPE.ENTITY, None)
        return

    def _execute(self):
        entity = BigWorld.createEntity(self._type.getValue(), self._arena.getValue().spaceID, self._position.getValue(), (0, 0, 0), {})
        self._entity.setValue(weakref.proxy(entity))
        self._out.call()


class DestroyEntity(Block, EntityMeta):

    def __init__(self, *args, **kwargs):
        super(DestroyEntity, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._entity = self._makeDataInputSlot('entity', SLOT_TYPE.ENTITY)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        entity = self._entity.getValue()
        if entity is not None:
            entity.destroy()
        else:
            errorVScript(self, 'Cannot destroy entity: entity is None')
        self._out.call()
        return


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


class HasComponent(Block, EntityMeta):

    def __init__(self, *args, **kwargs):
        super(HasComponent, self).__init__(*args, **kwargs)
        self._entity = self._makeDataInputSlot('entity', SLOT_TYPE.ENTITY)
        self._name = self._makeDataInputSlot('name', SLOT_TYPE.STR)
        self._res = self._makeDataOutputSlot('res', SLOT_TYPE.BOOL, self._check)

    def _check(self):
        entity = self._entity.getValue()
        name = self._name.getValue()
        self._res.setValue(entity is not None and not entity.isDestroyed and name in entity.dynamicComponents)
        return


class RemoveComponent(Block, EntityMeta):

    def __init__(self, *args, **kwargs):
        super(RemoveComponent, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._exec)
        self._entity = self._makeDataInputSlot('entity', SLOT_TYPE.ENTITY)
        n = self._getInitParams()
        self._slots = [ self._makeDataInputSlot('name{}'.format(i), SLOT_TYPE.STR) for i in xrange(n) ]
        self._out = self._makeEventOutputSlot('out')

    @classmethod
    def initParams(cls):
        return [InitParam('paramCount', SLOT_TYPE.INT, 1)]

    def _exec(self):
        entity = self._entity.getValue()
        slots = self._slots
        if entity is None or entity.isDestroyed:
            self._out.call()
            return
        else:
            for slot in slots:
                name = slot.getValue()
                if name in entity.dynamicComponents:
                    component = entity.dynamicComponents.get(name)
                    if component is not None:
                        component.destroy()

            self._out.call()
            return


class FindEntitiesWithComponents(Block, EntityMeta):

    def __init__(self, *args, **kwargs):
        super(FindEntitiesWithComponents, self).__init__(*args, **kwargs)
        self._arena = self._makeDataInputSlot('arena', SLOT_TYPE.ARENA)
        self._typename = self._makeDataInputSlot('typename', SLOT_TYPE.STR)
        n = self._getInitParams()
        self._slots = [ self._makeDataInputSlot('name{}'.format(i), SLOT_TYPE.STR) for i in xrange(n) ]
        self._entities = self._makeDataOutputSlot('entities', arrayOf(SLOT_TYPE.ENTITY), self._find)

    @classmethod
    def initParams(cls):
        return [InitParam('paramCount', SLOT_TYPE.INT, 1)]

    def _find(self):
        arena = self._arena.getValue()
        typename = self._typename.getValue()
        components = set()
        for slot in self._slots:
            components.add(slot.getValue())

        entities = []
        for entity in BigWorld.entities.valuesOfType(typename, arena.spaceID):
            if components.issubset(entity.dynamicComponents.keys()):
                entities.append(weakref.proxy(entity))

        self._entities.setValue(entities)
