# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DualAccuracy.py
import BigWorld
from DualAccuracyBase import DualAccuracyBase

class DualAccuracy(DualAccuracyBase):

    def __init__(self):
        super(DualAccuracy, self).__init__()
        self.__coolingEndTime = 0.0

    def getGunCoolingLeftTime(self):
        curTime = BigWorld.time()
        endTime = self.__coolingEndTime
        return 0.0 if endTime <= curTime else float(endTime - curTime)

    def onCoolingDataUpdated(self, coolingTime):
        self.__coolingEndTime = BigWorld.time() + coolingTime
        self.updateDualAccuracyData()
