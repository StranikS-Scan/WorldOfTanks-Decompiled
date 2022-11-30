# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearVisualObject.py
import logging
import BigWorld
import math_utils
_logger = logging.getLogger(__name__)

class NewYearVisualObject(BigWorld.Entity):

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
