# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/cgf/ny_animations.py
import functools
import CGF
from GenericComponents import AnimatorComponent
from Triggers import TimeTriggerComponent
from cgf_components.token_component import TokenComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from constants import IS_CLIENT
from helpers import dependency
from new_year.ny_constants import AnchorNames
from new_year.skeletons.new_year import INewYearController
from new_year_common.items.components.ny_constants import OBJECT_MAX_LEVEL
from skeletons.gui.shared.utils import IHangarSpace
if IS_CLIENT:
    from new_year.helpers.ny_helpers import getCurrentObjectLevel

@registerComponent
class NyCustomizationZoneMarker(object):
    editorTitle = 'NY Customization Zone Marker'
    category = 'New Year'
    objectName = ComponentProperty(type=CGFMetaTypes.STRING, editorName='object name', value=AnchorNames.TREE)

    def __init__(self, *args, **kwargs):
        super(NyCustomizationZoneMarker, self).__init__(*args, **kwargs)
        self.animationEndCallbackID = None
        return


@registerComponent
class NyFireworks(object):
    editorTitle = 'NyFireworks'
    category = 'New Year'
    startAnimationLayer = ComponentProperty(type=CGFMetaTypes.STRING, editorName='start animation layer', value='')
    muteAnimationLink = ComponentProperty(type=CGFMetaTypes.LINK, editorName='mute animation', value=AnimatorComponent)
    muteAnimationLayer = ComponentProperty(type=CGFMetaTypes.STRING, editorName='mute animation layer', value='')
    linkedTokenName = ComponentProperty(type=CGFMetaTypes.STRING, editorName='linked token name', value='')

    def __init__(self, *args, **kwargs):
        super(NyFireworks, self).__init__(*args, **kwargs)
        self.animationEndCallbackID = None
        return

    def muteAnimation(self):
        if self.muteAnimationLink() is not None:
            self.muteAnimationLink().stopLayerByName(self.muteAnimationLayer)
            return True
        else:
            return False

    def unmuteAnimation(self):
        if self.muteAnimationLink() is not None:
            self.muteAnimationLink().startLayerByName(self.muteAnimationLayer)
            return True
        else:
            return False


class NewYearAnimatorManager(CGF.ComponentManager):
    __nyController = dependency.descriptor(INewYearController)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    _UNMUTE_ANIMATION_DELAY = 0.1

    def __init__(self):
        super(NewYearAnimatorManager, self).__init__()
        self.__animatorCache = {}

    def activate(self):
        self.__nyController.onCustomizationObjectUpdated += self.__onObjectUpdate

    def deactivate(self):
        self.__nyController.onCustomizationObjectUpdated -= self.__onObjectUpdate
        self.__animatorCache.clear()

    @onAddedQuery(CGF.GameObject, AnimatorComponent, NyCustomizationZoneMarker, TimeTriggerComponent)
    def handleNewYearAnimationAllAdded(self, gameObject, _, customizationObject, timeTrigger):
        fireworks = gameObject.findComponentByType(NyFireworks)
        self.__animatorCache[customizationObject.objectName, fireworks is not None] = CGF.ComponentLink(gameObject, AnimatorComponent)
        customizationObject.animationEndCallbackID = timeTrigger.addFireReaction(self.__zoneAnimationEndReaction)
        return

    @onRemovedQuery(CGF.GameObject, TimeTriggerComponent, AnimatorComponent, NyCustomizationZoneMarker)
    def handleNewYearAnimationRemoved(self, gameObject, timeTrigger, _, customizationObject):
        fireworks = gameObject.findComponentByType(NyFireworks)
        self.__animatorCache.pop((customizationObject.objectName, fireworks is not None), None)
        timeTrigger.removeFireReaction(customizationObject.animationEndCallbackID)
        return

    @onAddedQuery(CGF.GameObject, TimeTriggerComponent, AnimatorComponent, NyFireworks, TokenComponent)
    def handleNewYearFireworksFullAdded(self, gameObject, timeTrigger, animator, fireworks, token):
        if token.tokenName == fireworks.linkedTokenName:
            token.triggerEvent += functools.partial(self.__onAtmosphereLevelMaxLevelReached, gameObject, animator, fireworks)
        fireworks.animationEndCallbackID = timeTrigger.addFireReaction(self.__newYearFireworksEndReaction)

    @onRemovedQuery(CGF.GameObject, TimeTriggerComponent, AnimatorComponent, NyFireworks, TokenComponent)
    def handleNewYearFireworksRemoved(self, gameObject, timeTrigger, animator, fireworks, token):
        if token.tokenName == fireworks.linkedTokenName:
            token.triggerEvent -= functools.partial(self.__onAtmosphereLevelMaxLevelReached, gameObject, animator, fireworks)
        timeTrigger.removeFireReaction(fireworks.animationEndCallbackID)

    @onAddedQuery(CGF.GameObject, AnimatorComponent, NyFireworks, TokenComponent)
    def handleNewYearFireworksAnimationAdded(self, gameObject, *_):
        if not gameObject.findComponentByType(TimeTriggerComponent):
            gameObject.createComponent(TimeTriggerComponent, 0.0, 0)

    @onAddedQuery(CGF.GameObject, AnimatorComponent, NyCustomizationZoneMarker)
    def handleNewYearAnimationAdded(self, gameObject, *_):
        if not gameObject.findComponentByType(TimeTriggerComponent):
            gameObject.createComponent(TimeTriggerComponent, 0.0, 0)

    def __onObjectUpdate(self, *updatedObjects):
        if self.__nyController.isOnboardingOpen() or not self.__hangarSpace.spaceInited:
            return
        for updatedObject in updatedObjects:
            self.startZoneAnimator(updatedObject)
            if self.__needShowFireworksAnimation(updatedObject):
                self.startZoneAnimator(updatedObject, True)

    def __needShowFireworksAnimation(self, objectName):
        return getCurrentObjectLevel(objectName) == OBJECT_MAX_LEVEL

    def __onAtmosphereLevelMaxLevelReached(self, gameObject, animator, fireworks, _):
        if not gameObject.isValid():
            return
        timeTrigger = gameObject.findComponentByType(TimeTriggerComponent)
        fireworks.muteAnimation()
        animator.startLayerByName(fireworks.startAnimationLayer)
        timeTrigger.reset(animator.getDuration() + self._UNMUTE_ANIMATION_DELAY, 1)

    def startZoneAnimator(self, objectName, fireworks=False):
        animatorLink = self.__animatorCache.get((objectName, fireworks), None)
        if animatorLink is None:
            return
        else:
            animator = animatorLink()
            if not animator:
                return
            go = animatorLink.gameObject
            timeTrigger = go.findComponentByType(TimeTriggerComponent)
            duration = animator.getDuration()
            animator.start()
            timeTrigger.reset(duration, 1)
            return duration

    @staticmethod
    def __zoneAnimationEndReaction(who):
        if not who.isValid():
            return
        animator = who.findComponentByType(AnimatorComponent)
        if animator:
            animator.stop()

    @staticmethod
    def __newYearFireworksEndReaction(who):
        if not who.isValid():
            return
        animator = who.findComponentByType(AnimatorComponent)
        fireworks = who.findComponentByType(NyFireworks)
        if animator and fireworks:
            animator.stopLayerByName(fireworks.startAnimationLayer)
            fireworks.unmuteAnimation()
