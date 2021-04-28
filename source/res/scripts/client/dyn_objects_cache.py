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
_ScenariosEffect = namedtuple('_ScenariosEffect', ('path', 'rate', 'offset', 'scaleRatio'))
_DropPlane = namedtuple('_DropPlane', ('model', 'flyAnimation', 'sound'))
_AirDrop = namedtuple('_AirDrop', ('model', 'dropAnimation'))
_LootEffect = namedtuple('_LootEffect', ('path_fwd', 'path'))
_LootModel = namedtuple('_LootModel', ('name', 'border'))
_Loot = namedtuple('_Loot', ('model', 'effect', 'pickupEffect'))
_PointOfInterest = namedtuple('_PointOfInterest', ('modelName', 'color', 'overTerrainHeight'))
_MinesEffects = namedtuple('_MinesEffects', ('plantEffect', 'idleEffect', 'destroyEffect'))
_BerserkerEffects = namedtuple('_BerserkerEffects', ('turretEffect', 'hullEffect', 'transformPath'))
MIN_OVER_TERRAIN_HEIGHT = 0
MIN_UPDATE_INTERVAL = 0
_TerrainCircleSettings = namedtuple('_TerrainCircleSettings', ('modelPath', 'color', 'enableAccurateCollision', 'maxUpdateInterval', 'overTerrainHeight', 'cutOffYDistance'))

def _createScenarioEffect(section, path):
    return _ScenariosEffect(section.readString(path, ''), section.readFloat('rate', ZERO_FLOAT), section.readVector3('offset', (ZERO_FLOAT, ZERO_FLOAT, ZERO_FLOAT)), section.readFloat('scaleRatio', ZERO_FLOAT))


def _addPrecacheCandidate(prerequisites, modelName):
    prerequisites.add(modelName)


def _createDropPlane(section, prerequisites):
    modelName = section.readString('model')
    _addPrecacheCandidate(prerequisites, modelName)
    flyAnimation = section.readString('flyAnimation')
    dropPlane = _DropPlane(modelName, flyAnimation, section.readString('sound'))
    return dropPlane


def _createAirDrop(section, prerequisites):
    modelName = section.readString('model')
    _addPrecacheCandidate(prerequisites, modelName)
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
        _addPrecacheCandidate(prerequisites, modelName)
        effect = loot['effect']
        effectPath = effect.readString('path')
        effectPathFwd = effect.readString('path_fwd')
        pickupEffect = loot['pickupEffect']
        pickUpPath = pickupEffect.readString('path')
        pickUpFwd = pickupEffect.readString('path_fwd')
        loots[typeID] = _Loot(_LootModel(modelName, model.readString('border')), _LootEffect(effectPathFwd, effectPath), _LootEffect(pickUpFwd, pickUpPath))

    return loots


def _createTerrainCircleSettings(section):
    sectionKeys = ('ally', 'enemy')
    result = dict.fromkeys(sectionKeys)
    for sectionKey in sectionKeys:
        subSection = section[sectionKey]
        if subSection is not None:
            result[sectionKey] = _TerrainCircleSettings(subSection.readString('visual'), int(subSection.readString('color'), 0), subSection.readBool('enableAccurateCollision'), max(MIN_UPDATE_INTERVAL, subSection.readFloat('maxUpdateInterval')), max(MIN_OVER_TERRAIN_HEIGHT, subSection.readFloat('overTerrainHeight')), subSection.readFloat('cutOffYDistance', default=-1.0))

    return result


def _createPointOfInterest(section, prerequisites):
    modelName = section.readString('model')
    color = int(section.readString('color'), 0)
    overTerrainHeight = section.readFloat('overTerrainHeight')
    _addPrecacheCandidate(prerequisites, modelName)
    pointOfInterest = _PointOfInterest(modelName, color, overTerrainHeight)
    return pointOfInterest


def _parseEffectSubsection(dataSection, sectionKey):
    if dataSection is not None:
        effectSection = dataSection[sectionKey]
        if effectSection is not None:
            effPathPropName = 'path' if isRendererPipelineDeferred() else 'path_fwd'
            return _createScenarioEffect(effectSection, effPathPropName)
    return


