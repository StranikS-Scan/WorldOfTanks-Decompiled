# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBVehicleEffect.py
import enum
import Math
import BigWorld
import AnimationSequence
from items import vehicles
from vehicle_systems.stricted_loading import makeCallbackWeak
from helpers import newFakeModel
from helpers.EffectsList import EffectsListPlayer
from gui.shared.utils.graphics import isRendererPipelineDeferred
from Event import EventsSubscriber
import logging
import SoundGroups
from Sound import Sound3DComponent
import GenericComponents
import CGF
_logger = logging.getLogger(__name__)

class SequenceEffect(object):
    __slots__ = ('__active', '__animator', '__bindNode', '__spaceID', '__model', '__loadingTaskID', '__owner', '__config', '__sequencePatch', '__unapplyCbkID', '__isPlaying', '__timeToFinish', '__soundGameObject', '__soundStart', '__soundEnd', '__weakref__')

    def __init__(self, entity, data):
        self.__active = False
        self.__animator = None
        self.__bindNode = None
        self.__spaceID = None
        self.__model = None
        self.__loadingTaskID = None
        self.__owner = entity
        self.__config = data
        self.__unapplyCbkID = None
        self.__isPlaying = False
        self.__timeToFinish = 0
        self.__soundGameObject = None
        self.__soundStart = ''
        self.__soundEnd = ''
        if self.__config['path'] and self.__config['path_fwd']:
            self.__sequencePatch = self.__config['path'] if isRendererPipelineDeferred() else self.__config['path_fwd']
        else:
            self.__sequencePatch = self.__config['path']
        return

    def apply(self, startTime):
        if self.__config['duration'] > 0:
            finishTime = startTime + self.__config['duration']
            self.__timeToFinish = finishTime - BigWorld.serverTime()
            if self.__timeToFinish <= 0:
                return
        if self.__isPlaying:
            return
        self.__active = True
        self.__soundStart = self.__config['soundStart']
        self._applyVisualEffects()

    def unapply(self):
        self._unapplyVisualEffects()
        if self.__unapplyCbkID is not None:
            BigWorld.cancelCallback(self.__unapplyCbkID)
            self.__unapplyCbkID = None
        self.__active = False
        self.__timeToFinish = 0
        return

    def destroy(self):
        self.__owner = None
        self.__config = None
        self.__soundGameObject = None
        self.__model = None
        self.__animator = None
        self.__bindNode = None
        return

    def _applyVisualEffects(self):
        if self.__isPlaying:
            return
        self._cancelLoadingTask()
        self.__spaceID = BigWorld.player().spaceID
        loader = AnimationSequence.Loader(self.__sequencePatch, self.__spaceID)
        self.__loadingTaskID = BigWorld.loadResourceListBG((loader,), makeCallbackWeak(self._onLoaded))

    def _unapplyVisualEffects(self):
        if not self.__isPlaying:
            return
        self._cancelLoadingTask()
        self._detachModel()

    def _onLoaded(self, resourceRefs):
        self.__loadingTaskID = None
        if self.__sequencePatch not in resourceRefs.failedIDs:
            self.__animator = resourceRefs[self.__sequencePatch]
            self.__animator.loopCount = self.__config['loopCount']
        if self.__active and self.__owner.model and self.__animator is not None:
            self._attachModel()
        return

    def _cancelLoadingTask(self):
        if self.__loadingTaskID is None:
            return
        else:
            BigWorld.stopLoadResourceListBGTask(self.__loadingTaskID)
            self.__loadingTaskID = None
            return

    def _attachModel(self):
        self.__model = newFakeModel()
        canStart = False
        if self.__config['bindNode'] == 'ground':
            self.__model.position = Math.Vector3(self.__owner.position)
            BigWorld.player().addModel(self.__model)
            canStart = True
        elif self.__config['bindNode'] == 'detached':
            BigWorld.player().addModel(self.__model)
            rotationMatrix = Math.WGTranslationOnlyMP()
            rotationMatrix.source = self.__owner.matrix
            self.__model.addMotor(BigWorld.Servo(rotationMatrix))
            canStart = True
        else:
            nodeName = self.__config['bindNode']
            if nodeName == 'HP_gunFire':
                multiGun = self.__owner.typeDescriptor.turret.multiGun
                gunIndex = self.__owner.prevGunIndex
                isDualGun = self.__owner.typeDescriptor.isDualgunVehicle
                nodeName = multiGun[gunIndex].gunFire if isDualGun and multiGun is not None else 'HP_gunFire'
            self.__bindNode = self.__owner.model.node(nodeName)
            if self.__bindNode is not None:
                self.__bindNode.attach(self.__model)
                canStart = True
        if canStart:
            self.__animator.bindTo(AnimationSequence.ModelWrapperContainer(self.__model, self.__spaceID))
            self.__animator.start()
            self.__checkAndPlayStartSound()
            self.__isPlaying = True
            if self.__timeToFinish > 0:
                self.__unapplyCbkID = BigWorld.callback(self.__timeToFinish, self.unapply)
        return

    def _detachModel(self):
        self.__destroy3DSoundOnGameObject()
        if self.__animator is not None and self.__active:
            self.__animator.stop()
            self.__animator = None
            self.__isPlaying = False
        if self.__bindNode is not None and not self.__bindNode.isDangling:
            self.__bindNode.detach(self.__model)
        self.__model = None
        self.__bindNode = None
        self.__spaceID = None
        return

    def __checkAndPlayStartSound(self):
        if not self.__soundStart:
            return
        if self.__config['bindOnGameObject']:
            self.__play3DSoundOnGameObject(self.__soundStart)
        else:
            SoundGroups.g_instance.playSoundPos(self.__soundStart, self.__model.position)

    def __play3DSoundOnGameObject(self, eventName):
        if self.__soundGameObject is None:
            self.__soundGameObject = CGF.GameObject(self.__owner.appearance.spaceID)
        else:
            self.__soundGameObject.removeComponentByType(Sound3DComponent)
            self.__soundGameObject.removeComponentByType(GenericComponents.TransformComponent)
            self.__soundGameObject.removeComponentByType(GenericComponents.HierarchyComponent)
        go = self.__owner.entityGameObject
        self.__soundGameObject.createComponent(GenericComponents.TransformComponent, Math.Vector3(0, 0, 0))
        self.__soundGameObject.createComponent(GenericComponents.HierarchyComponent, go)
        self.__soundGameObject.createComponent(Sound3DComponent, eventName, eventName, True)
        return

    def __destroy3DSoundOnGameObject(self):
        if self.__soundGameObject is not None:
            self.__soundGameObject.removeComponentByType(Sound3DComponent)
            self.__soundGameObject.removeComponentByType(GenericComponents.TransformComponent)
            self.__soundGameObject.removeComponentByType(GenericComponents.HierarchyComponent)
            CGF.removeGameObject(self.__soundGameObject)
        self.__soundGameObject = None
        self.__soundStart = ''
        return


