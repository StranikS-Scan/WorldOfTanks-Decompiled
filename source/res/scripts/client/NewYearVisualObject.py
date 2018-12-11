# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearVisualObject.py
import logging
import BigWorld
import Math
_logger = logging.getLogger(__name__)

class OtherEntityCreator(object):

    @classmethod
    def createEntity(cls, spaceID, targetTransformMatrix, state, entityType=None):
        if entityType is None:
            entityType = cls.__name__
        m = Math.Matrix(targetTransformMatrix)
        entityId = BigWorld.createEntity(entityType, spaceID, 0, m.translation, (m.roll, m.pitch, m.yaw), state)
        return entityId

    @staticmethod
    def destroyEntity(entityId):
        if entityId in BigWorld.entities.keys():
            BigWorld.destroyEntity(entityId)
            return True
        return False


class NewYearVisualObject(BigWorld.Entity, OtherEntityCreator):

    def __init__(self):
        super(NewYearVisualObject, self).__init__()
        self.model = None
        return

    def prerequisites(self):
        return [] if not self.modelName else [self.modelName]

    def onEnterWorld(self, prereqs):
        if not self.modelName:
            return
        if self.modelName in prereqs.failedIDs:
            _logger.error('Failed to load model "%s"', self.modelName)
            return
        self.model = prereqs[self.modelName]
        self.filter = BigWorld.DumbFilter()
        self.model.addMotor(BigWorld.Servo(self.matrix))

    def onLeaveWorld(self):
        pass
