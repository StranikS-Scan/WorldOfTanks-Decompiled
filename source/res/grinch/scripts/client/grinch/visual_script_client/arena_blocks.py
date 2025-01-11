# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/visual_script_client/arena_blocks.py
import logging
import BigWorld
from visual_script.arena_blocks import ArenaMeta
from visual_script.block import Block, InitParam
from visual_script.cgf_blocks import CGFMeta
from visual_script.misc import ASPECT
from visual_script.slot_types import SLOT_TYPE, arrayOf
from visual_script.contexts.cgf_context import GameObjectWrapper
from grinch_common.shared_helpers import safeWeakProxy
from grinch_common.grinch_constants import GrinchClientArenaComponents
_logger = logging.getLogger(__name__)

class CacheGameObjects(Block, CGFMeta):

    def __init__(self, *args, **kwargs):
        super(CacheGameObjects, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._out = self._makeEventOutputSlot('out')
        self._prefabs = self._makeDataInputSlot('prefabs', arrayOf(SLOT_TYPE.STR))

    @classmethod
    def blockIcon(cls):
        pass

    def _execute(self):
        import CGF
        prefabsSet = set(self._prefabs.getValue())
        CGF.cacheGameObjects(list(prefabsSet), False)

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class ClearCacheGameObjects(Block, CGFMeta):

    def __init__(self, *args, **kwargs):
        super(ClearCacheGameObjects, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._out = self._makeEventOutputSlot('out')
        self._prefabs = self._makeDataInputSlot('prefabs', arrayOf(SLOT_TYPE.STR))

    @classmethod
    def blockIcon(cls):
        pass

    def _execute(self):
        import CGF
        prefabsSet = set(self._prefabs.getValue())
        CGF.clearGameObjectsCache(list(prefabsSet))
        prefabsSet.clear()

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class OnDynamicComponentCreatedOnVehicle(Block, ArenaMeta):

    def __init__(self, *args, **kwargs):
        super(OnDynamicComponentCreatedOnVehicle, self).__init__(*args, **kwargs)
        self._out = self._makeEventOutputSlot('out')
        self._vehicle = self._makeDataOutputSlot('vehicle', SLOT_TYPE.VEHICLE, None)
        self._componentName = self._makeDataOutputSlot('componentName', SLOT_TYPE.STR, None)
        return

    @classmethod
    def initParams(cls):
        return [InitParam(name='Component key name', slotType=SLOT_TYPE.STR, defaultValue='')]

    def validate(self):
        return 'Component name is required!' if not self.componentName else super(OnDynamicComponentCreatedOnVehicle, self).validate()

    @classmethod
    def blockIcon(cls):
        pass

    @property
    def componentName(self):
        componentName = self._getInitParams()
        return componentName

    def captionText(self):
        return 'OnDynamicComponentCreatedOnVehicle: {}'.format(self.componentName)

    def onStartScript(self):
        BigWorld.player().arena.onDynamicComponentCreatedOnVehicle += self.__onCreated

    def onFinishScript(self):
        BigWorld.player().arena.onDynamicComponentCreatedOnVehicle -= self.__onCreated

    def __onCreated(self, component):
        if not hasattr(component, 'keyName'):
            return
        blockComponentName = self.componentName
        if blockComponentName != component.keyName:
            return
        self._vehicle.setValue(safeWeakProxy(component.entity))
        self._componentName.setValue(blockComponentName)
        self._out.call()

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class OnDynamicComponentDestroyedOnVehicle(Block, ArenaMeta):

    def __init__(self, *args, **kwargs):
        super(OnDynamicComponentDestroyedOnVehicle, self).__init__(*args, **kwargs)
        self._out = self._makeEventOutputSlot('out')
        self._vehicle = self._makeDataOutputSlot('vehicle', SLOT_TYPE.VEHICLE, None)
        self._componentName = self._makeDataOutputSlot('componentName', SLOT_TYPE.STR, None)
        return

    @classmethod
    def blockIcon(cls):
        pass

    def onStartScript(self):
        BigWorld.player().arena.onDynamicComponentDestroyedOnVehicle += self.__onDestroyed
        BigWorld.player().onVehicleLeaveWorld += self.__onVehicleLeave

    def onFinishScript(self):
        BigWorld.player().arena.onDynamicComponentDestroyedOnVehicle -= self.__onDestroyed
        BigWorld.player().onVehicleLeaveWorld -= self.__onVehicleLeave

    def __onDestroyed(self, component):
        if not hasattr(component, 'keyName'):
            return
        self._vehicle.setValue(safeWeakProxy(component.entity))
        self._componentName.setValue(component.keyName)
        self._out.call()

    def __onVehicleLeave(self, vehicle):
        if vehicle.isAlive():
            for dc in vehicle.dynamicComponents.itervalues():
                self.__onDestroyed(dc)

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class StoreVisualStateGO(Block, ArenaMeta):

    def __init__(self, *args, **kwargs):
        super(StoreVisualStateGO, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self.__execute)
        self._vehicleGO = self._makeDataInputSlot('vehicleGameObject', SLOT_TYPE.GAME_OBJECT)
        self._componentName = self._makeDataInputSlot('componentName', SLOT_TYPE.STR)
        self._visualsGO = self._makeDataInputSlot('visualsGameObject', SLOT_TYPE.GAME_OBJECT)
        self._out = self._makeEventOutputSlot('out')

    @classmethod
    def blockIcon(cls):
        pass

    def __execute(self):
        vehicleGO = self._vehicleGO.getValue()
        componentName = self._componentName.getValue()
        visualsGO = self._visualsGO.getValue()
        storageComponent = getattr(BigWorld.player().arena.componentSystem, GrinchClientArenaComponents.GRINCH_VISUAL_STATE_GO_STORAGE, None)
        if storageComponent:
            import Vehicle
            vehicle = vehicleGO.findComponentByType(Vehicle.Vehicle)
            if vehicle:
                if componentName in vehicle.dynamicComponents:
                    storageComponent.storeGO(vehicleGO.id, componentName, visualsGO)
                else:
                    _logger.debug("Failed to find '%s' component for vehicle id=%d", componentName, vehicle.id)
                    import CGF
                    CGF.removeGameObject(visualsGO)
            else:
                _logger.debug('Could not find vehicle for GO id=%d', vehicleGO.id)
        self._out.call()
        return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class RetrieveVisualStateGO(Block, ArenaMeta):

    def __init__(self, *args, **kwargs):
        super(RetrieveVisualStateGO, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self.__execute)
        self._vehicleGO = self._makeDataInputSlot('vehicleGameObject', SLOT_TYPE.GAME_OBJECT)
        self._componentName = self._makeDataInputSlot('componentName', SLOT_TYPE.STR)
        self._out = self._makeEventOutputSlot('out')
        self._visualsGO = self._makeDataOutputSlot('visualsGameObject', SLOT_TYPE.GAME_OBJECT, None)
        return

    @classmethod
    def blockIcon(cls):
        pass

    def __execute(self):
        vehicleGO = self._vehicleGO.getValue()
        componentName = self._componentName.getValue()
        storageComponent = getattr(BigWorld.player().arena.componentSystem, GrinchClientArenaComponents.GRINCH_VISUAL_STATE_GO_STORAGE, None)
        if storageComponent:
            visualsGO = storageComponent.retrieveGO(vehicleGO.id, componentName)
            if visualsGO and visualsGO.isValid():
                goWrapper = GameObjectWrapper(visualsGO)
                self._visualsGO.setValue(safeWeakProxy(goWrapper))
                self._out.call()
        return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class GetVehicleClass(Block, ArenaMeta):

    def __init__(self, *args, **kwargs):
        super(GetVehicleClass, self).__init__(*args, **kwargs)
        self._vehicle = self._makeDataInputSlot('vehicle', SLOT_TYPE.VEHICLE)
        self._classTag = self._makeDataOutputSlot('classTag', SLOT_TYPE.STR, self._execute)

    def _execute(self):
        vehicle = self._vehicle.getValue()
        self._classTag.setValue(vehicle.typeDescriptor.type.classTag)

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class DetachFromHierarchy(Block, CGFMeta):

    def __init__(self, *args, **kwargs):
        super(DetachFromHierarchy, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._exec)
        self._go = self._makeDataInputSlot('gameObject', SLOT_TYPE.GAME_OBJECT)
        self._out = self._makeEventOutputSlot('out')

    def validate(self):
        return 'GameObject is required' if not self._go.hasValue() else super(DetachFromHierarchy, self).validate()

    def _exec(self):
        go = self._go.getValue()
        if go and go.isValid():
            import GenericComponents
            transformComponent = go.findComponentByType(GenericComponents.TransformComponent)
            worldTransform = transformComponent.worldTransform
            go.removeComponentByType(GenericComponents.HierarchyComponent)
            transformComponent.transform = worldTransform
        self._out.call()

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]
