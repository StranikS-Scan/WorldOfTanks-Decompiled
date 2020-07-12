# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/battleground/loot_object.py
import logging
import BigWorld
import Math
import AnimationSequence
from helpers import dependency
from battleground.component_loading import loadComponentSystem, Loader
from battleground.components import SequenceComponent, TerrainAreaGameObject
from gui.shared.utils.graphics import isRendererPipelineDeferred
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from skeletons.gui.battle_session import IBattleSessionProvider
from svarog_script.script_game_object import ComponentDescriptorTyped
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(dynamicObjectsCache=IBattleDynamicObjectsCache, battleSession=IBattleSessionProvider)
def loadLootById(radius, callback, typeID, dynamicObjectsCache=None, battleSession=None):
    lootDscr = dynamicObjectsCache.getConfig(battleSession.arenaVisitor.getArenaGuiType()).getLoots().get(typeID, None)
    if lootDscr is not None:
        return _loadLoot(typeID, radius, callback, lootDscr)
    else:
        _logger.error('[Loot] Could not find loot types for %s.', typeID)
        return


def _loadLoot(typeID, radius, callback, desc):
    loot = LootObject(radius, typeID)
    loaders = {}
    if hasattr(desc, 'model'):
        modelName = desc.model.name
        offset = getattr(desc.model, 'overTerrainHeight', 0.0)
        if modelName is None:
            _logger.warning('Model for loot %s not set', typeID)
        else:
            modelAssembler = BigWorld.CompoundAssembler('model', BigWorld.player().spaceID)
            modelAssembler.addRootPart(modelName, 'root')
            borderName = getattr(desc.model, 'border', None)
            if borderName is not None:
                borderMatrix = Math.Matrix()
                modelAssembler.addPart(borderName, 'root', 'border', borderMatrix)
            loaders['model'] = Loader(modelAssembler, offset=offset)
    if hasattr(desc, 'effect'):
        if isRendererPipelineDeferred():
            effectPath = desc.effect.path
        else:
            effectPath = desc.effect.path_fwd
        loaders['markingSmoke'] = Loader(AnimationSequence.Loader(effectPath, BigWorld.player().spaceID))
    if hasattr(desc, 'pickupEffect'):
        if isRendererPipelineDeferred():
            effectPath = desc.pickupEffect.path
        else:
            effectPath = desc.pickupEffect.path_fwd
        loaders['pickupEffect'] = Loader(AnimationSequence.Loader(effectPath, BigWorld.player().spaceID))
    loadComponentSystem(loot, callback, loaders)
    return loot


class ILootObject(object):

    def processPickup(self, entityID):
        pass


class LootObject(TerrainAreaGameObject, ILootObject):
    markingSmoke = ComponentDescriptorTyped(SequenceComponent)
    pickupEffect = ComponentDescriptorTyped(SequenceComponent)

    def __init__(self, radius, lootTypeID):
        super(LootObject, self).__init__(BigWorld.player().spaceID)
        self.radius = radius
        self.lootTypeID = lootTypeID

    def activate(self):
        super(LootObject, self).activate()
        if self.markingSmoke is not None:
            self.markingSmoke.bindToCompound(self.model.compoundModel)
            self.markingSmoke.start()
        if self.pickupEffect is not None:
            self.pickupEffect.disable()
        return

    def processPickup(self, entityID):
        if self.pickupEffect is not None:
            self.pickupEffect.enable()
            self.pickupEffect.bindAsTerrainEffect(self.model.position, self._nativeSystem.worldID)
        return

    def startSmoke(self):
        if self.markingSmoke is not None:
            self.markingSmoke.start()
        return

    def stopSmoke(self):
        if self.markingSmoke is not None:
            self.markingSmoke.stop()
        return
