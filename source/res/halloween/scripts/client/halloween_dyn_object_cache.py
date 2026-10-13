# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween_dyn_object_cache.py
from __future__ import absolute_import
import typing
import ResMgr
from dyn_objects_cache import DynObjectsBase
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from collections import namedtuple

class HWPrefabs(object):
    SOULS_COLLECTOR = 'hwSoulsCollector'
    ALL = (SOULS_COLLECTOR,)


class HWEffects(object):
    PHASE_SWITCH = 'hwPhaseSwitch'
    ALL = (PHASE_SWITCH,)


class HWModels(object):
    DEATHZONE_BORDER_RECT = 'hwDeathZoneBorderRect'
    DEATHZONE_BORDER_CIRCLE = 'hwDeathZoneBorderCircle'
    ALL = (DEATHZONE_BORDER_RECT, DEATHZONE_BORDER_CIRCLE)


class HWHexapodTerrainEffects(object):
    SECTION = 'hwHexapodTerrainEffects'
    DEFAULT_GROUP = 'defaultGroup'
    Effect = namedtuple('Effect', ('effect', 'rate', 'duration', 'sound'))
    DEFAULT_DURATION = 3.0
    DEFAULT_RATE = 1.0
    DEFAULT_SOUND = ''


@dependency.replace_none_kwargs(dynamicObjectsCache=IBattleDynamicObjectsCache, battleSession=IBattleSessionProvider)
def getPrefabPath(objID, dynamicObjectsCache=None, battleSession=None):
    return dynamicObjectsCache.getConfig(battleSession.arenaVisitor.getArenaGuiType()).getPrefab(objID)


@dependency.replace_none_kwargs(dynamicObjectsCache=IBattleDynamicObjectsCache, battleSession=IBattleSessionProvider)
def getEffectSection(objID, dynamicObjectsCache=None, battleSession=None):
    return dynamicObjectsCache.getConfig(battleSession.arenaVisitor.getArenaGuiType()).getEffectSection(objID)


@dependency.replace_none_kwargs(dynamicObjectsCache=IBattleDynamicObjectsCache, battleSession=IBattleSessionProvider)
def getModel(objID, dynamicObjectsCache=None, battleSession=None):
    return dynamicObjectsCache.getConfig(battleSession.arenaVisitor.getArenaGuiType()).getModel(objID)


@dependency.replace_none_kwargs(dynamicObjectsCache=IBattleDynamicObjectsCache, battleSession=IBattleSessionProvider)
def getHexapodTerrainEffects(group=HWHexapodTerrainEffects.DEFAULT_GROUP, dynamicObjectsCache=None, battleSession=None):
    return dynamicObjectsCache.getConfig(battleSession.arenaVisitor.getArenaGuiType()).getHexapodTerrainEffects(group)


class _HalloweenDynObjects(DynObjectsBase):

    def __init__(self):
        super(_HalloweenDynObjects, self).__init__()
        self.__prefabPaths = {}
        self.__effectSections = {}
        self.__models = {}
        self.__hexapodTerrainEffects = {}

    def init(self, dataSection):
        if self._initialized:
            return
        for prefabKey in HWPrefabs.ALL:
            self.__prefabPaths[prefabKey] = self.__readPrefab(dataSection, prefabKey)

        for effectKey in HWEffects.ALL:
            self.__effectSections[effectKey] = self.__readEffect(dataSection, effectKey)

        for model in HWModels.ALL:
            self.__models[model] = self.__readModel(dataSection, model)

        self.__hexapodTerrainEffects = self.__readHexapodTerrainEffects(dataSection[HWHexapodTerrainEffects.SECTION])
        super(_HalloweenDynObjects, self).init(dataSection)

    def destroy(self):
        super(_HalloweenDynObjects, self).clear()
        self.__effectSections.clear()

    def getPrefab(self, key):
        return self.__prefabPaths.get(key, None)

    def getEffectSection(self, key):
        return self.__effectSections.get(key, None)

    def getModel(self, key):
        return self.__models.get(key)

    def getHexapodTerrainEffects(self, group=None):
        return self.__hexapodTerrainEffects.get(group, self.__hexapodTerrainEffects[HWHexapodTerrainEffects.DEFAULT_GROUP])

    @staticmethod
    def __readPrefab(dataSection, key):
        return dataSection[key].readString('prefab')

    @staticmethod
    def __readEffect(dataSection, key):
        return ResMgr.openSection(dataSection[key].readString('effect'))

    @staticmethod
    def __readModel(dataSection, key):
        return dataSection[key].readString('model')

    def __readHexapodTerrainEffects(self, dataSection):
        return {group:self.__readHexapodTerrainGroup(section) for group, section in dataSection.items()}

    def __readHexapodTerrainGroup(self, dataSection):
        return {material:self.__readHexapodTerrainEffect(section) for material, section in dataSection.items()}

    def __readHexapodTerrainEffect(self, dataSection):
        return HWHexapodTerrainEffects.Effect(dataSection.readString('effect'), dataSection.readFloat('rate', HWHexapodTerrainEffects.DEFAULT_RATE), dataSection.readFloat('duration', HWHexapodTerrainEffects.DEFAULT_DURATION), dataSection.readString('sound', HWHexapodTerrainEffects.DEFAULT_SOUND))
