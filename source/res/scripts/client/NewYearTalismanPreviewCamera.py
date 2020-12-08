# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearTalismanPreviewCamera.py
from collections import namedtuple
import BigWorld
from helpers import dependency
from skeletons.new_year import ITalismanSceneController
_PreviewCameraDescriptor = namedtuple('_PreviewCameraDescriptor', 'groupName, time, matrix, fov, nearStart, nearDist, farStart, farDist')

class NewYearTalismanPreviewCamera(BigWorld.Entity):
    __talismanController = dependency.descriptor(ITalismanSceneController)

    def onEnterWorld(self, _):
        descriptor = _PreviewCameraDescriptor(self.groupName, self.time, self.matrix, self.fov, self.nearStart, self.nearDist, self.farStart, self.farDist)
        self.__talismanController.cameraPreviewAdded(descriptor)
