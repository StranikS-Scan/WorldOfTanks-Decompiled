# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableCameraObject.py
import CGF
from ClientSelectableObject import ClientSelectableObject
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates, CameraRelatedEvents
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from helpers import dependency
from cgf_components.hangar_camera_manager import HangarCameraManager
from skeletons.gui.shared.utils import IHangarSpace

class ClientSelectableCameraObject(ClientSelectableObject):
    hangarSpace = dependency.descriptor(IHangarSpace)
    allCameraObjects = set()

    def __init__(self):
        ClientSelectableObject.__init__(self)
        self.__state = CameraMovementStates.FROM_OBJECT

    def onEnterWorld(self, prereqs):
        ClientSelectableCameraObject.allCameraObjects.add(self)
        ClientSelectableObject.onEnterWorld(self, prereqs)

    def onLeaveWorld(self):
        if self in ClientSelectableCameraObject.allCameraObjects:
            ClientSelectableCameraObject.allCameraObjects.remove(self)

    def onMouseClick(self):
        ClientSelectableCameraObject.switchCamera(self)
        return self.state != CameraMovementStates.FROM_OBJECT

    @classmethod
    def switchCamera(cls, clickedObject=None, cameraName=None):
        if not clickedObject:
            clickedObject = cls.hangarSpace.space.getVehicleEntity()
        if clickedObject is None or clickedObject.state != CameraMovementStates.FROM_OBJECT:
            return
        else:
            cls.deselectAll()
            cameraManager = CGF.getManager(cls.hangarSpace.spaceID, HangarCameraManager)
            if cameraName is None:
                cameraManager.switchToTank(False)
            else:
                cameraManager.switchByCameraName(cameraName, False)
            clickedObject.onSelect()
            return

    @classmethod
    def deselectAll(cls):
        for cameraObject in ClientSelectableCameraObject.allCameraObjects:
            cameraObject.onDeselect()

    def onSelect(self):
        self.setEnable(False)
        self.setState(CameraMovementStates.MOVING_TO_OBJECT)
        self.setState(CameraMovementStates.ON_OBJECT)

    def onDeselect(self):
        self.setState(CameraMovementStates.FROM_OBJECT)
        self.setEnable(True)

    def setState(self, state):
        self.__state = state
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, ctx={'state': self.__state,
         'entityId': self.id}), scope=EVENT_BUS_SCOPE.DEFAULT)

    @property
    def state(self):
        return self.__state
