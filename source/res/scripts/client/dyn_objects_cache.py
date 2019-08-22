# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/dyn_objects_cache.py
import logging
from collections import namedtuple
import BigWorld
import resource_helper
from constants import ARENA_GUI_TYPE
from gui.shared.utils.graphics import isRendererPipelineDeferred
from items.components.component_constants import ZERO_FLOAT
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from vehicle_systems.stricted_loading import makeCallbackWeak
_CONFIG_PATH = 'scripts/dynamic_objects.xml'
_logger = logging.getLogger(__name__)
_ScenariosEffect = namedtuple('_ScenariosEffect', ('path', 'rate', 'offset'))
_DropPlane = namedtuple('_DropPlane', ('model', 'flyAnimation', 'sound'))
_AirDrop = namedtuple('_AirDrop', ('model', 'dropAnimation'))
_LootEffect = namedtuple('_LootEffect', ('path_fwd', 'path'))
_LootModel = namedtuple('_LootModel', ('name', 'border'))
_Loot = namedtuple('_Loot', ('model', 'effect', 'pickupEffect'))
MIN_OVER_TERRAIN_HEIGHT = 0
MIN_UPDATE_INTERVAL = 0
_TerrainCircleSettings = namedtuple('_TerrainCircleSettings', ('modelPath', 'color', 'enableAccurateCollision', 'maxUpdateInterval', 'overTerrainHeight'))

def _createScenarioEffect(section, path):
    return _ScenariosEffect(section.readString(path, ''), section.readFloat('rate', ZERO_FLOAT), section.readVector3('offset', (ZERO_FLOAT, ZERO_FLOAT, ZERO_FLOAT)))


def _createDropPlane(section, prerequisites):
    modelName = section.readString('model')
    prerequisites.add(modelName)
    flyAnimation = section.readString('flyAnimation')
    dropPlane = _DropPlane(modelName, flyAnimation, section.readString('sound'))
    return dropPlane


def _createAirDrop(section, prerequisites):
    modelName = section.readString('model')
    prerequisites.add(modelName)
    dropAnimation = section.readString('dropAnimation')
    airDrop = _AirDrop(modelName, dropAnimation)
    return airDrop


def _createLoots(dataSection, typeSection, prerequisites):
    loots = {}
    for lootType in typeSection.items():
        typeName = lootType[1]['name'].asString.strip()
        typeID = lootType[1]['id'].asInt
        loot = dataSection[typeName]
        model = loot['model']
        modelName = model.readString('name')
        prerequisites.add(modelName)
        effect = loot['effect']
        effectPath = effect.readString('path')
        effectPathFwd = effect.readString('path_fwd')
        pickupEffect = loot['pickupEffect']
        pickUpPath = pickupEffect.readString('path')
        pickUpFwd = pickupEffect.readString('path_fwd')
        loots[typeID] = _Loot(_LootModel(modelName, model.readString('border')), _LootEffect(effectPathFwd, effectPath), _LootEffect(pickUpFwd, pickUpPath))

    return loots


def _createTerrainCircleSettings(section):
    return _TerrainCircleSettings(section.readString('visual'), int(section.readString('color'), 0), section.readBool('enableAccurateCollision'), max(MIN_UPDATE_INTERVAL, section.readFloat('maxUpdateInterval')), max(MIN_OVER_TERRAIN_HEIGHT, section.readFloat('overTerrainHeight')))


class _BattleRoyaleTrapPointEffect(object):
    _ENEMY_SUB_NAME = 'enemy'
    _ALLY_SUB_NAME = 'ally'

    def __init__(self, dataSection):
        super(_BattleRoyaleTrapPointEffect, self).__init__()
        tpSection = dataSection['TrapPoint']
        self.ally, self.allyVehicle = self.__parceSubSection(tpSection, self._ALLY_SUB_NAME)
        self.enemy, self.enemyVehicle = self.__parceSubSection(tpSection, self._ENEMY_SUB_NAME)

    def __parceSubSection(self, section, subName):
        subSection = section[subName]
        effect = None
        vehicleEffect = None
        effPathPropName = 'path' if isRendererPipelineDeferred() else 'path_fwd'
        effectSection = subSection['effect']
        if effectSection is not None:
            effect = _createScenarioEffect(effectSection, effPathPropName)
        vehicleSection = subSection['vehicleEffect']
        if vehicleSection is not None:
            vehicleEffect = _createScenarioEffect(vehicleSection, 'path')
        return (effect, vehicleEffect)


