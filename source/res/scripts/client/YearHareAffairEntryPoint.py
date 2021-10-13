# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/YearHareAffairEntryPoint.py
import logging
import enum
import CGF
import Math
from ClientSelectableObject import ClientSelectableObject
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents, CameraMovementStates
from gui.shared import g_eventBus
from helpers import dependency
from skeletons.gui.game_control import IYearHareAffairController
from skeletons.gui.shared.utils import IHangarSpace
_logger = logging.getLogger(__name__)

class _EntryPointStates(enum.IntEnum):
    ACTIVE = 0
    INACTIVE = 1


class YearHareAffairEntryPoint(ClientSelectableObject):
    __yhaController = dependency.descriptor(IYearHareAffairController)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(YearHareAffairEntryPoint, self).__init__()
        self.__gameObjects = {}

    def onEnterWorld(self, prereqs):
        super(YearHareAffairEntryPoint, self).onEnterWorld(prereqs)
        self.__loadPrefabs()
        self.__addListeners()

    def onLeaveWorld(self):
        self.__removeListeners()
        self.__clearPrefabs()
        super(YearHareAffairEntryPoint, self).onLeaveWorld()

    def onMouseClick(self):
        super(YearHareAffairEntryPoint, self).onMouseClick()
        self.__yhaController.showWindow()

    def _getCollisionModelsPrereqs(self):
        if self.outlineModelName:
            collisionModels = ((0, self.outlineModelName),)
            return collisionModels
        return super(YearHareAffairEntryPoint, self)._getCollisionModelsPrereqs()

    def __loadPrefabs(self):
        parent = self.entityGameObject
        CGF.loadGameObjectIntoHierarchy(self.activePrefab, parent, Math.Vector3(), self.__onGameObjectLoaded(_EntryPointStates.ACTIVE))
        CGF.loadGameObjectIntoHierarchy(self.inactivePrefab, parent, Math.Vector3(), self.__onGameObjectLoaded(_EntryPointStates.INACTIVE))

    def __clearPrefabs(self):
        for go in self.__gameObjects.itervalues():
            CGF.removeGameObject(go)

        self.__gameObjects.clear()

    def __addListeners(self):
        g_eventBus.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated)
        self.__yhaController.onStateChanged += self.__onStateChanged

    def __removeListeners(self):
        g_eventBus.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated)
        self.__yhaController.onStateChanged -= self.__onStateChanged

    def __onCameraEntityUpdated(self, event):
        ctx = event.ctx
        state = ctx['state']
        entityId = ctx['entityId']
        if state == CameraMovementStates.FROM_OBJECT:
            if self.__isHangarVehicleEntity(entityId):
                self.setEnable(False)
        elif state == CameraMovementStates.ON_OBJECT:
            if self.__isHangarVehicleEntity(entityId):
                if not self.enabled:
                    self.setEnable(True)

    def __isHangarVehicleEntity(self, entityId):
        return False if self.__hangarSpace.space is None else entityId == self.__hangarSpace.space.vehicleEntityId

    def __onStateChanged(self):
        self.__updateState()

    def __onGameObjectLoaded(self, state):

        def wrapped(gameObject):
            self.__gameObjects[state] = gameObject
            self.__updateState()

        return wrapped

    def __updateState(self):
        isActiveState = self.__yhaController.isVideoAvailable
        self.__toggleGameObject(state=_EntryPointStates.ACTIVE, activate=isActiveState)
        self.__toggleGameObject(state=_EntryPointStates.INACTIVE, activate=not isActiveState)

    def __toggleGameObject(self, state, activate):
        go = self.__gameObjects.get(state)
        if go is not None:
            if activate:
                go.activate()
            else:
                go.deactivate()
        return