class Effect(object):
    MAX_APPLY_ATTEMPTS = 10
    APPLY_ATTEMPT_DELAY = 0.1
    __slots__ = ('__playerEffect', '__applyAttempts', '__owner', '__config', '__duration', '__isPlaying', '__soundStart', '__soundEnd')

    def __init__(self, owner, config, soundStart, soundEnd):
        self.__applyAttempts = 0
        self.__owner = owner
        self.__config = config
        self.__playerEffect = EffectsListPlayer(self.__config.effectsList, self.__config.keyPoints, debugParent=self)
        self.__soundStart = soundStart
        self.__soundEnd = soundEnd
        times = [ k.time for k in self.__config.keyPoints if k.name == 'effectEnd' ]
        self.__duration = times[0] / 1000 if times else 0
        self.__isPlaying = False

    def apply(self, startTime):
        if self.__duration > 0 and BigWorld.serverTime() > startTime + self.__duration:
            return
        if self.__isPlaying:
            return
        self.__playerEffect.stop()
        if self.__owner.appearance:
            self.__playerEffect.play(self.__owner.appearance.compoundModel)
            if self.__duration > 0:
                if self.__soundStart:
                    SoundGroups.g_instance.playSoundPos(self.__soundStart, self.__owner.appearance.compoundModel.position)
                BigWorld.callback(self.__duration, self.unapply)
            self.__isPlaying = True
        elif self.__applyAttempts >= Effect.MAX_APPLY_ATTEMPTS:
            self.__applyAttempts = 0
            _logger.error('Could not apply buff %s to vehicle: %s. Missing Appearance object', self.__playerEffect, self.__owner)
        else:
            BigWorld.callback(Effect.APPLY_ATTEMPT_DELAY, self.apply)
            self.__applyAttempts += 1
            _logger.debug('Setting up callback for applying buff %s to vehicle: %s. Missing Appearance object', self.__playerEffect, self.__owner)

    def unapply(self):
        if self.__playerEffect is not None:
            self.__playerEffect.stop()
            if self.__soundEnd:
                SoundGroups.g_instance.playSoundPos(self.__soundEnd, self.__owner.appearance.compoundModel.position)
        self.__isPlaying = False
        return

    def destroy(self):
        self.__owner = None
        self.__config = None
        self.__playerEffect = None
        return


