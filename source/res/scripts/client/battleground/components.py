# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/battleground/components.py
import BigWorld
import Math
import AnimationSequence
import CGF
import math_utils
from cgf_script.component_meta_class import CGFComponent, ComponentProperty, CGFMetaTypes
from cgf_obsolete_script.py_component import Component
from battleground.iself_assembler import ISelfAssembler
from cgf_obsolete_script.script_game_object import ScriptGameObject, ComponentDescriptorTyped
from arena_component_system.client_arena_component_system import ClientArenaComponent
from helpers import EffectsList, isPlayerAvatar
from PlayerEvents import g_playerEvents

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

    def bindToCompound(self, compound):
        if compound is None:
            return
        else:
            if self.__sequenceAnimator is not None and not self.__sequenceAnimator.isBound():
                self.__sequenceAnimator.bindTo(AnimationSequence.CompoundWrapperContainer(compound))
                self.__startUnchecked()
            return

    def unbind(self):
        if self.__sequenceAnimator is not None and self.__sequenceAnimator.isBound():
            self.__sequenceAnimator.unbind()
        return

    @property
    def sequenceAnimator(self):
        return self.__sequenceAnimator

    def bindToModel(self, model, spaceId):
        if model is None:
            return
        else:
            if self.__sequenceAnimator is not None and not self.__sequenceAnimator.isBound():
                self.__sequenceAnimator.bindTo(AnimationSequence.ModelWrapperContainer(model, spaceId))
            return

    def bindAsTerrainEffect(self, position, spaceId, scale=None, loopCount=1):
        if self.createTerrainEffect(position, scale, loopCount):
            effectHandler = CGF.GameObject(spaceId)
            effectHandler.createComponent(_SequenceAnimatorTimer, self.__sequenceAnimator, effectHandler)
            effectHandler.activate()
            effectHandler.transferOwnershipToWorld()
            self.__sequenceAnimator = None
        return

    def createTerrainEffect(self, position, scale=None, loopCount=1, rotation=(0, 0, 0)):
        if self.__sequenceAnimator is not None and not self.__sequenceAnimator.isBound():
            scale = scale if scale is not None else Math.Vector3(1, 1, 1)
            matrix = math_utils.createSRTMatrix(scale, rotation, position)
            self.__sequenceAnimator.bindToWorld(matrix)
            self.__sequenceAnimator.loopCount = loopCount
            self.__startUnchecked()
            return True
        else:
            return False

    def start(self):
        if self.__sequenceAnimator is not None:
            self.__startUnchecked()
        return

    def stop(self):
        if self.__sequenceAnimator is not None:
            self.__stopUnchecked()
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

    def __startUnchecked(self):
        self.__sequenceAnimator.setEnabled(True)
        self.__sequenceAnimator.start()

    def __stopUnchecked(self):
        self.__sequenceAnimator.stop()
        self.__sequenceAnimator.setEnabled(False)


class _SequenceAnimatorTimer(CGFComponent):
    parent = ComponentProperty(type=CGFMetaTypes.LINK, value=CGF.GameObject)

    def __init__(self, sequenceAnimator, parent):
        super(_SequenceAnimatorTimer, self).__init__()
        self.__sequenceAnimator = sequenceAnimator
        self.parent = parent

    def tick(self):
        if not self.__sequenceAnimator.isPlaying():
            self.__sequenceAnimator.stop()
            self.__sequenceAnimator.setEnabled(False)
            self.__sequenceAnimator = None
            CGF.removeGameObject(self.parent)
        return

    def destroy(self):
        if self.__sequenceAnimator is not None:
            self.__sequenceAnimator.stop()
            self.__sequenceAnimator.setEnabled(False)
        self.__sequenceAnimator = None
        self.parent = None
        return


class TerrainAreaComponent(Component):

    def __init__(self, area):
        self.area = area


class EffectPlayer(Component):

    def __init__(self, effectsListSectionRoot, effectsListName):
        timeline = EffectsList.effectsFromSection(effectsListSectionRoot[effectsListName])
        self.effectsListTimeLine = timeline
        self.__effectID = None
        return

    def play(self, pickupPosition):
        if self.__effectID:
            BigWorld.player().terrainEffects.stop(self.__effectID)
        velocityDir = Math.Vector3(0, 1, 0)
        self.__effectID = BigWorld.player().terrainEffects.addNew(pickupPosition, self.effectsListTimeLine.effectsList, self.effectsListTimeLine.keyPoints, None, start=pickupPosition + velocityDir, end=pickupPosition - velocityDir)
        return

    def stop(self):
        if self.__effectID:
            BigWorld.player().terrainEffects.stop(self.__effectID)
            self.__effectID = None
        return


class TerrainAreaGameObject(ScriptGameObject, ISelfAssembler):
    model = ComponentDescriptorTyped(ModelComponent)
    terrainArea = ComponentDescriptorTyped(TerrainAreaComponent)

    def assembleOnLoad(self):
        if self.terrainArea is not None:
            self.model.attach(self.terrainArea.area)
        return

    def setPosition(self, position):
        if self.model is not None:
            self.model.setPosition(position)
        return

    def setMotor(self, matrix):
        if self.model is not None:
            self.model.setMotor(matrix)
        return


class AvatarRelatedComponent(ClientArenaComponent):

    def activate(self):
        super(AvatarRelatedComponent, self).activate()
        if isPlayerAvatar():
            self._initialize()
        else:
            g_playerEvents.onAvatarBecomePlayer += self._initialize

    def deactivate(self):
        super(AvatarRelatedComponent, self).deactivate()
        g_playerEvents.onAvatarBecomePlayer -= self._initialize

    def _initialize(self):
        g_playerEvents.onAvatarBecomePlayer -= self._initialize


class SequenceObject(ScriptGameObject):
    sequence = ComponentDescriptorTyped(SequenceComponent)

    def __init__(self):
        super(SequenceObject, self).__init__(BigWorld.player().spaceID)

    def enable(self, enabled):
        if self.sequence is not None:
            if enabled:
                self.sequence.enable()
            else:
                self.sequence.disable()
        return

    def bindAndStart(self, *args):
        if self.sequence is not None:
            self.sequence.createTerrainEffect(args[0], loopCount=-1)
        return

    def start(self):
        if self.sequence is not None:
            self.sequence.start()
        return

    def stop(self):
        if self.sequence is not None:
            self.sequence.stop()
        return

    def unbind(self):
        if self.sequence is not None:
            self.sequence.unbind()
        return


class SmartSequenceObject(SequenceObject):

    def bindAndStart(self, *args):
        if self.sequence is not None:
            self.sequence.bindAsTerrainEffect(args[0], args[1])
        return


class CompoundSequenceObject(SequenceObject):

    def bindAndStart(self, *args):
        if self.sequence is not None:
            self.sequence.bindToCompound(args[0])
        return


class EffectPlayerObject(ScriptGameObject):
    effectList = ComponentDescriptorTyped(EffectPlayer)

    def __init__(self):
        super(EffectPlayerObject, self).__init__(BigWorld.player().spaceID)

    def start(self, position):
        if self.effectList is not None:
            self.effectList.play(position)
        return

    def stop(self):
        if self.effectList is not None:
            self.effectList.stop()
        return
