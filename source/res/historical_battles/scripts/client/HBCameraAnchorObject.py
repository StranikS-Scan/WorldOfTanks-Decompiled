# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBCameraAnchorObject.py
from collections import namedtuple
import BigWorld
import Math
from helpers import dependency
from historical_battles.skeletons.gui.customizable_objects_manager import ICustomizableObjectsManager
CameraAnchorDescriptor = namedtuple('CameraAnchorDescriptor', ('initMatrix', 'yawConstraints', 'pitchConstraints', 'distanceConstraints', 'fov'))

class HBCameraAnchorObject(BigWorld.Entity):
    objMgr = dependency.descriptor(ICustomizableObjectsManager)

    def prerequisites(self):
        return []

    def onEnterWorld(self, prereqs):
        anchorDescr = CameraAnchorDescriptor(Math.Matrix(self.matrix), self.yawConstraints, self.pitchConstraints, self.distanceConstraints, self.fov)
        self.objMgr.addCameraAnchor(self.anchorName, anchorDescr)

    def onLeaveWorld(self):
        self.objMgr.removeCameraAnchor(self.anchorName)