class HBVehicleEffect(BigWorld.DynamicScriptComponent):

    class OwnerType(enum.IntEnum):
        SELF = 0
        TEAM_MATE = 1
        ENEMY = 2

    def __init__(self):
        super(HBVehicleEffect, self).__init__()
        self.__sequences = None
        self.__effects = None
        self._waitAppearanceReady = False
        self._es = EventsSubscriber()
        self._es.subscribeToEvent(self.entity.onAppearanceReady, self._onAppearanceReady)
        self._es.subscribeToEvent(BigWorld.player().onVehicleEnterWorld, self.__onVehicleEnterWorld)
        self._activate(self.startTime)
        return

    def set_eqId(self, prev):
        if self.eqId > 0:
            self._activate(self.startTime)

    def onDestroy(self):
        if self._es is not None:
            self._es.unsubscribeFromAllEvents()
            self._es = None
        self.__stopAllEffects()
        self.__destroyAllEffects()
        return

    def onLeaveWorld(self):
        self.onDestroy()

    def _activate(self, startTime):
        if self.eqId <= 0:
            return
        if self.ownerType < 0:
            return
        if not self.entity.isStarted:
            return
        if self._waitAppearanceReady:
            return
        self.__initSequncesData()
        self.__initEffectsData()
        self.__startSequences(startTime)
        self.__startEffects(startTime)

    def _getEffectData(self):
        equipment = vehicles.g_cache.equipments()[self.eqId]
        return equipment.effects

    def _onAppearanceReady(self):
        pass

    def __onVehicleEnterWorld(self, v):
        if not self._waitAppearanceReady:
            self._activate(self.startTime)

    def __stopAllEffects(self):
        self.__stopEffects(self.__sequences)
        if self.__effects is not None:
            for _effects in self.__effects:
                if _effects is not None:
                    _effects.unapply()

        return

    def __destroyAllEffects(self):
        self.__destroyEffects(self.__sequences)
        if self.__effects is not None:
            for _effects in self.__effects:
                if _effects is not None:
                    _effects.destroy()

        self.__sequences = None
        self.__effects = None
        return

    def __startSequences(self, startTime):
        sequences = self.__sequences[self.ownerType]
        if sequences:
            for sequence in sequences:
                sequence.apply(startTime)

    def __startEffects(self, startTime):
        if self.__effects[self.ownerType] is not None:
            self.__effects[self.ownerType].apply(startTime)
        return

    def __stopEffects(self, effectsList):
        if effectsList is not None:
            for _effects in effectsList:
                if _effects is not None:
                    for effect in _effects:
                        effect.unapply()

        return

    def __destroyEffects(self, effectsList):
        if effectsList is not None:
            for _effects in effectsList:
                if _effects is not None:
                    for effect in _effects:
                        effect.destroy()

        return

    def __initSequncesData(self):
        if self.__sequences is None:
            self.__sequences = [self.__getSequence(self.OwnerType.SELF), self.__getSequence(self.OwnerType.TEAM_MATE), self.__getSequence(self.OwnerType.ENEMY)]
        return

    def __initEffectsData(self):
        if self.__effects is None:
            self.__effects = [self.__getEffect(self.OwnerType.SELF), self.__getEffect(self.OwnerType.TEAM_MATE), self.__getEffect(self.OwnerType.ENEMY)]
        return

    def __getSequence(self, ownerType):
        sequences = self._getEffectData().get('sequences')
        if sequences is not None:
            key = self.__ownerTypeToStr(ownerType)
            sequence = sequences.get(key)
            if sequence:
                return [ SequenceEffect(self.entity, data) for data in sequence ]
        return

    def __getEffect(self, ownerType):
        effects = self._getEffectData().get('effects')
        if effects is not None:
            key = self.__ownerTypeToStr(ownerType)
            effect = effects.get(key)
            if effect:
                soundStart = effects.get('{}_soundStart'.format(key), '')
                soundEnd = effects.get('{}_soundStart'.format(key), '')
                return Effect(self.entity, effect, soundStart, soundEnd)
        return

    def __ownerTypeToStr(self, ownerType):
        if ownerType == self.OwnerType.SELF:
            return 'owner'
        if ownerType == self.OwnerType.TEAM_MATE:
            return 'teamMate'
        return 'enemy' if ownerType == self.OwnerType.ENEMY else ''
