# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearCelebrityObject.py
import logging
import AnimationSequence
import BigWorld
from ClientSelectableObject import ClientSelectableObject
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates, CameraRelatedEvents
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.shared import g_eventBus
from helpers import dependency
from new_year.ny_constants import AnchorNames
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import INewYearController, ICelebritySceneController
from uilogging.decorators import simpleLog, loggerEntry, loggerTarget
from uilogging.ny.constants import NY_LOG_KEYS, NY_LOG_ACTIONS
from uilogging.ny.loggers import NYLogger
from vehicle_systems.stricted_loading import makeCallbackWeak
_logger = logging.getLogger(__name__)

@loggerTarget(logKey=NY_LOG_KEYS.NY_CELEBRITY_CHALLENGE, loggerCls=NYLogger)
class NewYearCelebrityObject(ClientSelectableObject):
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _nyController = dependency.descriptor(INewYearController)
    _celebrityController = dependency.descriptor(ICelebritySceneController)

    def __init__(self):
        super(NewYearCelebrityObject, self).__init__()
        self.__animator = None
        self.__modelWrapperContainer = None
        return

    @loggerEntry
    def onEnterWorld(self, prereqs):
        super(NewYearCelebrityObject, self).onEnterWorld(prereqs)
        self._nyController.onStateChanged += self.__onStateChanged
        self.__onStateChanged()
        g_eventBus.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated)
        if self.stateMachine:
            animationLoader = AnimationSequence.Loader(self.stateMachine, self.spaceID)
            BigWorld.loadResourceListBG((animationLoader,), makeCallbackWeak(self.__onAnimatorLoaded, self.stateMachine))
        self._celebrityController.addCelebrityEntity(self)

    def onLeaveWorld(self):
        self._celebrityController.removeCelebrityEntity()
        self._nyController.onStateChanged -= self.__onStateChanged
        g_eventBus.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated)
        if self.__animator is not None:
            self.__animator.stop()
            self.__animator.unsubscribe(self.__animatorEvent)
            self.__animator = None
        self.__modelWrapperContainer = None
        super(NewYearCelebrityObject, self).onLeaveWorld()
        return

    @simpleLog(action=NY_LOG_ACTIONS.NY_CELEBRITY_ENTRY_FROM_HANGAR)
    def onMouseClick(self):
        super(NewYearCelebrityObject, self).onMouseClick()
        NewYearSoundsManager.playEvent(NewYearSoundEvents.ENTER_CUSTOME)
        NewYearNavigation.switchByAnchorName(AnchorNames.CELEBRITY)

    def setAnimatorTrigger(self, triggerName):
        if self.__animator is None:
            _logger.error('Failed to set animation state machine trigger: %s. Missing state machine for Celebrity Entity', triggerName)
            return
        else:
            self.__animator.setTrigger(triggerName)
            return

    def _addEdgeDetect(self):
        self._celebrityController.addEdgeDetect()

    def _delEdgeDetect(self):
        self._celebrityController.delEdgeDetect()

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

    def __onCameraEntityUpdated(self, event):
        ctx = event.ctx
        state = ctx['state']
        entityId = ctx['entityId']
        if state == CameraMovementStates.FROM_OBJECT:
            if self.__isHangarVehicleEntity(entityId):
                self.setEnable(False)
        elif state == CameraMovementStates.ON_OBJECT:
            if self.__isHangarVehicleEntity(entityId):
                if not self.enabled and self._nyController.isEnabled():
                    self.setEnable(True)

    def __isHangarVehicleEntity(self, entityId):
        return entityId == self._hangarSpace.space.vehicleEntityId

    def __onStateChanged(self):
        self.setEnable(self._nyController.isEnabled())
