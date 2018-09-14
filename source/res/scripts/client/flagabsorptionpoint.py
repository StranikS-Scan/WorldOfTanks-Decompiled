# Embedded file name: scripts/client/FlagAbsorptionPoint.py
import BigWorld
from Math import Vector3
from debug_utils import LOG_DEBUG
from CTFManager import _CTFCheckPoint, _CTFPointFlag

class FlagAbsorptionPoint(BigWorld.UserDataObject, _CTFCheckPoint, _CTFPointFlag):
    _RADIUS_MODEL_NAME = 'absorptionPointRadiusModel'
    _FRIEND = True
    _ENEMY = False
    _TEAM_PARAMS = {_FRIEND: ('absorption_point_flag_green', 4278255360L),
     _ENEMY: ('absorption_point_flag_red', 4294901760L)}
    _OVER_TERRAIN_HEIGHT = 0.5

    def __init__(self):
        BigWorld.UserDataObject.__init__(self)
        _CTFCheckPoint.__init__(self, self._RADIUS_MODEL_NAME)
        LOG_DEBUG('FlagAbsorptionPoint ', self.position, self.radius, self.team)
        teamParams = self._TEAM_PARAMS[BigWorld.player().team == self.team]
        flagModelName = teamParams[0]
        color = teamParams[1]
        _CTFPointFlag.__init__(self, flagModelName, self.position)
        if self.__isVisibleForCurrentArena():
            self._createTerrainSelectedArea(self.position, self.radius * 2.0, self._OVER_TERRAIN_HEIGHT, color)
            self._createFlag()

    def __del__(self):
        _CTFCheckPoint.__del__(self)
        _CTFPointFlag.__del__(self)

    def __isVisibleForCurrentArena(self):
        arenaType = BigWorld.player().arena.arenaType
        if hasattr(arenaType, 'flagAbsorptionPoints'):
            flagAbsorptionPoints = arenaType.flagAbsorptionPoints
            for pt in flagAbsorptionPoints:
                if 'position' not in pt:
                    continue
                distSq = (Vector3(pt['position']) - self.position).lengthSquared
                if distSq < 100:
                    return True

        return False
