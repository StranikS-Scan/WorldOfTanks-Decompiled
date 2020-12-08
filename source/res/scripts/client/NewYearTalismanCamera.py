# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearTalismanCamera.py
from collections import namedtuple
import BigWorld
from helpers import dependency
from skeletons.new_year import ITalismanSceneController
_CameraDescriptor = namedtuple('_CameraDescriptor', 'groupName, matrix, fov, nearStart, nearDist, farStart, farDist')

class NewYearTalismanCamera(BigWorld.Entity):
    __talismanController = dependency.descriptor(ITalismanSceneController)

    def onEnterWorld(self, _):
        descriptor = _CameraDescriptor(self.groupName, self.matrix, self.fov, self.nearStart, self.nearDist, self.farStart, self.farDist)
        self.__talismanController.cameraAdded(descriptor)
