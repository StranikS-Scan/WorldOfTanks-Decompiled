# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/effect_controller.py
from collections import namedtuple
import AnimationSequence
import BigWorld
import SoundGroups
from debug_utils import LOG_ERROR, LOG_WARNING
from event_effect_settings import EventEffectsSettings
from helpers.CallbackDelayer import CallbackDelayer
from vehicle_systems.stricted_loading import makeCallbackWeak
from helpers.EffectsList import effectsFromSection, EffectsListPlayer
_EffectListPlayerDescr = namedtuple('EffectListPlayerDescr', ('effectListPlayer', 'effectEnd'))
g_effectSettings = None

class EffectController(CallbackDelayer):

    def __init__(self, effectKey):
        global g_effectSettings
        CallbackDelayer.__init__(self)
        self.effectKey = effectKey
        if 'g_effectSettings' in globals() and globals()['g_effectSettings'] is not None:
            __settings = globals()['g_effectSettings']
            self._effectsList = __settings.eventEffectsSettings
            self._dynamicObjects = __settings.dynamicObjects
        else:
            g_effectSettings = EventEffectsSettings()
            self._effectsList = g_effectSettings.eventEffectsSettings
            self._dynamicObjects = g_effectSettings.dynamicObjects
        self._effectsList = self._effectsList.get(self.effectKey, None)
        self._currentSequence = None
        self._currentRegularEffect = None
        self._currentHangingEffect = None
        self._sequenceExternalCallback = None
        self._sequenceMarkedForPlayback = False
        return

    def __getEffectPlayerDescr(self, effectType):
        effect = effectsFromSection(self._dynamicObjects[self._effectsList[effectType]['name']])
        effectEnd = 0
        for keyPoint in effect.keyPoints:
            if keyPoint.name == 'effectEnd':
                effectEnd = keyPoint.time

        return _EffectListPlayerDescr(EffectsListPlayer(effect.effectsList, effect.keyPoints, debugParent=self), effectEnd)

    @property
    def isSequencePlaying(self):
        return bool(self._currentSequence)

    def reset(self):
        self._sequenceMarkedForPlayback = False
        if self._currentSequence is not None:
            self._currentSequence.stop()
            self._currentSequence = None
        if self._currentRegularEffect is not None:
            self._currentRegularEffect.stop()
            self._currentRegularEffect = None
        if self._currentHangingEffect is not None:
            self._currentHangingEffect.stop()
            self._currentHangingEffect = None
        CallbackDelayer.destroy(self)
        return

    def playHangingEffect(self, entity):
        if self._effectsList is not None and 'hanging' in self._effectsList:
            self._currentHangingEffect = self.__getEffectPlayerDescr('hanging').effectListPlayer
            self._currentHangingEffect.play(entity.model)
        else:
            LOG_ERROR('No hanging effect configuration for {} '.format(self.effectKey))
        return

    def playRegularEffect(self, entity):
        if self._effectsList is not None and 'regular' in self._effectsList:
            self._currentRegularEffect = self.__getEffectPlayerDescr('regular').effectListPlayer
            self._currentRegularEffect.play(entity.model)
        else:
            LOG_ERROR('No regular effect configuration for {}'.format(self.effectKey))
        return

    def playSequence(self, entity, callback=None):
        if self._effectsList is not None and 'sequence' in self._effectsList:
            self._sequenceMarkedForPlayback = True
            self._sequenceExternalCallback = callback
            spaceID = BigWorld.player().spaceID
            path = self._dynamicObjects[self._effectsList['sequence']['name']].readString('path')
            loader = AnimationSequence.Loader(path, spaceID)
            BigWorld.loadResourceListBG((loader,), makeCallbackWeak(self.__onAnimatorLoaded, path, entity))
        else:
            LOG_ERROR('No sequenced configuration for {}'.format(self.effectKey))
        return

    def __onAnimatorLoaded(self, resourceName, entity, resourceList):
        if not self._sequenceMarkedForPlayback:
            return
        else:
            animator = resourceList[resourceName]
            if isinstance(entity, BigWorld.Model):
                spaceID = BigWorld.player().spaceID
                animator.bindTo(AnimationSequence.ModelWrapperContainer(entity, spaceID))
            else:
                if entity.isDestroyed:
                    return
                if entity.model is None:
                    LOG_WARNING('Model is NONE for sequence {}'.format(resourceName))
                    return
                animator.bindTo(AnimationSequence.CompoundWrapperContainer(entity.model))
            animator.start()
            self._currentSequence = animator
            if self._effectsList['sequence']['duration']:
                self.delayCallback(self._effectsList['sequence']['duration'], self.stopSequnce)
            wwsound = self._dynamicObjects[self._effectsList['sequence']['name']].readString('wwsound', '')
            if wwsound and entity.position is not None:
                SoundGroups.g_instance.playSoundPos(wwsound, entity.position)
            return

    def stopHangingEffect(self):
        if self._currentHangingEffect is not None:
            self._currentHangingEffect.stop()
            self._currentHangingEffect = None
        return

    def stopSequnce(self):
        if self._currentSequence is not None:
            self._currentSequence.stop()
            self._currentSequence = None
        if self._sequenceExternalCallback is not None:
            self._sequenceExternalCallback()
        return
