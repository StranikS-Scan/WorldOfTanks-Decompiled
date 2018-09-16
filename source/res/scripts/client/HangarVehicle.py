# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HangarVehicle.py
import Math
from hangar_camera_common import CameraMovementStates
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
import WWISE
from gui.shared.utils.HangarSpace import g_hangarSpace

class HangarVehicle(ClientSelectableCameraVehicle):
    _SOUND_STATE_MAIN_TANK = '_main'
    _SOUND_START_MOVING_TO_MAIN = 'hangar_premium_2018_camera_fly_backward'

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

    def prerequisites(self):
        return []

    def onEnterWorld(self, prereqs):
        super(HangarVehicle, self).onEnterWorld(prereqs)
        self.enable(False)
        self.setState(CameraMovementStates.ON_OBJECT)
        WWISE.WW_setState(self._SOUND_GROUP_HANGAR_TANK_VIEW, '{}{}'.format(self._SOUND_GROUP_HANGAR_TANK_VIEW, self._SOUND_STATE_MAIN_TANK))

    def _onSpaceCreated(self):
        super(HangarVehicle, self)._onSpaceCreated()
        self.setState(CameraMovementStates.ON_OBJECT)
        self.cameraPivot = g_hangarSpace.space.camera.pivotPosition

    def _setStartValues(self):
        pass

    def _getMovingSound(self):
        return self._SOUND_START_MOVING_TO_MAIN

    def _getNextMusicState(self):
        return self._SOUND_STATE_MAIN_TANK
