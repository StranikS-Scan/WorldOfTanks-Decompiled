# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/arena_component_system/sector_base_arena_component.py
from client_arena_component_system import ClientArenaComponent
import Event
from debug_utils import LOG_ERROR
ID_TO_BASENAME = {1: 'A',
 2: 'B',
 3: 'C',
 4: 'D',
 5: 'E',
 6: 'F'}
_MISSION_SECTOR_ID_MAPPING = {1: {0: 4,
     1: 4,
     2: 1},
 2: {0: 5,
     1: 5,
     2: 2},
 3: {0: 6,
     1: 6,
     2: 3}}

class SectorBaseArenaComponent(ClientArenaComponent):
    sectorBases = property(lambda self: self.__sectorBases)
    stepSectorBasePlayerAction = property(lambda self: self.__sectorBasePlayerAction)

    def __init__(self, componentSystem):
        ClientArenaComponent.__init__(self, componentSystem)
        self.__sectorBases = []
        self.__sectorBasePlayerAction = {}
        self.__baseReinforcementLvl = None
        self.onSectorBaseAdded = Event.Event(self._eventManager)
        self.onSectorBaseCaptured = Event.Event(self._eventManager)
        self.onSectorBasePointsUpdate = Event.Event(self._eventManager)
        self.onSectorBaseActiveStateChanged = Event.Event(self._eventManager)
        self.onSectorBasePlayerAction = Event.Event(self._eventManager)
        return

    def destroy(self):
        ClientArenaComponent.destroy(self)
        self.__sectorBases = []
        self.__sectorBasePlayerAction.clear()

    def addSectorBase(self, sectorBase):
        self.__sectorBases.append(sectorBase)
        self.onSectorBaseAdded(sectorBase)

    def removeSectorBase(self, sectorBase):
        self.__sectorBases.remove(sectorBase)

    def sectorBasePointsUpdated(self, sectorBase):
        self.onSectorBasePointsUpdate(sectorBase.baseID, sectorBase.isPlayerTeam(), sectorBase.capturePercentage, sectorBase.capturingStopped, sectorBase.invadersCount, sectorBase.expectedCaptureTime)

    def sectorBaseCaptured(self, sectorBase):
        self.onSectorBaseCaptured(sectorBase.baseID, sectorBase.isPlayerTeam())
        self.onSectorBaseActiveStateChanged(sectorBase.baseID, sectorBase.active())

    def sectorBaseActiveStateChanged(self, sectorBase):
        self.onSectorBaseActiveStateChanged(sectorBase.baseID, sectorBase.active())

    def getSectorBaseById(self, baseID):
        for base in self.__sectorBases:
            if base.baseID == baseID:
                return base

        return None

    def getBaseBySectorId(self, sectorID):
        for base in self.__sectorBases:
            if base.sectorID == sectorID:
                return base

        return None

    def getCapturedBaseIDs(self):
        return frozenset((base.baseID for base in self.__sectorBases if base.isCaptured))

    def getNumCapturedBases(self):
        captured = 0
        for base in self.__sectorBases:
            if base.isCaptured:
                captured += 1

        return captured

    def getNumCapturedBasesByLane(self, lane):
        captured = 0
        for base in self.__sectorBases:
            if base.isCaptured:
                sector = self.getSectorForSectorBase(base.baseID)
                if sector is not None and sector.playerGroup == lane:
                    captured += 1

        return captured

    def getNumNonCapturedBasesByLane(self, lane):
        notCaptured = 0
        for base in self.__sectorBases:
            if not base.isCaptured:
                sector = self.getSectorForSectorBase(base.baseID)
                if sector is not None and sector.playerGroup == lane:
                    notCaptured += 1

        return notCaptured

    def getNumNonCapturedActiveBasesByLane(self, lane):
        notCaptured = 0
        for base in self.__sectorBases:
            if not base.isCaptured:
                sector = self.getSectorForSectorBase(base.baseID)
                if sector is not None and sector.playerGroup == lane and base.active():
                    notCaptured += 1

        return notCaptured

    def getSectorForSectorBase(self, sectorBaseId):
        sectorComponent = self._componentSystem().arena().componentSystem.sectorComponent
        if sectorComponent is not None:
            for base in self.__sectorBases:
                if base.baseID == sectorBaseId:
                    sector = sectorComponent.getSectorById(base.sectorID)
                    return sector

        LOG_ERROR('Sector for SectorBase not found: ', sectorBaseId)
        return

    def sectorBasePlayerAction(self, sectorBaseId, action, nextActionTime):
        sectorBase = self.getSectorBaseById(sectorBaseId)
        if sectorBase.isPlayerTeam():
            return
        self.__sectorBasePlayerAction[sectorBaseId] = (action, nextActionTime)
        self.onSectorBasePlayerAction(sectorBaseId, action, nextActionTime)

    def getSectorBasePlayerAction(self, sectorBaseId):
        return self.__sectorBasePlayerAction[sectorBaseId] if sectorBaseId in self.__sectorBasePlayerAction else None

    def getNonCapturedSectorBaseIdsByLane(self, lane):
        return self.__getSectorBaseIdsByLaneAndCapturedState(lane, False)

    def getCapturedSectorBaseIdsByLane(self, lane):
        return self.__getSectorBaseIdsByLaneAndCapturedState(lane, True)

    def getDistanceToSectorBase(self, sectorBaseId, playerPosition):
        sectorBase = self.getSectorBaseById(sectorBaseId)
        if sectorBase is not None:
            distVec = sectorBase.position - playerPosition
            return distVec.length
        else:
            return 0

    def __getSectorBaseIdsByLaneAndCapturedState(self, lane, isCaptured):
        if not lane:
            return []
        else:
            ids = []
            for base in self.__sectorBases:
                sector = self.getSectorForSectorBase(base.baseID)
                if sector is not None and sector.playerGroup == lane and base.isCaptured == isCaptured:
                    ids.append(base.baseID)

            ids.sort()
            return ids
