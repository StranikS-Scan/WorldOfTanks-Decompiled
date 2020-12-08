# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/CameraTarget.py
import BigWorld
import Math
from helpers import dependency
from skeletons.new_year import ICustomizableObjectsManager

class CameraTarget(BigWorld.Entity):
    _objMgr = dependency.descriptor(ICustomizableObjectsManager)

    def onEnterWorld(self, prereqs):
        self._objMgr.addCameraTarget(self.anchorName, Math.Vector3(self.position))

    def onLeaveWorld(self):
        self._objMgr.removeCameraTarget(self.anchorName)
