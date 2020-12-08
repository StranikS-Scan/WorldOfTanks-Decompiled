# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearToyObject.py
import logging
import BigWorld
import AnimationSequence
from helpers.animator_instance_properties import AnimatorInstanceProperties
from vehicle_systems.stricted_loading import makeCallbackWeak
from NewYearSelectableObject import NewYearSelectableObject
from helpers.EffectsList import EffectsListPlayer
_logger = logging.getLogger(__name__)

class NewYearToyObject(NewYearSelectableObject):

    def __init__(self):
        super(NewYearToyObject, self).__init__()
        self.__hangingEffectPlayer = None
        self.__regularEffectPlayer = None
        self.__animators = {}
        self.__appearanceDelayCallbackId = None
        self.__alphaFadeFashion = None
        return

    def onEnterWorld(self, prereqs):
        if self._selfDestroyCheck():
            return
        super(NewYearToyObject, self).onEnterWorld(prereqs)
        self.__playEffects()
        if self.minAlpha:
            self.__alphaFadeFashion = BigWorld.WGAlphaFadeFashion()
            self.__alphaFadeFashion.minAlpha = self.minAlpha
            self.__alphaFadeFashion.maxAlphaDist = self.maxAlphaDistance * self.maxAlphaDistance
            self.model.fashion = self.__alphaFadeFashion
        if self.appearanceDelay:
            self.model.visible = False
            self.__appearanceDelayCallbackId = BigWorld.callback(self.appearanceDelay, self.__showModel)

    def onLeaveWorld(self):
        if self.__appearanceDelayCallbackId is not None:
            BigWorld.cancelCallback(self.__appearanceDelayCallbackId)
            self.__appearanceDelayCallbackId = None
        if self.__hangingEffectPlayer is not None:
            self.__hangingEffectPlayer.stop()
            self.__hangingEffectPlayer = None
        if self.__regularEffectPlayer is not None:
            self.__regularEffectPlayer.stop()
            self.__regularEffectPlayer = None
        for animator in self.__animators.itervalues():
            if animator is not None:
                animator.stop()

        self.__animators.clear()
        super(NewYearToyObject, self).onLeaveWorld()
        return

    def __playEffects(self):
        if self.hangingEffectName:
            self.__hangingEffectPlayer = self.__createEffectPlayer(self.hangingEffectName)
            if self.__hangingEffectPlayer is not None:
                self.__hangingEffectPlayer.play(self.model)
        if self.regularEffectName:
            self.__regularEffectPlayer = self.__createEffectPlayer(self.regularEffectName)
            if self.__regularEffectPlayer is not None:
                self.__regularEffectPlayer.play(self.model)
        if self.hangingAnimationSequence:
            self.__spawnAnimationSequence(self.hangingAnimationSequence, isHanging=True)
        if self.animationSequence:
            self.__spawnAnimationSequence(self.animationSequence)
        return

    def __createEffectPlayer(self, effectName):
        effect = self.customizableObjectsMgr.getEffect(effectName)
        if effect is None:
            return
        else:
            effectPlayer = EffectsListPlayer(effect.effectsList, effect.keyPoints)
            return effectPlayer

    def __spawnAnimationSequence(self, resourceName, isHanging=False):
        if resourceName in self.__animators:
            _logger.error('Unable to start animation sequence, because it is already loaded: "%s"', resourceName)
            return
        elif self.model is None:
            _logger.error('Could not spawn animation sequence "%s", because model is not loaded: "%s"', resourceName, self.modelName)
            return
        else:
            self.__animators[resourceName] = None
            animProps = AnimatorInstanceProperties(loopCount=1, loop=False) if isHanging else AnimatorInstanceProperties()
            loader = AnimationSequence.Loader(resourceName, self.spaceID, animProps)
            BigWorld.loadResourceListBG((loader,), makeCallbackWeak(self.__onAnimatorLoaded, resourceName))
            return

    def __onAnimatorLoaded(self, resourceName, resourceList):
        animator = resourceList[resourceName]
        animator.bindTo(AnimationSequence.ModelWrapperContainer(self.model, self.spaceID))
        animator.start()
        self.__animators[resourceName] = animator

    def __showModel(self):
        self.__appearanceDelayCallbackId = None
        self.model.visible = True
        return
