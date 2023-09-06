# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/battleground/loot_object.py
import logging
import weakref
from collections import defaultdict
import BigWorld
import Math
import AnimationSequence
import CGF
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from cgf_script.bonus_caps_rules import bonusCapsManager
from helpers import dependency
from battleground.component_loading import loadComponentSystem, Loader, CompositeLoaderMixin, loadResourceMapping
from battleground.components import TerrainAreaGameObject, CompoundSequenceObject, SmartSequenceObject
from gui.shared.utils.graphics import isRendererPipelineDeferred
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(dynamicObjectsCache=IBattleDynamicObjectsCache, battleSession=IBattleSessionProvider)
def loadLootById(radius, callback, typeID, dynamicObjectsCache=None, battleSession=None):
    lootDscr = dynamicObjectsCache.getConfig(battleSession.arenaVisitor.getArenaGuiType()).getLoots().get(typeID, None)
    if lootDscr is not None:
        return _loadLoot(typeID, radius, callback, lootDscr)
    else:
        _logger.error('[Loot] Could not find loot types for %s.', typeID)
        return


def _getSequenceResourceMapping(desc, effectName, spaceID, includePaths=False):
    effectDesc = getattr(desc, effectName, None)
    if effectDesc is not None:
        if isRendererPipelineDeferred():
            effectPath = effectDesc.path
        else:
            effectPath = effectDesc.path_fwd
        res = {'sequence': Loader(AnimationSequence.Loader(effectPath, spaceID))}
        if includePaths:
            res['path'] = effectPath
        return res
    else:
        return {}


def _loadLootForeground(loot, spaceID, desc):
    loaders = {}
    if hasattr(desc, 'model'):
        modelName = desc.model.name
        offset = getattr(desc.model, 'overTerrainHeight', 0.0)
        if modelName is not None:
            modelAssembler = BigWorld.CompoundAssembler('model', spaceID)
            modelAssembler.addRootPart(modelName, 'root')
            borderName = getattr(desc.model, 'border', None)
            if borderName is not None:
                borderMatrix = Math.Matrix()
                modelAssembler.addPart(borderName, 'root', 'border', borderMatrix)
            loaders['model'] = Loader(modelAssembler, offset=offset)
    loadComponentSystem(loot.markingSmoke, loot.appendPiece, _getSequenceResourceMapping(desc, 'effect', spaceID), forceForegroundLoad=True)
    loadComponentSystem(loot.pickupEffect, loot.appendPiece, _getSequenceResourceMapping(desc, 'pickupEffect', spaceID), forceForegroundLoad=True)
    loadComponentSystem(loot, loot.appendPiece, loaders, forceForegroundLoad=True)
    _logger.info('[Loot] Loading of loot type %d done', loot.lootTypeID)
    return


def _loadLoot(typeID, radius, callback, desc):
    loot = LootObject(radius, typeID)
    loot.prepareCompositeLoader(callback)
    spaceID = BigWorld.player().spaceID
    cachingManager = CGF.getManager(spaceID, SteelHunterDynamicObjectsCachingManager)
    if cachingManager is not None and cachingManager.hasCachedLoot(typeID):
        _loadLootForeground(loot, spaceID, desc)
    else:
        cachingManager.cacheForegroundLootLoading(loot)
    return loot


class ILootObject(object):

    def processPickup(self, entityID):
        pass


class LootObject(TerrainAreaGameObject, ILootObject, CompositeLoaderMixin):

    def __init__(self, radius, lootTypeID):
        super(LootObject, self).__init__(BigWorld.player().spaceID)
        self.radius = radius
        self.lootTypeID = lootTypeID
        self.markingSmoke = CompoundSequenceObject()
        self.pickupEffect = SmartSequenceObject()
        self.__children = (self.markingSmoke, self.pickupEffect)
        self.__collected = False

    def activate(self):
        super(LootObject, self).activate()
        for child in self.__children:
            child.activate()

        if not self.__collected:
            self.markingSmoke.bindAndStart(self.model.compoundModel)
        self.pickupEffect.enable(False)

    def deactivate(self):
        super(LootObject, self).deactivate()
        self.markingSmoke.stop()
        self.markingSmoke.unbind()
        for child in self.__children:
            child.deactivate()

    def processPickup(self, entityID):
        self.__collected = True
        self.stopSmoke()
        if self.model is not None:
            self.pickupEffect.enable(True)
            self.pickupEffect.bindAndStart(self.model.position, self._nativeSystem.spaceID)
        return

    def startSmoke(self):
        self.markingSmoke.start()

    def stopSmoke(self):
        self.markingSmoke.stop()

    def _piecesNum(self):
        return len(self.__children) + 1


