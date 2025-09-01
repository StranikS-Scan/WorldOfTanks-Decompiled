# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/skeletons/white_tiger_spawn_listener.py
from enum import IntEnum

class SpawnType(IntEnum):
    DEFAULT = 1
    TELEPORT = 2


class ISpawnListener(object):

    def setSpawnPoints(self, points, pointId=None):
        pass

    def showSpawnPoints(self):
        pass

    def closeSpawnPoints(self):
        pass

    def updatePoint(self, vehicleId, pointId, prevPointId):
        pass

    def updateCloseTime(self, timeLeft, state):
        pass

    def onSelectPoint(self, pointId):
        pass

    def setSpawnType(self, spawnType):
        pass
