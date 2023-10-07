# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/dyn_objects_cache.py
import logging
from collections import namedtuple
import typing
import BigWorld
import CGF
import resource_helper
from constants import ARENA_GUI_TYPE
from gui.shared.system_factory import registerDynObjCache, collectDynObjCache
from gui.shared.utils.graphics import isRendererPipelineDeferred
from items.components.component_constants import ZERO_FLOAT
from shared_utils import first
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
_MinesEffects = namedtuple('_MinesEffects', ('plantEffect', 'idleEffect', 'destroyEffect', 'placeMinesEffect', 'blowUpEffectName', 'activationEffect'))
_BerserkerEffects = namedtuple('_BerserkerEffects', ('turretEffect', 'hullEffect', 'transformPath'))
MIN_OVER_TERRAIN_HEIGHT = 0
MIN_UPDATE_INTERVAL = 0
_TerrainCircleSettings = namedtuple('_TerrainCircleSettings', ('modelPath', 'color', 'enableAccurateCollision', 'enableWaterCollision', 'maxUpdateInterval', 'overTerrainHeight', 'cutOffDistance', 'cutOffAngle', 'minHeight', 'maxHeight'))

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

    def readFloatOrNone(subSection, key):
        return subSection.readFloat(key, default=None) if subSection.has_key(key) else None

    for sectionKey in sectionKeys:
        subSection = section[sectionKey]
        if subSection is not None:
            result[sectionKey] = _TerrainCircleSettings(subSection.readString('visual'), int(subSection.readString('color'), 0), subSection.readBool('enableAccurateCollision'), subSection.readBool('enableWaterCollision', default=False), max(MIN_UPDATE_INTERVAL, subSection.readFloat('maxUpdateInterval')), max(MIN_OVER_TERRAIN_HEIGHT, subSection.readFloat('overTerrainHeight')), readFloatOrNone(subSection, 'cutOffDistance'), readFloatOrNone(subSection, 'cutOffAngle'), readFloatOrNone(subSection, 'minHeight'), readFloatOrNone(subSection, 'maxHeight'))

    return result


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


class _BattleRoyaleBotClingDeliveryEffect(_TeamRelatedEffect):
    _SECTION_NAME = 'BotClingDeliveryEffect'


class _BattleRoyaleBotDeliveryMarkerArea(_TeamRelatedEffect):
    _SECTION_NAME = 'BotDeliveryArea'


class _MinesPlantEffect(_SimpleEffect):
    _SECTION_NAME = 'minesPlantEffect'


class _MinesIdleEffect(_TeamRelatedEffect):
    _SECTION_NAME = 'minesIdleEffect'


class _EpicMinesIdleEffect(_TeamRelatedEffect):
    _SECTION_NAME = 'epicMinesIdleEffect'


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

    def getInspiringEffect(self):
        return {}

    def getHealPointEffect(self):
        return {}


class _CommonForBattleRoyaleAndEpicBattleDynObjects(DynObjectsBase):

    def __init__(self):
        super(_CommonForBattleRoyaleAndEpicBattleDynObjects, self).__init__()
        self.__inspiringEffect = None
        self.__healPointEffect = None
        return

    def init(self, dataSection):
        if not self._initialized:
            self.__inspiringEffect = _createTerrainCircleSettings(dataSection['InspireAreaVisual'])
            self.__healPointEffect = _createTerrainCircleSettings(dataSection[self._healPointKey])
            super(_CommonForBattleRoyaleAndEpicBattleDynObjects, self).init(dataSection)

    def getInspiringEffect(self):
        return self.__inspiringEffect

    def getHealPointEffect(self):
        return self.__healPointEffect

    @property
    def _healPointKey(self):
        pass

    def clear(self):
        pass

    def destroy(self):
        pass


class _StrongholdDynObjects(DynObjectsBase):

    def __init__(self):
        super(_StrongholdDynObjects, self).__init__()
        self.__inspiringEffect = None
        return

    def init(self, dataSection):
        if not self._initialized:
            self.__inspiringEffect = _createTerrainCircleSettings(dataSection['InspireAreaVisual'])
            super(_StrongholdDynObjects, self).init(dataSection)

    def getInspiringEffect(self):
        return self.__inspiringEffect


