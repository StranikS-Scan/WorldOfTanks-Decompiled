# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/components/vehicle_prefabs.py
from __future__ import absolute_import
import logging
import typing
import weakref
import CGF
from events_containers.common.containers import ContainersListener
from events_containers.components.life_cycle import IComponentLifeCycleListenerLogic
from events_handler import eventHandler
from vehicle_systems.model_assembler import loadAppearancePrefab
if typing.TYPE_CHECKING:
    from events_containers.components.life_cycle import ILifeCycleComponent
    from items.vehicles import VehicleDescriptor
    from Vehicle import Vehicle
_logger = logging.getLogger(__name__)

class VehiclePrefabSpawner(ContainersListener, IComponentLifeCycleListenerLogic):
    _DEFAULT_OUTFIT = 'default'

    def __init__(self, vehicle):
        super(VehiclePrefabSpawner, self).__init__()
        self.__vehicle = weakref.proxy(vehicle)
        self.__vehicleID = self.__vehicle.id
        self.__prefabRoot = None
        self.__prefabPath = ''
        return

    def isPrefabRoot(self, gameObject):
        return self.__prefabRoot is not None and self.__prefabRoot.id == gameObject.id

    @eventHandler
    def onComponentDestroyed(self, component):
        self.__prefabPath = ''
        if self.__prefabRoot is not None:
            _logger.debug('[VehiclePrefabSpawner] removeGameObject (onDestroy) for %s', self.__vehicleID)
            CGF.removeGameObject(self.__prefabRoot)
            self.__prefabRoot = None
        self.__vehicle = None
        return

    @eventHandler
    def onComponentParamsCollected(self, params):
        skin = self.__vehicle.appearance.modelsSetParams.skin or self._DEFAULT_OUTFIT
        self.__prefabPath = self._getPrefabPath(self.__vehicle.typeDescriptor, skin)

    def loadAppearancePrefab(self):
        loadAppearancePrefab(self.__prefabPath, self.__vehicle.appearance, self.__onComponentPrefabLoaded)
        _logger.debug('[VehiclePrefabSpawner] loadAppearancePrefab for %s', self.__vehicleID)

    def getPrefabRoot(self):
        return self.__prefabRoot

    def _getPrefabPath(self, typeDescriptor, skin):
        raise NotImplementedError

    def __onComponentPrefabLoaded(self, root):
        if not root.isValid:
            _logger.error('[VehiclePrefabSpawner] failed to load prefab: %s', self.__prefabPath)
            return
        elif self.__vehicle is None:
            _logger.debug('[VehiclePrefabSpawner] removeGameObject (onLoaded) for %s', self.__vehicleID)
            CGF.removeGameObject(root)
            return
        else:
            self.__prefabRoot = root
            return


class VehiclePrefabSetsSpawner(VehiclePrefabSpawner):
    _PREFABS_SET_KEY = ''

    def _getPrefabPath(self, typeDescriptor, skin):
        prefabs = self._getPrefabsSets(typeDescriptor)
        skin = skin if skin in prefabs else self._DEFAULT_OUTFIT
        return prefabs[skin][self._PREFABS_SET_KEY][0]

    def _getPrefabsSets(self, typeDescriptor):
        raise NotImplementedError


class VehicleMechanicPrefabSpawner(VehiclePrefabSetsSpawner):
    _PREFABS_SET_KEY = 'mechanicEffects'

    def _getPrefabsSets(self, typeDescriptor):
        return typeDescriptor.type.prefabs


def createMechanicPrefabSpawner(vehicle, component):
    mechanicPrefabSpawner = VehicleMechanicPrefabSpawner(vehicle)
    component.lifeCycleEvents.lateSubscribe(mechanicPrefabSpawner)
    return mechanicPrefabSpawner
