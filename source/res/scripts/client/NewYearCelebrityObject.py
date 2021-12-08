# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearCelebrityObject.py
import logging
import AnimationSequence
import BigWorld
from ClientSelectableObject import ClientSelectableObject
from entity_constants import HighlightColors
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from helpers import dependency
from new_year.ny_constants import AnchorNames
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import INewYearController, ICelebritySceneController
from new_year.cgf_components.highlight_manager import HighlightGroupComponent
from uilogging.ny.mixins import SelectableObjectLoggerMixin
from vehicle_systems.stricted_loading import makeCallbackWeak
_logger = logging.getLogger(__name__)

class NewYearCelebrityObject(ClientSelectableObject, SelectableObjectLoggerMixin):
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _nyController = dependency.descriptor(INewYearController)
    _celebrityController = dependency.descriptor(ICelebritySceneController)
    _HIGHLIGHT_COLOR = HighlightColors.BLUE

    def __init__(self):
        super(NewYearCelebrityObject, self).__init__()
        self.__animator = None
        self.__modelWrapperContainer = None
        return

    def onEnterWorld(self, prereqs):
        super(NewYearCelebrityObject, self).onEnterWorld(prereqs)
        self._nyController.onStateChanged += self.__onStateChanged
        self.__onStateChanged()
        if self.stateMachine:
            animationLoader = AnimationSequence.Loader(self.stateMachine, self.spaceID)
            BigWorld.loadResourceListBG((animationLoader,), makeCallbackWeak(self.__onAnimatorLoaded, self.stateMachine))
        self._celebrityController.addCelebrityEntity(self)
        if self.selectionGroupIdx:
            self.entityGameObject.createComponent(HighlightGroupComponent, self.selectionGroupIdx)

    def onLeaveWorld(self):
        self._celebrityController.removeCelebrityEntity()
        self._nyController.onStateChanged -= self.__onStateChanged
        if self.__animator is not None:
            self.__animator.stop()
            self.__animator.unsubscribe(self.__animatorEvent)
            self.__animator = None
        self.__modelWrapperContainer = None
        self.entityGameObject.removeComponentByType(HighlightGroupComponent)
        super(NewYearCelebrityObject, self).onLeaveWorld()
        return

    def onMouseClick(self):
        super(NewYearCelebrityObject, self).onMouseClick()
        NewYearSoundsManager.playEvent(NewYearSoundEvents.ENTER_CUSTOME)
        self.logClick(AnchorNames.CELEBRITY)
        NewYearNavigation.switchByAnchorName(AnchorNames.CELEBRITY)

    def setAnimatorTrigger(self, triggerName):
        if self.__animator is None:
            _logger.error('Failed to set animation state machine trigger: %s. Missing state machine for Celebrity Entity', triggerName)
            return
        else:
            self.__animator.setTrigger(triggerName)
            return

    def _getCollisionModelsPrereqs(self):
        if self.collisionModelName:
            collisionModels = ((0, self.collisionModelName),)
            return collisionModels
        return super(NewYearCelebrityObject, self)._getCollisionModelsPrereqs()

    def __checkResource(self, resourceName, resourceList):
        if self.model is None:
            _logger.error('Could not spawn resource. Model is not loaded: %s', self.modelName)
            return False
        elif resourceName in resourceList.failedIDs:
            _logger.error('Failed to load resource "%s". Effects wont be used', resourceName)
            return False
        else:
            if self.__modelWrapperContainer is None:
                self.__modelWrapperContainer = AnimationSequence.ModelWrapperContainer(self.model, self.spaceID)
            return True

    def __onAnimatorLoaded(self, resourceName, resourceList):
        if not self.__checkResource(resourceName, resourceList):
            return
        self.__animator = resourceList[self.stateMachine]
        self.__animator.bindTo(self.__modelWrapperContainer)
        self.__animator.subscribe(self.__animatorEvent)
        self.__animator.start()
        if self._celebrityController.isInChallengeView:
            self._celebrityController.onEnterChallenge()

    def __animatorEvent(self, name, _):
        self._celebrityController.onAnimatorEvent(name)

    def __onStateChanged(self):
        self.setEnable(self._nyController.isEnabled())