class _EpicBattleDynObjects(_CommonForBattleRoyaleAndEpicBattleDynObjects):

    def __init__(self):
        super(_EpicBattleDynObjects, self).__init__()
        self.__minesEffects = None
        return

    def init(self, dataSection):
        if not self._initialized:
            self.__minesEffects = _MinesEffects(plantEffect=_MinesPlantEffect(dataSection), idleEffect=_EpicMinesIdleEffect(dataSection), destroyEffect=_MinesDestroyEffect(dataSection), placeMinesEffect='epicMinesDecalEffect', blowUpEffectName='epicMinesBlowUpEffect', activationEffect='epicMinesActivationDecalEffect')
            super(_EpicBattleDynObjects, self).init(dataSection)

    def getMinesEffect(self):
        return self.__minesEffects


class _BattleRoyaleDynObjects(_CommonForBattleRoyaleAndEpicBattleDynObjects):
    _LOOT_TYPES = 'lootTypes'

    def __init__(self):
        super(_BattleRoyaleDynObjects, self).__init__()
        self.__vehicleUpgradeEffect = None
        self.__kamikazeActivatedEffect = None
        self.__trapPoint = None
        self.__repairPoint = None
        self.__botDeliveryEffect = None
        self.__botClingDeliveryEffect = None
        self.__botDeliveryMarker = None
        self.__dropPlane = None
        self.__airDrop = None
        self.__loots = {}
        self.__minesEffects = None
        self.__berserkerEffects = None
        self.__resourcesCache = None
        return

    def init(self, dataSection):
        if not self._initialized:
            self.__vehicleUpgradeEffect = _VehicleUpgradeEffect(dataSection)
            self.__kamikazeActivatedEffect = _KamikazeActivatedEffect(dataSection)
            self.__trapPoint = _BattleRoyaleTrapPointEffect(dataSection)
            self.__repairPoint = _BattleRoyaleRepairPointEffect(dataSection)
            self.__botDeliveryEffect = _BattleRoyaleBotDeliveryEffect(dataSection)
            self.__botClingDeliveryEffect = _BattleRoyaleBotClingDeliveryEffect(dataSection)
            self.__botDeliveryMarker = _BattleRoyaleBotDeliveryMarkerArea(dataSection)
            self.__minesEffects = _MinesEffects(plantEffect=_MinesPlantEffect(dataSection), idleEffect=_MinesIdleEffect(dataSection), destroyEffect=_MinesDestroyEffect(dataSection), placeMinesEffect='minesDecalEffect', blowUpEffectName='minesBlowUpEffect', activationEffect=None)
            self.__berserkerEffects = _BerserkerEffects(turretEffect=_BerserkerTurretEffect(dataSection), hullEffect=_BerserkerHullEffect(dataSection), transformPath=dataSection.readString('berserkerTransformPath'))
            prerequisites = set()
            self.__dropPlane = _createDropPlane(dataSection['dropPlane'], prerequisites)
            self.__airDrop = _createAirDrop(dataSection['airDrop'], prerequisites)
            self.__loots = _createLoots(dataSection, dataSection[self._LOOT_TYPES], prerequisites)
            BigWorld.loadResourceListBG(list(prerequisites), makeCallbackWeak(self.__onResourcesLoaded))
            super(_BattleRoyaleDynObjects, self).init(dataSection)
        return

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

    def getBotClingDeliveryEffect(self):
        return self.__botClingDeliveryEffect

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

    def __onResourcesLoaded(self, resourceRefs):
        self.__resourcesCache = resourceRefs


class _Comp7DynObjects(DynObjectsBase):
    _AOE_HEAL_KEY = 'aoeHeal'
    __ALL_KEYS = (_AOE_HEAL_KEY,)
    _SPAWNPOINT_VISUAL_PATH_KEY = 'spawnPointVisualPath'

    def __init__(self):
        super(_Comp7DynObjects, self).__init__()
        self.__prefabPaths = {}
        self.__cachedPrefabs = set()
        self.__spawnPointConfig = None
        self.__pointsOfInterestConfig = None
        return

    def init(self, dataSection):
        if self._initialized:
            return
        for prefabKey in self.__ALL_KEYS:
            self.__prefabPaths[prefabKey] = self.__readPrefab(dataSection, prefabKey)

        self.__spawnPointConfig = _SpawnPointsConfig.createFromXML(dataSection['spawnPointsConfig'])
        self.__pointsOfInterestConfig = _PointsOfInterestConfig.createFromXML(dataSection['pointOfInterest'])
        self.__cachedPrefabs.update(set(self.__prefabPaths.values()))
        self.__cachedPrefabs.update(set(self.__pointsOfInterestConfig.getPrefabs()))
        CGF.cacheGameObjects(list(self.__cachedPrefabs), False)
        super(_Comp7DynObjects, self).init(dataSection)

    def clear(self):
        if self.__cachedPrefabs:
            CGF.clearGameObjectsCache(list(self.__cachedPrefabs))
            self.__cachedPrefabs.clear()
        self.__spawnPointConfig = None
        self.__pointsOfInterestConfig = None
        self._initialized = False
        return

    def destroy(self):
        self.clear()
        self.__prefabPaths.clear()

    def getAoeHealPrefab(self):
        return self.__prefabPaths[self._AOE_HEAL_KEY]

    def getSpawnPointsConfig(self):
        return self.__spawnPointConfig

    def getPointOfInterestConfig(self):
        return self.__pointsOfInterestConfig

    @staticmethod
    def __readPrefab(dataSection, key):
        return dataSection[key].readString('prefab')