class _SimpleEffect(object):
    _SECTION_NAME = None

    def __init__(self, dataSection):
        super(_SimpleEffect, self).__init__()
        self.effectDescr = _parseEffectSubsection(dataSection[self._SECTION_NAME], 'effect')


class _TeamRelatedEffect(object):
    _ENEMY_SUB_NAME = 'enemy'
    _ALLY_SUB_NAME = 'ally'
    _SECTION_NAME = None

    def __init__(self, dataSection):
        super(_TeamRelatedEffect, self).__init__()
        tpSection = dataSection[self._SECTION_NAME]
        self.ally = _parseEffectSubsection(tpSection[self._ALLY_SUB_NAME], 'effect')
        self.enemy = _parseEffectSubsection(tpSection[self._ENEMY_SUB_NAME], 'effect')


class _BattleRoyaleTrapPointEffect(_TeamRelatedEffect):
    _SECTION_NAME = 'TrapPoint'

    def __init__(self, dataSection):
        super(_BattleRoyaleTrapPointEffect, self).__init__(dataSection)
        tpSection = dataSection[self._SECTION_NAME]
        self.vehicleEffect = _parseEffectSubsection(tpSection[self._ENEMY_SUB_NAME], 'vehicleEffect')


class _BattleRoyaleRepairPointEffect(_TeamRelatedEffect):
    _SECTION_NAME = 'RepairPoint'


class _BattleRoyaleBotDeliveryEffect(_TeamRelatedEffect):
    _SECTION_NAME = 'BotDeliveryEffect'


class _BattleRoyaleBotDeliveryMarkerArea(_TeamRelatedEffect):
    _SECTION_NAME = 'BotDeliveryArea'


class _MinesPlantEffect(_SimpleEffect):
    _SECTION_NAME = 'minesPlantEffect'


class _MinesIdleEffect(_TeamRelatedEffect):
    _SECTION_NAME = 'minesIdleEffect'


class _MinesDestroyEffect(_SimpleEffect):
    _SECTION_NAME = 'minesDestroyEffect'


class _VehicleUpgradeEffect(_SimpleEffect):
    _SECTION_NAME = 'VehicleUpgrade'


class _KamikazeActivatedEffect(_SimpleEffect):
    _SECTION_NAME = 'KamikazeActivated'


class _BerserkerHullEffect(_SimpleEffect):
    _SECTION_NAME = 'berserkerHullEffect'


class _BerserkerTurretEffect(_SimpleEffect):
    _SECTION_NAME = 'berserkerTurretEffect'


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


class _CommonDynObjects(DynObjectsBase):

    def __init__(self):
        super(_CommonDynObjects, self).__init__()
        self.__inspiringEffect = None
        self.__healPointEffect = None
        self.__resourcesCache = None
        return

    def init(self, dataSection):
        if not self._initialized:
            self.__inspiringEffect = _createTerrainCircleSettings(dataSection['InspireAreaVisual'])
            self.__healPointEffect = _createTerrainCircleSettings(dataSection[self._healPointKey])
            super(_CommonDynObjects, self).init(dataSection)

    def getInspiringEffect(self):
        return self.__inspiringEffect

    def getHealPointEffect(self):
        return self.__healPointEffect

    @property
    def _healPointKey(self):
        pass

    def _onResourcesLoaded(self, resourceRefs):
        self.__resourcesCache = resourceRefs

    def clear(self):
        pass

    def destroy(self):
        pass