class DynObjectsBase(object):

    def __init__(self):
        super(DynObjectsBase, self).__init__()
        self._initialized = False

    def init(self, dataSection):
        self._initialized = True

    def clear(self):
        pass

    def destroy(self):
        pass


class _CommonForBattleRoyaleAndEpicBattleDynObjects(DynObjectsBase):

    def __init__(self):
        super(_CommonForBattleRoyaleAndEpicBattleDynObjects, self).__init__()
        self.__inspiringEffect = None
        self.__healPointEffect = None
        return

    def init(self, dataSection):
        if not self._initialized:
            self.__inspiringEffect = _createTerrainCircleSettings(dataSection['InspireAreaVisual'])
            self.__healPointEffect = _createTerrainCircleSettings(dataSection['HealPointVisual'])
            super(_CommonForBattleRoyaleAndEpicBattleDynObjects, self).init(dataSection)

    def getInspiringEffect(self):
        return self.__inspiringEffect

    def getHealPointEffect(self):
        return self.__healPointEffect

    def clear(self):
        pass

    def destroy(self):
        pass


class _BattleRoyaleDynObjects(_CommonForBattleRoyaleAndEpicBattleDynObjects):

    def __init__(self):
        super(_BattleRoyaleDynObjects, self).__init__()
        self.__vehicleUpgradeEffect = None
        self.__trapPoint = None
        self.__dropPlane = None
        self.__airDrop = None
        self.__loots = {}
        self.__resourcesCache = None
        import battleroyale.trap_point
        return

    def init(self, dataSection):
        if not self._initialized:
            self.__vehicleUpgradeEffect = _createScenarioEffect(dataSection['VehicleUpgrade']['effect'], 'path')
            self.__trapPoint = _BattleRoyaleTrapPointEffect(dataSection)
            prerequisites = set()
            self.__dropPlane = _createDropPlane(dataSection['dropPlane'], prerequisites)
            self.__airDrop = _createAirDrop(dataSection['airDrop'], prerequisites)
            self.__loots = _createLoots(dataSection, dataSection['lootTypes'], prerequisites)
            BigWorld.loadResourceListBG(list(prerequisites), makeCallbackWeak(self.__onResourcesLoaded))
            super(_BattleRoyaleDynObjects, self).init(dataSection)

    def getVehicleUpgradeEffect(self):
        return self.__vehicleUpgradeEffect

    def getTrapPointEffect(self):
        return self.__trapPoint

    def getDropPlane(self):
        return self.__dropPlane

    def getAirDrop(self):
        return self.__airDrop

    def getLoots(self):
        return self.__loots

    def clear(self):
        pass

    def destroy(self):
        self.__vehicleUpgradeEffect = None
        self.__trapPoint = None
        self.__resourcesCache = None
        return

    def __onResourcesLoaded(self, resourceRefs):
        self.__resourcesCache = resourceRefs


_CONF_STORAGES = {ARENA_GUI_TYPE.BATTLE_ROYALE: _BattleRoyaleDynObjects,
 ARENA_GUI_TYPE.EPIC_BATTLE: _CommonForBattleRoyaleAndEpicBattleDynObjects,
 ARENA_GUI_TYPE.EPIC_TRAINING: _CommonForBattleRoyaleAndEpicBattleDynObjects}

class BattleDynamicObjectsCache(IBattleDynamicObjectsCache):

    def __init__(self):
        super(BattleDynamicObjectsCache, self).__init__()
        self.__configStorage = {}

    def getConfig(self, arenaType):
        return self.__configStorage.get(arenaType)

    def load(self, arenaType):
        if arenaType not in self.__configStorage:
            if arenaType in _CONF_STORAGES:
                confStorage = _CONF_STORAGES[arenaType]()
                self.__configStorage[arenaType] = confStorage
                _, section = resource_helper.getRoot(_CONFIG_PATH)
                confStorage.init(section)
                resource_helper.purgeResource(_CONFIG_PATH)

    def unload(self, arenaType):
        for cV in self.__configStorage.itervalues():
            cV.clear()

    def destroy(self):
        if self.__configStorage is not None:
            for cV in self.__configStorage.itervalues():
                cV.destroy()

            self.__configStorage = None
        return
