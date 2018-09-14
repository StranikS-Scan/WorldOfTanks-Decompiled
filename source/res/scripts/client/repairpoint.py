# Embedded file name: scripts/client/RepairPoint.py
import BigWorld
from Math import Vector3
from debug_utils import LOG_DEBUG
from CTFManager import _CTFCheckPoint, _CTFPointFlag

class RepairPoint(BigWorld.UserDataObject, _CTFCheckPoint, _CTFPointFlag):
    _RADIUS_MODEL_NAME = 'repairPointRadiusModel'
    _FLAG_MODEL_NAME = 'repair_point_flag'
    _COLOR = 4294967295L
    _OVER_TERRAIN_HEIGHT = 0.5

    def __init__(self):
        BigWorld.UserDataObject.__init__(self)
        _CTFCheckPoint.__init__(self, self._RADIUS_MODEL_NAME)
        _CTFPointFlag.__init__(self, self._FLAG_MODEL_NAME, self.position)
        LOG_DEBUG('RepairPoint ', self.position, self.radius)
        if self.__isVisibleForCurrentArena():
            self._createTerrainSelectedArea(self.position, self.radius * 2.0, self._OVER_TERRAIN_HEIGHT, self._COLOR)
            self._createFlag()

    def __del__(self):
        _CTFCheckPoint.__del__(self)
        _CTFPointFlag.__del__(self)

    def __isVisibleForCurrentArena(self):
        arenaType = BigWorld.player().arena.arenaType
        if hasattr(arenaType, 'repairPoints'):
            repairPoints = arenaType.repairPoints
            for pt in repairPoints:
                if 'guid' not in pt:
                    continue
                if pt['guid'] == self.guid:
                    return True

        return False