class _BattleRoyaleDynObjects(_CommonDynObjects):

    def __init__(self):
        super(_BattleRoyaleDynObjects, self).__init__()
        self.__vehicleUpgradeEffect = None
        self.__kamikazeActivatedEffect = None
        self.__trapPoint = None
        self.__repairPoint = None
        self.__botDeliveryEffect = None
        self.__botDeliveryMarker = None
        self.__dropPlane = None
        self.__airDrop = None
        self.__loots = {}
        self.__minesEffects = None
        self.__berserkerEffects = None
        return

    def init(self, dataSection):
        if not self._initialized:
            self.__vehicleUpgradeEffect = _VehicleUpgradeEffect(dataSection)
            self.__kamikazeActivatedEffect = _KamikazeActivatedEffect(dataSection)
            self.__trapPoint = _BattleRoyaleTrapPointEffect(dataSection)
            self.__repairPoint = _BattleRoyaleRepairPointEffect(dataSection)
            self.__botDeliveryEffect = _BattleRoyaleBotDeliveryEffect(dataSection)
            self.__botDeliveryMarker = _BattleRoyaleBotDeliveryMarkerArea(dataSection)
            self.__minesEffects = _MinesEffects(plantEffect=_MinesPlantEffect(dataSection), idleEffect=_MinesIdleEffect(dataSection), destroyEffect=_MinesDestroyEffect(dataSection))
            self.__berserkerEffects = _BerserkerEffects(turretEffect=_BerserkerTurretEffect(dataSection), hullEffect=_BerserkerHullEffect(dataSection), transformPath=dataSection.readString('berserkerTransformPath'))
            prerequisites = set()
            self.__dropPlane = _createDropPlane(dataSection['dropPlane'], prerequisites)
            self.__airDrop = _createAirDrop(dataSection['airDrop'], prerequisites)
            self.__loots = _createLoots(dataSection, dataSection['lootTypes'], prerequisites)
            BigWorld.loadResourceListBG(list(prerequisites), makeCallbackWeak(self._onResourcesLoaded))
            super(_BattleRoyaleDynObjects, self).init(dataSection)

    def getVehicleUpgradeEffect(self):
        return self.__vehicleUpgradeEffect

    def getKamikazeActivatedEffect(self):
        return self.__kamikazeActivatedEffect

    def getTrapPointEffect(self):
        return self.__trapPoint

    def getRepairPointEffect(self):
        return self.__repairPoint

    def getBotDeliveryEffect(self):
        return self.__botDeliveryEffect

    def getBotDeliveryMarker(self):
        return self.__botDeliveryMarker

    def getDropPlane(self):
        return self.__dropPlane

    def getAirDrop(self):
        return self.__airDrop

    def getLoots(self):
        return self.__loots

    def getMinesEffect(self):
        return self.__minesEffects

    def getBerserkerEffects(self):
        return self.__berserkerEffects

    def clear(self):
        pass

    def destroy(self):
        self.__vehicleUpgradeEffect = None
        self.__kamikazeActivatedEffect = None
        self.__trapPoint = None
        self.__repairPoint = None
        self.__resourcesCache = None
        self.__minesEffects = None
        return

    @property
    def _healPointKey(self):
        pass


class _WeekendBrawlDynObjects(_CommonDynObjects):

    def __init__(self):
        super(_WeekendBrawlDynObjects, self).__init__()
        self.__pointsOfInterest = None
        return

    def init(self, dataSection):
        prerequisites = set()
        section = dataSection['pointOfInterest']
        if section is not None:
            self.__pointsOfInterest = _createPointOfInterest(section, prerequisites)
            BigWorld.loadResourceListBG(list(prerequisites), makeCallbackWeak(self._onResourcesLoaded))
        else:
            _logger.error('Failed to read pointOfInterest config section')
        super(_WeekendBrawlDynObjects, self).init(dataSection)
        return

    def destroy(self):
        self.__pointsOfInterest = None
        super(_WeekendBrawlDynObjects, self).destroy()
        return

    def getPointsOfInterest(self):
        return self.__pointsOfInterest


_CONF_STORAGES = {ARENA_GUI_TYPE.BATTLE_ROYALE: _BattleRoyaleDynObjects,
 ARENA_GUI_TYPE.EPIC_BATTLE: _CommonDynObjects,
 ARENA_GUI_TYPE.EPIC_TRAINING: _CommonDynObjects,
 ARENA_GUI_TYPE.WEEKEND_BRAWL: _WeekendBrawlDynObjects}

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
