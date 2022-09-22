# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/cgf_blocks.py
import weakref
from visual_script.block import Block, Meta
from visual_script.slot_types import SLOT_TYPE
from visual_script.misc import ASPECT
from visual_script.dependency import dependencyImporter
from contexts.cgf_context import GameObjectWrapper
Vehicle, CGF, tankStructure, GenericComponents = dependencyImporter('Vehicle', 'CGF', 'vehicle_systems.tankStructure', 'GenericComponents')

class CGFMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT, ASPECT.HANGAR]


class GetVehicleAppearanceGameObject(Block, CGFMeta):

    def __init__(self, *args, **kwargs):
        super(GetVehicleAppearanceGameObject, self).__init__(*args, **kwargs)
        self._object = self._makeDataInputSlot('gameObject', SLOT_TYPE.GAME_OBJECT)
        self._appObject = self._makeDataOutputSlot('appearanceObject', SLOT_TYPE.GAME_OBJECT, self._exec)

    def validate(self):
        return 'GameObject is required' if not self._object.hasValue() else super(GetVehicleAppearanceGameObject, self).validate()

    def _exec(self):
        currentGO = self._object.getValue()
        hierarchy = CGF.HierarchyManager(currentGO.spaceID)
        topGO = hierarchy.getTopMostParent(currentGO)
        currentGO = hierarchy.findFirstNode(topGO, tankStructure.CgfTankNodes.TANK_ROOT)
        if currentGO is not None:
            goWrapper = GameObjectWrapper(currentGO)
            self._appObject.setValue(weakref.proxy(goWrapper))
        else:
            self._appObject.setValue(None)
        return


class GetVehicleGameObject(Block, CGFMeta):

    def __init__(self, *args, **kwargs):
        super(GetVehicleGameObject, self).__init__(*args, **kwargs)
        self._object = self._makeDataInputSlot('gameObject', SLOT_TYPE.GAME_OBJECT)
        self._vehicleObject = self._makeDataOutputSlot('vehicleObject', SLOT_TYPE.GAME_OBJECT, self._exec)

    def validate(self):
        return 'GameObject is required' if not self._object.hasValue() else super(GetVehicleGameObject, self).validate()

    def _exec(self):
        currentGO = self._object.getValue()
        hierarchy = CGF.HierarchyManager(currentGO.spaceID)
        topGO = hierarchy.getTopMostParent(currentGO)
        if topGO.findComponentByType(Vehicle.Vehicle) is not None:
            goWrapper = GameObjectWrapper(topGO)
            self._vehicleObject.setValue(weakref.proxy(goWrapper))
        else:
            self._vehicleObject.setValue(None)
        return


class SpawnPrefab(Block, CGFMeta):

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
        vehicle = self.__getVehicle(gameObject)
        if vehicle and vehicle.appearance:
            gameObject.createComponent(GenericComponents.RedirectorComponent, vehicle.appearance.gameObject)
            gameObject.createComponent(GenericComponents.DynamicModelComponent, vehicle.appearance.compoundModel)
        goWrapper = GameObjectWrapper(gameObject)
        self._go.setValue(weakref.proxy(goWrapper))
        self._out.call()

    def __getVehicle(self, gameObject):
        hierarchy = CGF.HierarchyManager(gameObject.spaceID)
        parent = hierarchy.getTopMostParent(gameObject)
        return parent.findComponentByType(Vehicle.Vehicle)

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class TransferOwnershipToWorld(Block, CGFMeta):

    def __init__(self, *args, **kwargs):
        super(TransferOwnershipToWorld, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._exec)
        self._go = self._makeDataInputSlot('GO', SLOT_TYPE.GAME_OBJECT)
        self._out = self._makeEventOutputSlot('out')

    def _exec(self):
        if self._go.hasValue():
            go = self._go.getValue()
            if go is not None:
                go.transferOwnershipToWorld()
        self._out.call()
        return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]
