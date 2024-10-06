# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/battleground/loot_object.py
import logging
import BigWorld
import CGF
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from cgf_script.bonus_caps_rules import bonusCapsManager
from helpers import dependency
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(dynamicObjectsCache=IBattleDynamicObjectsCache, battleSession=IBattleSessionProvider)
def loadLootById(typeID, dynamicObjectsCache=None, battleSession=None):
    descr = dynamicObjectsCache.getConfig(battleSession.arenaVisitor.getArenaGuiType()).getLoots().get(typeID, None)
    if descr is None:
        _logger.error('[Loot] Could not find loot types for %s.', typeID)
    return descr


@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, CGF.DomainOption.DomainClient)
class SteelHunterDynamicObjectsCachingManager(CGF.ComponentManager):
    __dynamicObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)

    def __init__(self):
        super(SteelHunterDynamicObjectsCachingManager, self).__init__()
        self.__cachedPrefabs = set()
        self.__cachedConfig = None
        return

    def activate(self):
        config = self.__getConfig()
        loots = config.getLoots().values()
        for loot in loots:
            self.__cachePrefabs(loot)

    def deactivate(self):
        if self.__cachedPrefabs:
            CGF.clearGameObjectsCache(list(self.__cachedPrefabs))

    def __cachePrefabs(self, lootDescr):
        if lootDescr is not None:
            for path in ('prefab', 'prefabPickup'):
                prefabPath = getattr(lootDescr, path, None)
                if prefabPath:
                    self.__cachedPrefabs.add(prefabPath)

        if self.__cachedPrefabs:
            CGF.cacheGameObjects(list(self.__cachedPrefabs), False)
        return

    def __getConfig(self):
        if self.__cachedConfig is None:
            self.__cachedConfig = self.__dynamicObjectsCache.getConfig(BigWorld.player().arenaGuiType)
        return self.__cachedConfig
