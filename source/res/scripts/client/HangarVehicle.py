# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HangarVehicle.py
import Math
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
from gui.shared.utils.HangarSpace import g_hangarSpace

class HangarVehicle(ClientSelectableCameraVehicle):

    def __init__(self):
        self.selectionId = ''
        self.clickSoundName = ''
        self.releaseSoundName = ''
        self.mouseOverSoundName = ''
        self.edgeMode = 2
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
        self.vehicleGunPitch = 0.0
        self.vehicleTurretYaw = 0.0
        self.cameraBackwardDuration = 10.0
        self.cameraUpcomingDuration = 10.0
        super(HangarVehicle, self).__init__()
        return

    def onEnterWorld(self, prereqs):
        super(HangarVehicle, self).onEnterWorld(prereqs)
        g_hangarSpace.onSpaceCreate += self.__onSpaceCreated
        self.enable(False)
        self.setState(CameraMovementStates.ON_OBJECT)

    def onLeaveWorld(self):
        g_hangarSpace.onSpaceCreate -= self.__onSpaceCreated
        super(HangarVehicle, self).onLeaveWorld()

    def __onSpaceCreated(self):
        self.enable(False)
        self.setState(CameraMovementStates.ON_OBJECT)
        self.cameraPivot = g_hangarSpace.space.camera.pivotPosition

    def _setStartValues(self):
        pass
