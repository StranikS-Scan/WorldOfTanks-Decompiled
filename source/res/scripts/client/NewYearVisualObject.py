# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearVisualObject.py
import logging
import BigWorld
import Math
import math_utils
_logger = logging.getLogger(__name__)

class OtherEntityCreator(object):

    @classmethod
    def createEntity(cls, spaceID, targetTransformMatrix, state, entityType=None):
        if entityType is None:
            entityType = cls.__name__
        m = Math.Matrix(targetTransformMatrix)
        scaleMatrix = math_utils.createRTMatrix((m.yaw, m.pitch, m.roll), m.translation)
        scaleMatrix.invert()
        scaleMatrix.preMultiply(targetTransformMatrix)
        scaleCoeffs = scaleMatrix.applyVector((1, 1, 1))
        creationState = {'scale': scaleCoeffs}
        creationState.update(state)
        entityId = BigWorld.createEntity(entityType, spaceID, 0, m.translation, (m.roll, m.pitch, m.yaw), creationState)
        return entityId

    @staticmethod
    def destroyEntity(entityId):
        if entityId in BigWorld.entities.keys():
            BigWorld.destroyEntity(entityId)
            return True
        return False


class NewYearVisualObject(BigWorld.Entity, OtherEntityCreator):

    def __init__(self):
        BigWorld.Entity.__init__(self)
        self.model = None
        self.scaleMatrix = math_utils.createSRTMatrix(self.scale, (0, 0, 0), (0, 0, 0))
        return

    def prerequisites(self):
        return [] if not self.modelName else [self.modelName]

    def onEnterWorld(self, prereqs):
        if not self.modelName:
            return
        if self.modelName in prereqs.failedIDs:
            _logger.error('Failed to load model "%s"', self.modelName)
            return
        model = prereqs[self.modelName]
        model.castsShadow = False
        self.model = model
        self.filter = BigWorld.DumbFilter()
        resultMatrix = math_utils.MatrixProviders.product(self.scaleMatrix, self.matrix)
        self.model.addMotor(BigWorld.Servo(resultMatrix))

    def onLeaveWorld(self):
        pass
