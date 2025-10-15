# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/ATGMCamera.py
from VideoCamera import VideoCamera
import Math
import math_utils

class ATGMCamera(VideoCamera):
    camera = property(lambda self: self._cam)

    def __init__(self, configDataSec):
        super(ATGMCamera, self).__init__(configDataSec)
        self.position = None
        return

    def enable(self, **args):
        super(ATGMCamera, self).enable(**args)
        worldMat = Math.Matrix(self._cam.invViewMatrix)
        yawMatrix = math_utils.createRTMatrix((worldMat.yaw, worldMat.pitch, 0), worldMat.translation)
        yawMatrix.invert()
        self.setViewMatrix(yawMatrix)

    def _update(self):
        super(ATGMCamera, self)._update()
        self.__position = self.position
        self._cam.invViewProvider.a.translation = self.position

    def handleKeyEvent(self, key, isDown):
        return False
