# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/components/vehicle_prefabs.py
from __future__ import absolute_import
import logging
import typing
import weakref
from functools import partial
import CGF
from ids_generators import SequenceIDGenerator
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
        self.__idGen = SequenceIDGenerator()
        self.__prefabRoot = None
        self.__prefabPath = ''
        return

    @eventHandler
    def onComponentParamsCollected(self, params):
        skin = self.__vehicle.appearance.modelsSetParams.skin or self._DEFAULT_OUTFIT
        self.__prefabPath = self._getPrefabPath(self.__vehicle.typeDescriptor, skin)

    @eventHandler
    def onComponentAppearanceReady(self, component):
        postLoadedCallback = partial(self.__onComponentPrefabLoaded, self.__idGen.nextSequenceID)
        loadAppearancePrefab(self.__prefabPath, self.__vehicle.appearance, postLoadedCallback, False)
        self.__logMessage(_logger.debug, 'loadAppearancePrefab')

    @eventHandler
    def onComponentAppearanceReset(self, component):
        self.__removePrefabRoot('onComponentAppearanceReset')
        _ = self.__idGen.nextSequenceID

    @eventHandler
    def onComponentDestroyed(self, component):
        self.__removePrefabRoot('onComponentDestroyed')
        self.__vehicle, self.__prefabPath = (None, '')
        self.__idGen.clear()
        return None

    def _getPrefabPath(self, typeDescriptor, skin):
        raise NotImplementedError

    def __onComponentPrefabLoaded(self, sequenceID, root, _, queue):
        if not root:
            self.__logMessage(_logger.error, 'failed to load prefab')
            return False
        elif self.__vehicle is None or sequenceID != self.__idGen.currSequenceID:
            self.__logMessage(_logger.debug, 'removeGameObject (onLoaded) {}'.format(sequenceID))
            return False
        else:
            self.__prefabRoot = queue.gameObject(root)
            return True

    def __logMessage(self, logMethod, message):
        logMethod('[VehiclePrefabSpawner][%s][%s][%s] %s', self.__vehicleID, self.__idGen.currSequenceID, self.__prefabPath, message)

    def __removePrefabRoot(self, source):
        if self.__prefabRoot is not None:
            self.__logMessage(_logger.debug, 'removeGameObject ({})'.format(source))
            CGF.removeGameObject(self.__prefabRoot)
            self.__prefabRoot = None
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
