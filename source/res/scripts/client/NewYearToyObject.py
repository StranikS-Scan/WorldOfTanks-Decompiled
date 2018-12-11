# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearToyObject.py
import BigWorld
import AnimationSequence
from vehicle_systems.stricted_loading import makeCallbackWeak
from NewYearSelectableObject import NewYearSelectableObject
from helpers.EffectsList import EffectsListPlayer

class NewYearToyObject(NewYearSelectableObject):

    def __init__(self):
        super(NewYearToyObject, self).__init__()
        self.__hangingEffectPlayer = None
        self.__regularEffectPlayer = None
        self.__animator = None
        self.__appearanceDelayCallbackId = None
        return

    def onEnterWorld(self, prereqs):
        if self._selfDestroyCheck():
            return
        super(NewYearToyObject, self).onEnterWorld(prereqs)
        self.__playEffects()
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
        if self.__animator is not None:
            self.__animator.stop()
            self.__animator = None
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

    def __spawnAnimationSequence(self, resourceName):
        loader = AnimationSequence.Loader(resourceName, self.spaceID)
        BigWorld.loadResourceListBG((loader,), makeCallbackWeak(self.__onAnimatorLoaded, resourceName))

    def __onAnimatorLoaded(self, resourceName, resourceList):
        self.__animator = resourceList[resourceName]
        self.__animator.bindTo(AnimationSequence.ModelWrapperContainer(self.model))
        self.__animator.start()

    def __showModel(self):
        self.__appearanceDelayCallbackId = None
        self.model.visible = True
        return
