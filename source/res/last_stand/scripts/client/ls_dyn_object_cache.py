# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/ls_dyn_object_cache.py
import typing
import ResMgr
from dyn_objects_cache import DynObjectsBase
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache

class LSPrefabs(object):
    ALL = ()


class LSEffects(object):
    PHASE_SWITCH = 'lsPhaseSwitch'
    ALL = (PHASE_SWITCH,)


@dependency.replace_none_kwargs(dynamicObjectsCache=IBattleDynamicObjectsCache, battleSession=IBattleSessionProvider)
def getPrefabPath(objID, dynamicObjectsCache=None, battleSession=None):
    return dynamicObjectsCache.getConfig(battleSession.arenaVisitor.getArenaGuiType()).getPrefab(objID)


@dependency.replace_none_kwargs(dynamicObjectsCache=IBattleDynamicObjectsCache, battleSession=IBattleSessionProvider)
def getEffectSection(objID, dynamicObjectsCache=None, battleSession=None):
    return dynamicObjectsCache.getConfig(battleSession.arenaVisitor.getArenaGuiType()).getEffectSection(objID)


class _LSDynObjects(DynObjectsBase):

    def __init__(self):
        super(_LSDynObjects, self).__init__()
        self.__prefabPaths = {}
        self.__effectSections = {}

    def init(self, dataSection):
        if self._initialized:
            return
        for prefabKey in LSPrefabs.ALL:
            self.__prefabPaths[prefabKey] = self.__readPrefab(dataSection, prefabKey)

        for effectKey in LSEffects.ALL:
            self.__effectSections[effectKey] = self.__readEffect(dataSection, effectKey)

        super(_LSDynObjects, self).init(dataSection)

    def destroy(self):
        super(_LSDynObjects, self).clear()
        self.__effectSections.clear()

    def getPrefab(self, key):
        return self.__prefabPaths.get(key, None)

    def getEffectSection(self, key):
        return self.__effectSections.get(key, None)

    @staticmethod
    def __readPrefab(dataSection, key):
        return dataSection[key].readString('prefab')

    @staticmethod
    def __readEffect(dataSection, key):
        return ResMgr.openSection(dataSection[key].readString('effect'))
