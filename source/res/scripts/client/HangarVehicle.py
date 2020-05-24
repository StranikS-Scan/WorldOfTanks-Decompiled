# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HangarVehicle.py
import Math
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events

class HangarVehicle(ClientSelectableCameraVehicle):
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        self.selectionId = ''
        self.clickSoundName = ''
        self.releaseSoundName = ''
        self.mouseOverSoundName = ''
        self.edgeMode = 0
        self.modelName = ''
        self.cameraShift = Math.Vector3(0.0, 0.0, 0.0)
        self.cameraPivot = Math.Vector3(0.0, 0.0, 0.0)
        self.cameraYaw = 0.0
        self.cameraPitch = 0.0
        self.cameraObjectAspect = 1.0
        self.enableYawLimits = False
        self.yawLimits = None
        self.pitchLimitMin = 0.0
        self.pitchLimitMax = 0.0
        self.cameraBackwardDuration = 10.0
        self.cameraUpcomingDuration = 10.0
        super(HangarVehicle, self).__init__()
        return

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

    def __onSpaceCreated(self):
        self.setEnable(False)
        self.setState(CameraMovementStates.ON_OBJECT)
        self.cameraPivot = self.hangarSpace.space.camera.pivotPosition

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
