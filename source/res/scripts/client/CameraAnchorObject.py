# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/CameraAnchorObject.py
from collections import namedtuple
import BigWorld
import Math
from helpers import dependency
from skeletons.new_year import ICustomizableObjectsManager
CameraAnchorDescriptor = namedtuple('CameraAnchorDescriptor', ('initMatrix', 'yawConstraints', 'pitchConstraints', 'distanceConstraints', 'fov'))

class CameraAnchorObject(BigWorld.Entity):
    objMgr = dependency.descriptor(ICustomizableObjectsManager)

    def prerequisites(self):
        return []

    def onEnterWorld(self, prereqs):
        anchorDescr = CameraAnchorDescriptor(Math.Matrix(self.matrix), self.yawConstraints, self.pitchConstraints, self.distanceConstraints, self.fov)
        self.objMgr.addCameraAnchor(self.anchorName, anchorDescr)

    def onLeaveWorld(self):
        self.objMgr.removeCameraAnchor(self.anchorName)
