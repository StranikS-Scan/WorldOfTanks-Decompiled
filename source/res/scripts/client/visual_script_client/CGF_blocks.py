# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/CGF_blocks.py
from visual_script.block import Block, Meta, ASPECT
from visual_script.slot_types import SLOT_TYPE
from visual_script.dependency import dependencyImporter
from visual_script.all_vstypes import GameObject
CGF, GenericComponents = dependencyImporter('CGF', 'GenericComponents')

class SpawnPrefab(Block, Meta):

    def __init__(self, *args, **kwargs):
        super(SpawnPrefab, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._exec)
        self._entity = self._makeDataInputSlot('entity', SLOT_TYPE.ENTITY)
        self._prefab = self._makeDataInputSlot('prefab', SLOT_TYPE.STR)
        self._matrix = self._makeDataInputSlot('matrix', SLOT_TYPE.MATRIX4)
        self._out = self._makeEventOutputSlot('out')
        self._go = self._makeDataOutputSlot('GO', SLOT_TYPE.GAME_OBJECT, None)
        return

    def _exec(self):
        vehicle = self._entity.getValue()
        parent = vehicle.entityGameObject
        matrix = self._matrix.getValue()
        if parent is not None and parent.isValid():
            CGF.loadGameObjectIntoHierarchy(self._prefab.getValue(), parent, matrix, self.__onGameObjectLoaded)
        return

    def __onGameObjectLoaded(self, gameObject):
        go = GameObject(gameObject)
        entity = self._entity.getValue()
        if hasattr(entity, 'appearance') and entity.appearance is not None:
            appearance = entity.appearance
            gameObject.createComponent(GenericComponents.RedirectorComponent, appearance.gameObject)
            gameObject.createComponent(GenericComponents.DynamicModelComponent, appearance.compoundModel)
        self._go.setValue(go)
        self._out.call()
        return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class RemoveGO(Block, Meta):

    def __init__(self, *args, **kwargs):
        super(RemoveGO, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._exec)
        self._go = self._makeDataInputSlot('GO', SLOT_TYPE.GAME_OBJECT)
        self._out = self._makeEventOutputSlot('out')

    def _exec(self):
        if self._go.hasValue():
            go = self._go.getValue()
            if go is not None:
                CGF.removeGameObject(go.gameObject)
        self._out.call()
        return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class TransferOwnershipToWorld(Block, Meta):

    def __init__(self, *args, **kwargs):
        super(TransferOwnershipToWorld, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._exec)
        self._go = self._makeDataInputSlot('GO', SLOT_TYPE.GAME_OBJECT)
        self._out = self._makeEventOutputSlot('out')

    def _exec(self):
        if self._go.hasValue():
            go = self._go.getValue()
            if go is not None:
                go.gameObject.transferOwnershipToWorld()
        self._out.call()
        return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]
