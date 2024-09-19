# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HangarVehicle.py
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates, CameraDistanceModes
from ClientSelectableCameraObject import ClientSelectableCameraObject
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
from helpers import dependency
from skeletons.gui.game_control import IEventBattlesController
from skeletons.gui.shared.utils import IHangarSpace
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events

class HangarVehicle(ClientSelectableCameraVehicle):
    hangarSpace = dependency.descriptor(IHangarSpace)
    eventBattlesCtrl = dependency.descriptor(IEventBattlesController)

    def __init__(self):
        self.selectionId = ''
        self.clickSoundName = ''
        self.releaseSoundName = ''
        self.mouseOverSoundName = ''
        self.edgeMode = 0
        self.modelName = ''
        super(HangarVehicle, self).__init__()
        self.camDistState = CameraDistanceModes.CUSTOM

    def onEnterWorld(self, prereqs):
        super(HangarVehicle, self).onEnterWorld(prereqs)
        self.hangarSpace.onSpaceCreate += self.__onSpaceCreated
        g_eventBus.addListener(events.HangarCustomizationEvent.CHANGE_VEHICLE_MODEL_TRANSFORM, self.__changeVehicleModelTransform, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.HangarCustomizationEvent.RESET_VEHICLE_MODEL_TRANSFORM, self.__resetVehicleModelTransform, scope=EVENT_BUS_SCOPE.LOBBY)
        self.setEnable(False)
        self.setState(CameraMovementStates.ON_OBJECT)

    def onLeaveWorld(self):
        self.hangarSpace.onSpaceCreate -= self.__onSpaceCreated
        g_eventBus.removeListener(events.HangarCustomizationEvent.CHANGE_VEHICLE_MODEL_TRANSFORM, self.__changeVehicleModelTransform, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.HangarCustomizationEvent.RESET_VEHICLE_MODEL_TRANSFORM, self.__resetVehicleModelTransform, scope=EVENT_BUS_SCOPE.LOBBY)
        super(HangarVehicle, self).onLeaveWorld()

    def onMouseClick(self):
        if self.eventBattlesCtrl.isAvailable() and self.eventBattlesCtrl.isEventPrbActive():
            self.eventBattlesCtrl.doLeaveEventPrb()
        return super(HangarVehicle, self).onMouseClick()

    def __onSpaceCreated(self):
        for cameraObject in ClientSelectableCameraObject.allCameraObjects:
            if cameraObject.state != CameraMovementStates.FROM_OBJECT:
                return

        self.setEnable(False)
        self.setState(CameraMovementStates.ON_OBJECT)

    def _setStartValues(self):
        pass

    def __changeVehicleModelTransform(self, event):
        ctx = event.ctx
        targetPos = ctx['targetPos']
        rotateYPR = ctx['rotateYPR']
        shadowYOffset = ctx['shadowYOffset']
        self._setVehicleModelTransform(targetPos, rotateYPR, shadowYOffset)

    def __resetVehicleModelTransform(self, event):
        self._resetVehicleModelTransform()