@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, CGF.DomainOption.DomainClient)
class SteelHunterDynamicObjectsCachingManager(CGF.ComponentManager):
    __dynamicObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)

    def __init__(self):
        super(SteelHunterDynamicObjectsCachingManager, self).__init__()
        self.__lootCache = {}
        self.__cachingQueue = defaultdict(lambda : [])
        self.__cachedConfig = None
        return

    def hasCachedLoot(self, lootType):
        return lootType in self.__lootCache

    def cacheForegroundLootLoading(self, loot):
        _logger.info('[Loot] Issuing caching of loot type %d creation', loot.lootTypeID)
        self.__cachingQueue[loot.lootTypeID].append(weakref.ref(loot))

    def activate(self):
        self.__lootCache = {}
        config = self.__getConfig()
        loots = config.getLoots().iteritems()
        for lootType, loot in loots:
            self.__orderLootCache(lootType, loot)

    def __orderLootCache(self, lootType, lootDescr):
        if lootDescr is not None:
            spaceID = self.spaceID
            if hasattr(lootDescr, 'model'):
                modelName = lootDescr.model.name
                offset = getattr(lootDescr.model, 'overTerrainHeight', 0.0)
                loaders = {}
                if modelName is not None:
                    modelAssembler = BigWorld.CompoundAssembler('model', spaceID)
                    modelAssembler.addRootPart(modelName, 'root')
                    borderName = getattr(lootDescr.model, 'border', None)
                    if borderName is not None:
                        borderMatrix = Math.Matrix()
                        modelAssembler.addPart(borderName, 'root', 'border', borderMatrix)
                    loaders = {'model': Loader(modelAssembler, offset=offset)}
                mapping = _getSequenceResourceMapping(lootDescr, 'effect', spaceID, True)
                effectsPaths = []
                if mapping:
                    loaders['effect'] = mapping['sequence']
                    effectsPaths.append(mapping['path'])
                mapping = _getSequenceResourceMapping(lootDescr, 'pickupEffect', spaceID, True)
                if mapping:
                    loaders['pickupEffect'] = mapping['sequence']
                    effectsPaths.append(mapping['path'])
                loadResourceMapping(loaders, self.__cacheResourceList, lootType, effectsPaths)
        return

    def __cacheResourceList(self, lootType, effectsPaths, resourceList):
        cachedResources = []
        for _, resource in resourceList.items():
            cachedResources.append(resource)

        self.__lootCache[lootType] = cachedResources
        for effectPath in effectsPaths:
            effect = resourceList[effectPath]
            if effect:
                effect.halt()

        _logger.info('[Loot] Loot %d resources has been cached', lootType)
        toForegroundLoad = self.__cachingQueue[lootType]
        if not toForegroundLoad:
            return
        _logger.info('[Loot] Performing cached loot creation of type %d, amount %d', lootType, len(toForegroundLoad))
        config = self.__dynamicObjectsCache.getConfig(BigWorld.player().arenaGuiType)
        lootDesc = config.getLoots()[lootType]
        for loot in toForegroundLoad:
            reference = loot()
            if reference:
                _loadLootForeground(reference, self.spaceID, lootDesc)

        del self.__cachingQueue[lootType]

    def __getConfig(self):
        if self.__cachedConfig is None:
            self.__cachedConfig = self.__dynamicObjectsCache.getConfig(BigWorld.player().arenaGuiType)
        return self.__cachedConfig