class _SpawnPointsConfig(object):

    def __init__(self, size, visualsPath, colors, overTerrainHeight):
        self.__size = size
        self.__visualsPath = visualsPath
        self.__colors = colors
        self.__overTerrainHeight = overTerrainHeight

    @property
    def size(self):
        return self.__size

    @property
    def overTerrainHeight(self):
        return self.__overTerrainHeight

    def getColor(self, isMyOwn, isConfirmed):
        ownageKey = 'own' if isMyOwn else 'ally'
        confirmationKey = 'confirmed' if isConfirmed else 'notConfirmed'
        return self.__colors[ownageKey][confirmationKey]

    def getVisualPath(self, positionNumber):
        positionName = 'position{}'.format(positionNumber)
        return self.__visualsPath.get(positionName)

    @classmethod
    def createFromXML(cls, section):
        return cls(size=section.readVector2('areaSize'), visualsPath=cls.__readVisualsPath(section['visualsPath']), colors=cls.__readColors(section['colors']), overTerrainHeight=section.readFloat('overTerrainHeight'))

    @staticmethod
    def __readVisualsPath(section):
        return {key:section.readString(key) for key in section.keys()}

    @staticmethod
    def __readColors(section):
        colors = {}
        renderKey = 'deferred' if isRendererPipelineDeferred() else 'forward'
        for ownageType, colorsConfig in section[renderKey].items():
            colors[ownageType] = {'confirmed': int(colorsConfig.readString('confirmed'), 16),
             'notConfirmed': int(colorsConfig.readString('notConfirmed'), 16)}

        return colors


class _PointsOfInterestConfig(object):

    def __init__(self, prefabs):
        self.__prefabs = prefabs

    def getPointOfInterestPrefab(self, radius):
        for (minRange, maxRange), path in self.__prefabs.iteritems():
            if minRange <= radius < maxRange:
                return path

        _logger.error('Failed to get prefab for PointOfInterest (radius=%d)', radius)
        return first(self.__prefabs.itervalues())

    def getPrefabs(self):
        return self.__prefabs.values()

    @classmethod
    def createFromXML(cls, section):
        points = {}
        for _, prefab in section.items():
            radiusRange = prefab.readVector2('radiusRange')
            path = prefab.readString('path')
            points[radiusRange.x, radiusRange.y] = path

        return cls(points)


registerDynObjCache(ARENA_GUI_TYPE.SORTIE_2, _StrongholdDynObjects)
registerDynObjCache(ARENA_GUI_TYPE.FORT_BATTLE_2, _StrongholdDynObjects)
registerDynObjCache(ARENA_GUI_TYPE.BATTLE_ROYALE, _BattleRoyaleDynObjects)
registerDynObjCache(ARENA_GUI_TYPE.EPIC_BATTLE, _EpicBattleDynObjects)
registerDynObjCache(ARENA_GUI_TYPE.EPIC_TRAINING, _EpicBattleDynObjects)
registerDynObjCache(ARENA_GUI_TYPE.EVENT_BATTLES, _EpicBattleDynObjects)
registerDynObjCache(ARENA_GUI_TYPE.COMP7, _Comp7DynObjects)

class BattleDynamicObjectsCache(IBattleDynamicObjectsCache):

    def __init__(self):
        super(BattleDynamicObjectsCache, self).__init__()
        self.__configStorage = {}

    def getConfig(self, arenaType):
        return self.__configStorage.get(arenaType)

    def load(self, arenaType):
        _logger.info('Trying to load resources for arenaType = %s', arenaType)
        _, section = resource_helper.getRoot(_CONFIG_PATH)
        if arenaType in self.__configStorage:
            self.__configStorage[arenaType].init(section)
        else:
            cache = collectDynObjCache(arenaType)
            if cache:
                confStorage = cache()
                self.__configStorage[arenaType] = confStorage
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
