# Embedded file name: scripts/client/ResourcePoint.py
import BigWorld
from debug_utils import LOG_DEBUG
from CTFManager import _CTFCheckPoint, _CTFResourcePointModel, _UDOAttributeChecker

class ResourcePoint(BigWorld.UserDataObject, _CTFCheckPoint, _CTFResourcePointModel, _UDOAttributeChecker):
    _COLOR = 4294967295L
    _OVER_TERRAIN_HEIGHT = 0.5

    def __init__(self):
        BigWorld.UserDataObject.__init__(self)
        _UDOAttributeChecker.__init__(self)
        self.__isVisible = self.__isVisibleForCurrentArena()
        if not self.__isVisible:
            return
        self.checkAttribute('radiusModel')
        self.checkAttribute('pointModel')
        self.checkAttribute('pointEffect')
        LOG_DEBUG('ResourcePoint ', self.guid, self.position, self.radius, self.team)
        _CTFCheckPoint.__init__(self, self.radiusModel)
        _CTFResourcePointModel.__init__(self, self.pointModel, self.pointEffect)
        self._createTerrainSelectedArea(self.position, self.radius * 2.0, self._OVER_TERRAIN_HEIGHT, self._COLOR)
        self._createPoint()

    def __del__(self):
        if self.isAttrCheckFailed:
            return
        if not self.__isVisible:
            return
        _CTFResourcePointModel.__del__(self)
        _CTFCheckPoint.__del__(self)

    def __isVisibleForCurrentArena(self):
        arenaType = BigWorld.player().arena.arenaType
        if hasattr(arenaType, 'resourcePoints'):
            resourcePoints = arenaType.resourcePoints
            for rp in resourcePoints:
                if 'guid' not in rp:
                    continue
                guid = rp['guid']
                if guid == self.guid:
                    return True

        return False
