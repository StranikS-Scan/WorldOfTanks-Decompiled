# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/battleground/loot_object.py
import logging
import BigWorld
import Math
import AnimationSequence
import Svarog
import math_utils
from battleground.iself_assembler import ISelfAssembler
from gui.shared.utils.graphics import isRendererPipelineDeferred
from helpers import dependency
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from skeletons.gui.battle_session import IBattleSessionProvider
from svarog_script.py_component import Component
from svarog_script.script_game_object import ScriptGameObject, ComponentDescriptorTyped
from battleground.component_loading import loadComponentSystem, Loader
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(dynamicObjectsCache=IBattleDynamicObjectsCache, battleSession=IBattleSessionProvider)
def loadLootById(radius, callback, typeID, dynamicObjectsCache=None, battleSession=None):
    loot = dynamicObjectsCache.getConfig(battleSession.arenaVisitor.getArenaGuiType()).getLoots().get(typeID, None)
    if loot is not None:
        return _loadLoot(typeID, radius, callback, loot)
    else:
        _logger.error('[Loot] Cannot find loot types for %s.', typeID)
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


class ModelComponent(Component):

    @property
    def position(self):
        return self.__baseModel.position

    @property
    def compoundModel(self):
        return self.__baseModel

    def __init__(self, compoundModel, **kwargs):
        offset = kwargs.get('offset', 0.0)
        self.__offset = (0.0, offset, 0.0)
        self.__baseModel = compoundModel
        self.__isInWorld = False

    def activate(self):
        if self.compoundModel is not None and not self.__isInWorld:
            BigWorld.player().addModel(self.compoundModel)
            self.__isInWorld = True
        return

    def deactivate(self):
        player = BigWorld.player()
        if self.__isInWorld and self.compoundModel is not None and player is not None:
            player.delModel(self.compoundModel)
        return

    def setPosition(self, position):
        if self.compoundModel is not None:
            self.compoundModel.position = position + self.__offset
        return

    def attach(self, attachment, offset=None):
        if offset is not None:
            offsetMatrix = Math.Matrix()
            offsetMatrix.setTranslate(offset)
            self.__baseModel.root.attach(attachment, offsetMatrix)
        else:
            self.__baseModel.root.attach(attachment)
        return

    def detach(self, attachment):
        self.__baseModel.root.detach(attachment)

    def setMotor(self, matrix):
        if self.compoundModel is not None:
            if getattr(self.compoundModel, 'addMotor', None) is not None:
                self.compoundModel.addMotor(BigWorld.Servo(matrix))
            else:
                self.compoundModel.matrix = matrix
        return


class SequenceComponent(Component):

    def __init__(self, sequenceAnimator):
        self.__sequenceAnimator = sequenceAnimator

    def bindToModel(self, model):
        if model is None:
            return
        else:
            if self.__sequenceAnimator is not None and not self.__sequenceAnimator.isBound():
                self.__sequenceAnimator.bindTo(AnimationSequence.CompoundWrapperContainer(model))
            return

    def bindAsTerrainEffect(self, position, spaceId, scale=None, loopCount=1):
        if self.createTerrainEffect(position, scale, loopCount):
            effectHandler = Svarog.GameObject(spaceId)
            timerComponent = _SequenceAnimatorTimer(self.__sequenceAnimator, lambda : Svarog.removeGameObject(spaceId, effectHandler))
            effectHandler.addComponent(timerComponent)
            Svarog.addGameObject(BigWorld.player().spaceID, effectHandler)
            effectHandler.activate()
            self.__sequenceAnimator = None
        return

    def createTerrainEffect(self, position, scale=None, loopCount=1):
        if self.__sequenceAnimator is not None and not self.__sequenceAnimator.isBound():
            scale = scale if scale is not None else Math.Vector3(1, 1, 1)
            matrix = math_utils.createSRTMatrix(scale, (0, 0, 0), position)
            self.__sequenceAnimator.bindToWorld(matrix)
            self.__sequenceAnimator.loopCount = loopCount
            self.__sequenceAnimator.start()
            return True
        else:
            return False

    def start(self):
        if self.__sequenceAnimator is not None:
            self.__sequenceAnimator.start()
        return

    def stop(self):
        if self.__sequenceAnimator is not None:
            self.__sequenceAnimator.stop()
        return

    def enable(self):
        if self.__sequenceAnimator is not None:
            self.__sequenceAnimator.setEnabled(True)
        return

    def disable(self):
        if self.__sequenceAnimator is not None:
            self.__sequenceAnimator.setEnabled(False)
        return

    def setTrigger(self, name):
        if self.__sequenceAnimator is not None:
            self.__sequenceAnimator.setTrigger(name)
        return

    def deactivate(self):
        self.stop()

    def destroy(self):
        self.__sequenceAnimator = None
        return


class _SequenceAnimatorTimer(Component):

    def __init__(self, sequenceAnimator, doneCallback):
        self.__sequenceAnimator = sequenceAnimator
        self.__doneCallback = doneCallback

    def tick(self):
        if self.__doneCallback is not None and not self.__sequenceAnimator.isPlaying():
            self.__doneCallback()
            self.__doneCallback = None
        return

    def destroy(self):
        self.__sequenceAnimator = None
        self.__doneCallback = None
        return


class TerrainAreaComponent(Component):

    def __init__(self, area):
        self.area = area


class ILootObject(ScriptGameObject):
    model = None

    def processPickup(self, entityID):
        pass


class LootObject(ILootObject, ISelfAssembler):
    model = ComponentDescriptorTyped(ModelComponent)
    markingSmoke = ComponentDescriptorTyped(SequenceComponent)
    pickupEffect = ComponentDescriptorTyped(SequenceComponent)
    terrainArea = ComponentDescriptorTyped(TerrainAreaComponent)

    def __init__(self, radius, lootTypeID):
        super(LootObject, self).__init__(BigWorld.player().spaceID)
        self.radius = radius
        self.lootTypeID = lootTypeID
        self.__rootModel = None
        return

    def assembleOnLoad(self):
        if self.terrainArea is not None:
            self.model.attach(self.terrainArea.area)
        return

    def activate(self):
        super(LootObject, self).activate()
        if self.markingSmoke is not None:
            self.markingSmoke.bindToModel(self.model.compoundModel)
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

    def setPosition(self, position):
        if self.model is not None:
            self.model.setPosition(position)
        return

    def setMotor(self, matrix):
        if self.model is not None:
            self.model.setMotor(matrix)
        return
