# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/MusicStageCameraObject.py
import BigWorld
import Math
from helpers import dependency
from skeletons.hangar_music_stage import IMusicStageCameraObjectsManager
from hangar_music_stage.camera_descriptor import CameraDescriptor
_CENTRAL_CAMERA_NAME = 'Camera1'

class MusicStageCameraObject(BigWorld.Entity):
    _cameraObjMgr = dependency.descriptor(IMusicStageCameraObjectsManager)

    def onEnterWorld(self, prereqs):
        cameraDescr = CameraDescriptor(initMatrix=Math.Matrix(self.matrix), yawConstraints=Math.Vector2(self.yawConstraints), pitchConstraints=Math.Vector2(self.pitchConstraints), distanceConstraints=Math.Vector2(self.distanceConstraints), fov=self.fov, isCentered=self.cameraName == _CENTRAL_CAMERA_NAME)
        self._cameraObjMgr.addCameraDescr(self.cameraName, cameraDescr)

    def onLeaveWorld(self):
        self._cameraObjMgr.removeCameraDescr(self.cameraName)
