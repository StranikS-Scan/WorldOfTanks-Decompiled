# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/cgf/raccoon_customization_components.py
from functools import partial
import CGF
import GenericComponents
from NyComponents import NySlotComponent
from Triggers import TimeTriggerComponent
from cgf_script.component_meta_class import registerComponent
from cgf_script.managers_registrator import onAddedQuery
from constants import IS_EDITOR
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from new_year.skeletons.new_year import INewYearController, INewYearRaccoonController
from cache import cached_property

@registerComponent
class UniqueAnimationOwner(object):
    editorTitle = 'Unique Animation Owner'
    category = 'New Year'


@registerComponent
class NeedHidden(object):
    editorTitle = 'Need Hidden'
    category = 'New Year'


@registerComponent
class RaccoonNeedHidden(object):
    editorTitle = 'Raccoon Need Hidden'
    category = 'New Year'


class RaccoonManager(CGF.ComponentManager):
    _nyController = dependency.descriptor(INewYearController)
    __raccoonCtrl = dependency.descriptor(INewYearRaccoonController)

    def __init__(self):
        super(RaccoonManager, self).__init__()
        self.__uniqueAnimationEnabled = False
        self.__hideGOCache = {}
        self.__callbackDelayer = CallbackDelayer()
        self.__currentAnimation = None
        self.__raccoon = None
        self.__currentAnimatorCount = 0
        return

    @cached_property
    def __hierarchyManager(self):
        return CGF.HierarchyManager(self.spaceID)

    def activate(self):
        self._nyController.onSetHangToyEffectEnabled += self.setUniqueAnimationEnabled
        self.__raccoonCtrl.onViewExit += self.onViewExit

    def deactivate(self):
        self._nyController.onSetHangToyEffectEnabled -= self.setUniqueAnimationEnabled
        self.__raccoonCtrl.onViewExit -= self.onViewExit
        self.__callbackDelayer.clearCallbacks()

    if not IS_EDITOR:

        @onAddedQuery(CGF.GameObject, UniqueAnimationOwner, tickGroup='PostHierarchy')
        def onToyUniqueAnimationAdded(self, go, _):
            if self.__uniqueAnimationEnabled:
                currentAnimation = self.__hierarchyManager.getChildren(go)
                slotGO = self.__findSlotGO(go)
                if not currentAnimation or not slotGO:
                    return
                if self.__currentAnimation:
                    self.__fade(partial(self.__restartAnimation, slotGO, currentAnimation))
                else:
                    self.__prepareHiddenCacheToRestart(slotGO)
                    self.__currentAnimation = currentAnimation
                    self.__fade(self.__startAnimation)

    @onAddedQuery(CGF.GameObject, NeedHidden)
    def onNeedHiddenAdded(self, go, _):
        if not self.__uniqueAnimationEnabled:
            for child in self.__hierarchyManager.getChildrenIncludingInactive(go):
                child.activate()

    @onAddedQuery(CGF.GameObject, RaccoonNeedHidden)
    def onRaccoonNeedHiddenAdded(self, go, _):
        self.__raccoon = go

    def setUniqueAnimationEnabled(self, enabled=True):
        self.__uniqueAnimationEnabled = enabled

    def onViewExit(self):
        self.__callbackDelayer.stopCallback(self.__fade)
        self.__callbackDelayer.stopCallback(self.__showGO)
        self.__callbackDelayer.delayCallback(0.75, self.__finalizeAnimation)

    def __callbackFinishAnimator(self, go):
        if go.isValid():
            go.findComponentByType(GenericComponents.AnimatorComponent).stop()
        self.__currentAnimatorCount -= 1
        if self.__currentAnimatorCount == 0:
            self.__currentAnimation = None
        return

    def __finalizeAnimation(self):
        self.__callbackDelayer.stopCallback(self.__fade)
        self.__callbackDelayer.stopCallback(self.__showGO)
        self.__showGO()
        if not self.__currentAnimation:
            return
        else:
            for child in self.__currentAnimation:
                if not child.isValid():
                    continue
                animator = child.findComponentByType(GenericComponents.AnimatorComponent)
                animator.stop()

            self.__currentAnimation = None
            return

    def __restartAnimation(self, slotGO, currentAnimation):
        self.__finalizeAnimation()
        self.__prepareHiddenCacheToRestart(slotGO)
        self.__currentAnimation = currentAnimation
        self.__startAnimation()

    def __startAnimation(self):
        maxAnimatorDuration = 0
        animatorCount = 0
        for child in self.__currentAnimation:
            animator = child.findComponentByType(GenericComponents.AnimatorComponent)
            animator.start()
            duration = animator.getDuration()
            maxAnimatorDuration = max(maxAnimatorDuration, duration)
            animatorCount += 1
            timer = child.findComponentByType(TimeTriggerComponent)
            if not timer:
                timer = child.createComponent(TimeTriggerComponent, duration, 1)
            else:
                timer.reset(duration, 1)
            timer.addFireReaction(self.__callbackFinishAnimator)

        self.__currentAnimatorCount = animatorCount
        self.__hideGO()
        self.__callbackDelayer.delayCallback(maxAnimatorDuration, self.__showGO)
        self.__callbackDelayer.delayCallback(maxAnimatorDuration - 0.2, self.__fade)

    def __fade(self, callback=None):
        self.__raccoonCtrl.showFade(callback)

    def __prepareHiddenCacheToRestart(self, slotGO):
        self.__hideGOCache = {go.id:go for go, _ in self.__hierarchyManager.findComponentsInHierarchy(slotGO, NeedHidden)}
        self.__hideGOCache[self.__raccoon.id] = self.__raccoon

    def __hideGO(self):
        for goId, hiddenGO in self.__hideGOCache.items():
            if hiddenGO.isValid():
                hiddenGO.deactivate()
            self.__hideGOCache.pop(goId)

    def __showGO(self):
        for goId, hiddenGO in self.__hideGOCache.items():
            if hiddenGO.isValid():
                hiddenGO.activate()
                for child in self.__hierarchyManager.getChildrenIncludingInactive(hiddenGO):
                    child.activate()

            self.__hideGOCache.pop(goId)

    def __findSlotGO(self, go):
        return go if go.findComponentByType(NySlotComponent) else self.__findSlotGO(self.__hierarchyManager.getParent(go))
