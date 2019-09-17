# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/MusicStageCameraTarget.py
import BigWorld
import Math
from helpers import dependency
from skeletons.hangar_music_stage import IMusicStageCameraObjectsManager

class MusicStageCameraTarget(BigWorld.Entity):
    _cameraObjMgr = dependency.descriptor(IMusicStageCameraObjectsManager)

    def onEnterWorld(self, prereqs):
        self._cameraObjMgr.addCameraTarget(self.cameraName, Math.Vector3(self.position))

    def onLeaveWorld(self):
        self._cameraObjMgr.removeCameraTarget(self.cameraName)
