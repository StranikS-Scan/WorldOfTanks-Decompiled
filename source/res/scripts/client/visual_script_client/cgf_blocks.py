# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/cgf_blocks.py
import weakref
from visual_script.block import Block, Meta
from visual_script.slot_types import SLOT_TYPE
from visual_script.misc import ASPECT
from visual_script.dependency import dependencyImporter
from contexts.cgf_context import GameObjectWrapper
Vehicle, CGF, tankStructure = dependencyImporter('Vehicle', 'CGF', 'vehicle_systems.tankStructure')

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
        return [ASPECT.CLIENT]


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
