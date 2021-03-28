# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/battleground/loot_object.py
import logging
import BigWorld
import Math
import AnimationSequence
from helpers import dependency
from battleground.component_loading import loadComponentSystem, Loader, CompositeLoaderMixin
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


def __getSequenceResourceMapping(desc, effectName, spaceID):
    effectDesc = getattr(desc, effectName, None)
    if effectDesc is not None:
        if isRendererPipelineDeferred():
            effectPath = effectDesc.path
        else:
            effectPath = effectDesc.path_fwd
        return {'sequence': Loader(AnimationSequence.Loader(effectPath, spaceID))}
    else:
        return {}


def _loadLoot(typeID, radius, callback, desc):
    loot = LootObject(radius, typeID)
    loaders = {}
    loot.prepareCompositeLoader(callback)
    spaceID = BigWorld.player().spaceID
    if hasattr(desc, 'model'):
        modelName = desc.model.name
        offset = getattr(desc.model, 'overTerrainHeight', 0.0)
        if modelName is None:
            _logger.warning('Model for loot %s not set', typeID)
        else:
            modelAssembler = BigWorld.CompoundAssembler('model', spaceID)
            modelAssembler.addRootPart(modelName, 'root')
            borderName = getattr(desc.model, 'border', None)
            if borderName is not None:
                borderMatrix = Math.Matrix()
                modelAssembler.addPart(borderName, 'root', 'border', borderMatrix)
            loaders['model'] = Loader(modelAssembler, offset=offset)
    loadComponentSystem(loot.markingSmoke, loot.appendPiece, __getSequenceResourceMapping(desc, 'effect', spaceID))
    loadComponentSystem(loot.pickupEffect, loot.appendPiece, __getSequenceResourceMapping(desc, 'pickupEffect', spaceID))
    loadComponentSystem(loot, loot.appendPiece, loaders)
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
        self.pickupEffect.enable(True)
        self.pickupEffect.bindAndStart(self.model.position, self._nativeSystem.spaceID)

    def startSmoke(self):
        self.markingSmoke.start()

    def stopSmoke(self):
        self.markingSmoke.stop()

    def _piecesNum(self):
        return len(self.__children) + 1
