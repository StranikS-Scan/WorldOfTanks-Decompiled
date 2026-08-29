# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/visual_script_client/cgf_blocks.py
from __future__ import absolute_import
import BigWorld
import weakref
import logging
import Math
from functools import partial
from visual_script.block import Block, InitParam, buildStrKeysValue
from visual_script.slot_types import SLOT_TYPE
from visual_script.misc import ASPECT, EDITOR_TYPE
from visual_script.dependency import dependencyImporter
from visual_script.contexts.cgf_context import GameObjectWrapper
from visual_script.cgf_blocks import CGFMeta
Vehicle, CGF, tankStructure, RAC, SimulatedVehicle = dependencyImporter('Vehicle', 'CGF', 'vehicle_systems.tankStructure', 'cgf_components.rocket_acceleration_component', 'SimulatedVehicle')
GenericComponents = dependencyImporter('GenericComponents')
_logger = logging.getLogger(__name__)

class AttachComponent(Block, CGFMeta):

    def __init__(self, *args, **kwargs):
        super(AttachComponent, self).__init__(*args, **kwargs)
        self._paramType = self._getInitParams()
        self._activate = self._makeEventInputSlot('in', self._execute)
        self._gameObject = self._makeDataInputSlot('TargetGO', SLOT_TYPE.GAME_OBJECT)
        self._out = self._makeEventOutputSlot('out')
        self._gameObjectOut = self._makeDataOutputSlot('object', SLOT_TYPE.GAME_OBJECT, None)
        return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]

    def _execute(self):
        targetGameObject = self._gameObject.getValue()
        vehicle = self.__getVehicle(targetGameObject)
        _componentsMap = {'RedirectorComponent': (GenericComponents.RedirectorComponent, vehicle.appearance.gameObject)}
        component, attachTarget = _componentsMap.get(self._paramType[0])
        if vehicle and vehicle.appearance and component and attachTarget:
            queue = CGF.CommandQueue(targetGameObject.spaceID)
            queue.createComponent(targetGameObject, component, attachTarget)
        goWrapper = GameObjectWrapper(targetGameObject)
        self._gameObjectOut.setValue(weakref.proxy(goWrapper))
        self._out.call()

    def __getVehicle(self, gameObject):
        hierarchy = CGF.findHierarchySingleton(gameObject.spaceID)
        parent = hierarchy.getTopMostParent(gameObject)
        return parent.findRead(Vehicle.Vehicle)

    def captionText(self):
        return 'Attach: ' + self._paramType[0]

    @classmethod
    def initParams(cls):
        _componentsArray = ['RedirectorComponent']
        return [InitParam('Data type', SLOT_TYPE.STR, buildStrKeysValue(*_componentsArray), EDITOR_TYPE.STR_KEY_SELECTOR)]


class AttachToEntity(Block, CGFMeta):

    def __init__(self, *args, **kwargs):
        super(AttachToEntity, self).__init__(*args, **kwargs)
        self._paramType = self._getInitParams()
        self._activate = self._makeEventInputSlot('in', self._execute)
        self._gameObject = self._makeDataInputSlot('TargetGO', SLOT_TYPE.GAME_OBJECT)
        self._entity = self._makeDataInputSlot('entity', SLOT_TYPE.ENTITY)
        self._out = self._makeEventOutputSlot('out')
        self._gameObjectOut = self._makeDataOutputSlot('object', SLOT_TYPE.GAME_OBJECT, None)
        return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]

    def _execute(self):
        targetGameObject = self._gameObject.getValue()
        entity = self._entity.getValue()
        vehicle = self.__getVehicle(targetGameObject)
        appearance = entity.appearance
        _componentsMap = {'RedirectorComponent': (GenericComponents.RedirectorComponent, appearance.gameObject)}
        component, attachTarget = _componentsMap.get(self._paramType[0])
        if vehicle and vehicle.appearance and component and attachTarget:
            queue = CGF.CommandQueue(targetGameObject.spaceID)
            queue.removeComponent(targetGameObject, component)
            queue.createComponent(targetGameObject, component, attachTarget)
        goWrapper = GameObjectWrapper(targetGameObject)
        self._gameObjectOut.setValue(weakref.proxy(goWrapper))
        self._out.call()

    def __getVehicle(self, gameObject):
        hierarchy = CGF.findHierarchySingleton(gameObject.spaceID)
        parent = hierarchy.getTopMostParent(gameObject)
        return parent.findRead(Vehicle.Vehicle)

    def captionText(self):
        return 'Attach: ' + self._paramType[0]

    @classmethod
    def initParams(cls):
        _componentsArray = ['RedirectorComponent']
        return [InitParam('Data type', SLOT_TYPE.STR, buildStrKeysValue(*_componentsArray), EDITOR_TYPE.STR_KEY_SELECTOR)]


class WTAddBossDestroyVFXPrefab(Block, CGFMeta):

    def __init__(self, *args, **kwargs):
        super(WTAddBossDestroyVFXPrefab, self).__init__(*args, **kwargs)
        self._activate = self._makeEventInputSlot('in', self._execute)
        self._parentGO = self._makeDataInputSlot('Parent', SLOT_TYPE.GAME_OBJECT)
        self._partGO = self._makeDataInputSlot('Tank Part', SLOT_TYPE.GAME_OBJECT)
        self._prefabPath = self._makeDataInputSlot('Prefab Resource', SLOT_TYPE.RESOURCE)
        self._hideTankDelay = self._makeDataInputSlot('Hide Tank Delay', SLOT_TYPE.FLOAT)
        self._entity = self._makeDataInputSlot('Entity', SLOT_TYPE.ENTITY)
        self._out = self._makeEventOutputSlot('out')
        self._gameObjectOut = self._makeDataOutputSlot('object', SLOT_TYPE.GAME_OBJECT, None)
        return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]

    def _execute(self):
        parentGO = self._parentGO.getValue()
        partGO = self._partGO.getValue()
        prefabPath = self._prefabPath.getValue()
        entity = self._entity.getValue()
        hideTankDelay = self._hideTankDelay.getValue()
        parentTransform = parentGO.findWrite(CGF.TransformComponent)
        partTransform = partGO.findRead(CGF.TransformComponent)
        hierarchy = CGF.findHierarchySingleton(partGO.spaceID)
        parent = hierarchy.getTopMostParent(partGO)
        vehicle = parent.findRead(Vehicle.Vehicle)
        parentTransform.position = partTransform.worldPosition
        parentTransform.rotation = partTransform.worldRotation
        appearance = entity.appearance
        if vehicle and vehicle.appearance and appearance:
            CGF.loadAndCreatePrefabWithParent(prefabPath, parentGO, Math.Vector3(0, 0, 0), lambda objects, queue: BigWorld.callback(hideTankDelay, partial(self.hideVehicle, parent)))
            q = CGF.CommandQueue(parentGO.spaceID)
            q.removeComponent(parentGO, GenericComponents.RedirectorComponent)
            q.createComponent(parentGO, GenericComponents.RedirectorComponent, appearance.gameObject)
        goWrapper = GameObjectWrapper(parentGO)
        self._gameObjectOut.setValue(weakref.proxy(goWrapper))
        self._out.call()

    def hideVehicle(self, vehicleObj):
        if not vehicleObj or not vehicleObj.valid:
            _logger.warning('[WTAddBossDestroyVFXPrefab] callback hideVehicle: vehicleObj is invalid')
            return
        vehicle = vehicleObj.findWrite(Vehicle.Vehicle)
        if vehicle and hasattr(vehicle, 'appearance') and vehicle.appearance.compoundModel:
            vehicle.appearance.compoundModel.visible = False
