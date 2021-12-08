# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/CameraAnchorObject.py
from collections import namedtuple
import BigWorld
import Math
from helpers import dependency
from skeletons.new_year import ICustomizableObjectsManager
CameraAnchorDescriptor = namedtuple('CameraAnchorDescriptor', ('anchorName', 'initMatrix', 'yawConstraints', 'pitchConstraints', 'distanceConstraints', 'fov', 'dofEnabled', 'dofParams', 'flightPoints'))

class CameraAnchorObject(BigWorld.Entity):
    objMgr = dependency.descriptor(ICustomizableObjectsManager)

    def prerequisites(self):
        return []

    def onEnterWorld(self, prereqs):
        anchorDescr = CameraAnchorDescriptor(self.anchorName, Math.Matrix(self.matrix), self.yawConstraints, self.pitchConstraints, self.distanceConstraints, self.fov, self.dofEnabled, (self.nearStart,
         self.nearDist,
         self.farStart,
         self.farDist), self.flightPoints)
        self.objMgr.addCameraAnchor(self.anchorName, anchorDescr)

    def onLeaveWorld(self):
        self.objMgr.removeCameraAnchor(self.anchorName)
