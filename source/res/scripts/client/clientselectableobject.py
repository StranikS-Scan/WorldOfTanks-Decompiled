# Embedded file name: scripts/client/ClientSelectableObject.py
import BigWorld
import Math
from ModelHitTester import SegmentCollisionResult
from debug_utils import LOG_ERROR

class ClientSelectableObject(BigWorld.Entity):

    def __init__(self):
        BigWorld.Entity.__init__(self)
        self.__bspModel = BigWorld.WGBspCollisionModel()

    def prerequisites(self):
        return [self.modelName]

    def onEnterWorld(self, prereqs):
        if self.modelName not in prereqs.failedIDs:
            model = prereqs[self.modelName]
            self.model = model
            self.filter = BigWorld.DumbFilter()
            if not self.__bspModel.setModel(self.model):
                LOG_ERROR('ClientSelectableObject failed to setModel', self.modelName)

    def collideSegment(self, startPoint, endPoint, skipGun = False):
        worldToVehMatrix = Math.Matrix(self.model.matrix)
        worldToVehMatrix.invert()
        startPoint = worldToVehMatrix.applyPoint(startPoint)
        endPoint = worldToVehMatrix.applyPoint(endPoint)
        res = None
        collisions = self.__bspModel.collideSegment(startPoint, endPoint)
        if collisions is None:
            return res
        else:
            for dist, _, hitAngleCos, _ in collisions:
                if res is None or res[0] >= dist:
                    res = SegmentCollisionResult(dist, hitAngleCos, 0)

            return res
