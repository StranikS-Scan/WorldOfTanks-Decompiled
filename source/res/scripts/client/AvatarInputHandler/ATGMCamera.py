# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/ATGMCamera.py
from VideoCamera import VideoCamera
import Math
import math_utils
from Math import Vector3
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore

def _flatCameraDirection(camera):
    direction = Math.Vector3(camera.direction)
    direction.y = 0
    if direction.length:
        direction.normalise()
    return direction


class ATGMCamera(VideoCamera):
    __settingsCore = dependency.descriptor(ISettingsCore)
    camera = property(lambda self: self._cam)

    def __init__(self, configDataSec):
        super(ATGMCamera, self).__init__(configDataSec)
        self.position = None
        return

    def setFlatWorldLookDirection(self, flatWorldDir):
        pos = self.position
        if pos is None:
            return
        else:
            d = Math.Vector3(flatWorldDir)
            d.y = 0.0
            if not d.length:
                return
            d.normalise()
            camMat = Math.Matrix()
            camMat.lookAt(pos, d, Vector3(0, 1, 0))
            camMat.invert()
            self._VideoCamera__ypr = Vector3(camMat.yaw, 0.0, 0.0)
            self._cam.invViewProvider.a = math_utils.createRTMatrix(self._VideoCamera__ypr, pos)
            return

    def enable(self, **args):
        super(ATGMCamera, self).enable(**args)
        worldMat = Math.Matrix(self._cam.invViewMatrix)
        if self.position is None:
            self.position = worldMat.translation
        flatDir = _flatCameraDirection(self.camera)
        if flatDir.length:
            self.setFlatWorldLookDirection(flatDir)
        else:
            yawMatrix = math_utils.createRTMatrix((worldMat.yaw, 0.0, 0.0), worldMat.translation)
            yawMatrix.invert()
            self.setViewMatrix(yawMatrix)
        self.__position = self.position
        return

    def _update(self):
        super(ATGMCamera, self)._update()
        if self.position is not None:
            self.__position = self.position
            self._cam.invViewProvider.a.translation = self.position
        return 0.0

    def handleKeyEvent(self, key, isDown):
        return False

    def handleMouseEvent(self, dx, dy, dz):
        settingsCore = self.__settingsCore
        if settingsCore.isReady:
            if settingsCore.getSetting('mouseHorzInvert'):
                dx = -dx
            if settingsCore.getSetting('mouseVertInvert'):
                dy = -dy
        super(ATGMCamera, self).handleMouseEvent(dx, dy, dz)
