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
from new_year_common.items.components.ny_constants import ToyTypes

@registerComponent
class UniqueAnimationOwner(object):
    editorTitle = 'Unique Animation Owner'
    category = 'New Year'

    def __init__(self, *args, **kwargs):
        super(UniqueAnimationOwner, self).__init__(*args, **kwargs)
        self.slotID = None
        return


@registerComponent
class NeedHidden(object):
    editorTitle = 'Need Hidden'
    category = 'New Year'

    def __init__(self, *args, **kwargs):
        super(NeedHidden, self).__init__(*args, **kwargs)
        self.slotID = None
        return


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
        self.__callbackDelayer = CallbackDelayer()
        self.__raccoon = None
        self.__activeAnimationSlotID = None
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
        self.__raccoon = None
        self.__activeAnimationSlotID = None
        return

    @onAddedQuery(CGF.GameObject, NySlotComponent)
    def onSlotAdded(self, go, slotComponent):
        if slotComponent.type in ToyTypes.PET:
            for child in self.__hierarchyManager.getChildrenRecursively(go):
                if child.isValid():
                    uniqOwner = child.findComponentByType(UniqueAnimationOwner)
                    if uniqOwner:
                        uniqOwner.slotID = slotComponent.id
                    needHidden = child.findComponentByType(NeedHidden)
                    if needHidden:
                        needHidden.slotID = slotComponent.id

    if not IS_EDITOR:

        @onAddedQuery(CGF.GameObject, UniqueAnimationOwner, tickGroup='PostHierarchy')
        def onToyUniqueAnimationAdded(self, go, animatorOwner):
            slotGO = self.__findSlotGO(go)
            if slotGO:
                animatorOwner.slotID = slotGO.findComponentByType(NySlotComponent).id
            if self.__uniqueAnimationEnabled:
                if not slotGO:
                    return
                slotID = slotGO.findComponentByType(NySlotComponent).id
                if self.__activeAnimationSlotID is not None:
                    self.__fade(partial(self.__restartRaccoonAnimation, slotID))
                else:
                    self.__fade(partial(self.__startRaccoonAnimation, slotID))
            return

    @onAddedQuery(CGF.GameObject, NeedHidden)
    def onNeedHiddenAdded(self, go, needHidden):
        if not self.__uniqueAnimationEnabled:
            for child in self.__hierarchyManager.getChildrenIncludingInactive(go):
                child.activate()

        slotGO = self.__findSlotGO(go)
        if slotGO:
            needHidden.slotID = slotGO.findComponentByType(NySlotComponent).id

    @onAddedQuery(CGF.GameObject, RaccoonNeedHidden)
    def onRaccoonNeedHiddenAdded(self, go, _):
        self.__raccoon = go

    def setUniqueAnimationEnabled(self, enabled=True):
        self.__uniqueAnimationEnabled = enabled

    def onViewExit(self):
        self.__callbackDelayer.stopCallback(self.__fade)
        self.__callbackDelayer.stopCallback(self.__stopRaccoonAnimation)
        self.__callbackDelayer.delayCallback(0.75, self.__finalizeAnimation)

    def __callbackFinishAnimator(self, go):
        if go.isValid():
            animator = go.findComponentByType(GenericComponents.AnimatorComponent)
            if animator and animator.isValid():
                animator.stop()

    def __finalizeAnimation(self, updateState=True):
        self.__callbackDelayer.stopCallback(self.__fade)
        self.__callbackDelayer.stopCallback(self.__stopRaccoonAnimation)
        self.__activeAnimationSlotID = None
        if updateState:
            self.__updateAnimationState()
        return

    def __restartRaccoonAnimation(self, slotID):
        self.__finalizeAnimation(updateState=False)
        self.__startRaccoonAnimation(slotID)

    def __startRaccoonAnimation(self, slotID):
        self.__activeAnimationSlotID = slotID
        maxAnimatorDuration = 0
        queryAnimationOwner = CGF.Query(self.spaceID, (CGF.GameObject, UniqueAnimationOwner))
        for animationOwnerGO, animationOwner in queryAnimationOwner:
            if animationOwnerGO.isValid() and animationOwner.slotID == slotID:
                for child in self.__hierarchyManager.getChildren(animationOwnerGO):
                    animator = child.findComponentByType(GenericComponents.AnimatorComponent)
                    maxAnimatorDuration = max(maxAnimatorDuration, animator.getDuration())

        self.__updateAnimationState()
        self.__callbackDelayer.delayCallback(maxAnimatorDuration, self.__stopRaccoonAnimation)
        self.__callbackDelayer.delayCallback(maxAnimatorDuration - 0.2, self.__fade)

    def __stopRaccoonAnimation(self):
        self.__activeAnimationSlotID = None
        self.__updateAnimationState()
        return

    def __fade(self, callback=None):
        if self.__raccoonCtrl.isFade():
            self.__raccoonCtrl.replaceCallback(callback)
        else:
            self.__raccoonCtrl.showFade(callback)

    def __findSlotGO(self, go):
        return go if go.isValid() and go.findComponentByType(NySlotComponent) else self.__findSlotGO(self.__hierarchyManager.getParent(go))

    def __updateAnimationState(self):
        queryNeedHidden = CGF.Query(self.spaceID, (CGF.GameObject, NeedHidden))
        queryAnimationOwner = CGF.Query(self.spaceID, (CGF.GameObject, UniqueAnimationOwner))
        for hiddenGO, needHidden in queryNeedHidden:
            if hiddenGO.isValid() and needHidden.slotID is not None:
                self.__updateNeedHiddenGoState(hiddenGO, needHidden)

        self.__updateRaccoonNeedHiddenState()
        for animationOwnerGO, animationOwner in queryAnimationOwner:
            if animationOwnerGO.isValid() and animationOwner.slotID is not None:
                self.__updateAnimationOwnerState(animationOwnerGO, animationOwner)

        return

    def __updateNeedHiddenGoState(self, go, needHidden):
        if self.__activeAnimationSlotID is not None and needHidden.slotID == self.__activeAnimationSlotID:
            for child in self.__hierarchyManager.getChildrenIncludingInactive(go):
                if child.isValid():
                    child.deactivate()

        else:
            for child in self.__hierarchyManager.getChildrenIncludingInactive(go):
                if child.isValid():
                    child.activate()

        return

    def __updateRaccoonNeedHiddenState(self):
        if self.__raccoon is not None and self.__raccoon.isValid():
            for child in self.__hierarchyManager.getChildrenIncludingInactive(self.__raccoon):
                if self.__activeAnimationSlotID is not None:
                    if child.isValid():
                        child.deactivate()
                if child.isValid():
                    child.activate()

        return

    def __updateAnimationOwnerState(self, go, animationOwner):
        if self.__activeAnimationSlotID is not None and animationOwner.slotID == self.__activeAnimationSlotID:
            for child in self.__hierarchyManager.getChildren(go):
                self.__startChildAnimation(child)

        else:
            for child in self.__hierarchyManager.getChildren(go):
                self.__stopChildAnimation(child)

        return

    def __startChildAnimation(self, go):
        if not go.isValid():
            return
        animator = go.findComponentByType(GenericComponents.AnimatorComponent)
        if animator and animator.isValid():
            animator.start()
            duration = animator.getDuration()
            timer = go.findComponentByType(TimeTriggerComponent)
            if not timer:
                timer = go.createComponent(TimeTriggerComponent, duration, 1)
            else:
                timer.reset(duration, 1)
            timer.addFireReaction(self.__callbackFinishAnimator)

    def __stopChildAnimation(self, go):
        if not go.isValid():
            return
        animator = go.findComponentByType(GenericComponents.AnimatorComponent)
        if animator and animator.isValid():
            animator.stop()
            timer = go.findComponentByType(TimeTriggerComponent)
            if timer:
                timer.reset(0.0, 0)
