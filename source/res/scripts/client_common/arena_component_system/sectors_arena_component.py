# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/arena_component_system/sectors_arena_component.py
from collections import defaultdict
from client_arena_component_system import ClientArenaComponent
import Event
from constants import SECTOR_STATE
from debug_utils import LOG_WARNING
import Math
from epic_constants import EPIC_BATTLE_TEAM_ID

class SectorGroup(object):
    id = property(lambda self: self.__id)
    center = property(lambda self: self.__center)
    numSubSectors = property(lambda self: len(self.__sectors))
    playerGroup = property(lambda self: self.__sectors[0].playerGroup)
    IDInPlayerGroup = property(lambda self: self.__sectors[0].IDInPlayerGroup)
    endOfTransitionPeriod = property(lambda self: self.__sectors[0].endOfTransitionPeriod)
    sectors = property(lambda self: self.__sectors)

    def __init__(self, sectorGroupId):
        self.__id = sectorGroupId
        self.__state = SECTOR_STATE.CLOSED
        self.__center = Math.Vector3(0, 0, 0)
        self.__sectors = []
        self.__bottomLeft = Math.Vector3(10000, 0, 100000)
        self.__upperRight = Math.Vector3(-100000, 0, -100000)
        self.__wayPoints = defaultdict(lambda : None)

    def destroy(self):
        self.__sectors = []

    def addSector(self, sector):
        self.__sectors.append(sector)
        self.updateSector(sector)

    def updateSector(self, sector):
        if self.__state is not sector.state:
            self.state = sector.state
        self.calculateSectorBoundaries()

    def calculateSectorBoundaries(self):
        self.__bottomLeft = Math.Vector3(10000, 0, 100000)
        self.__upperRight = Math.Vector3(-100000, 0, -100000)
        for sector in self.__sectors:
            self.__bottomLeft.x = min(self.__bottomLeft.x, sector.position.x - sector.lengthX * 0.5)
            self.__bottomLeft.z = min(self.__bottomLeft.z, sector.position.z - sector.lengthZ * 0.5)
            self.__upperRight.x = max(self.__upperRight.x, sector.position.x + sector.lengthX * 0.5)
            self.__upperRight.z = max(self.__upperRight.z, sector.position.z + sector.lengthZ * 0.5)

        self.__center = (self.__upperRight + self.__bottomLeft) * 0.5

    def getBound(self):
        return (self.__bottomLeft, self.__upperRight)

    def isInSector(self, position):
        return self.__bottomLeft.x <= position.x < self.__upperRight.x and self.__bottomLeft.z <= position.z < self.__upperRight.z

    def getWaypointsForTeam(self, arenaType, team):
        if self.__wayPoints[team] is None:
            self.__getWayPointsForSector(arenaType)
        return self.__wayPoints[team]

    def getClosestWayPointPosition(self, arenaType, team, position):
        wayPoints = self.getWaypointsForTeam(arenaType, team)
        if not wayPoints:
            return None
        else:
            distTuples = []
            for point in wayPoints:
                distVec = point - position
                distTuples.append((point, distVec.length))

            def getTupleKey(item):
                return item[1]

            sortedList = sorted(distTuples, key=getTupleKey)
            return sortedList[0][0] if sortedList else None

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, value):
        self.__state = value

    def __getWayPointsForSector(self, arenaType):
        self.__wayPoints.clear()
        if arenaType is None:
            return
        else:
            if hasattr(arenaType, 'sectorWayPoints'):
                sectorWayPoints = arenaType.sectorWayPoints
                for point in sectorWayPoints:
                    if self.isInSector(point['position']):
                        if self.__wayPoints.get(point['team'], None) is None:
                            self.__wayPoints[point['team']] = list()
                        self.__wayPoints[point['team']].append(point['position'])

            return


class PlayerGroup(object):
    id = property(lambda self: self.__id)
    sectors = property(lambda self: self.__sectors)

    def __init__(self, groupID):
        self.__id = groupID
        self.__sectors = {}

    def destroy(self):
        self.__sectors = {}

    def addSector(self, sector):
        self.__sectors[sector.IDInPlayerGroup] = sector.sectorID


class SectorsArenaComponent(ClientArenaComponent):
    sectors = property(lambda self: self.__sectors)
    sectorGroups = property(lambda self: self.__sectorGroups)
    playerGroups = property(lambda self: self.__playerGroups)
    currentPlayerSectorId = property(lambda self: self.__currentPlayerSectorID)

    def __init__(self, componentSystem):
        ClientArenaComponent.__init__(self, componentSystem)
        self.__sectors = []
        self.__sectorGroups = {}
        self.__playerGroups = {}
        self.__currentPlayerSectorGroupID = None
        self.__currentWayPointSector = None
        self.__currentPlayerSectorID = None
        self.__wayPointRepetitionRules = {EPIC_BATTLE_TEAM_ID.TEAM_ATTACKER: (4, 2),
         EPIC_BATTLE_TEAM_ID.TEAM_DEFENDER: (4, 2)}
        self.onSectorAdded = Event.Event(self._eventManager)
        self.onSectorTransitionTimeChanged = Event.Event(self._eventManager)
        self.onSectorGroupUpdated = Event.Event(self._eventManager)
        self.onSectorGroupTransitionTimeChanged = Event.Event(self._eventManager)
        self.onPlayerSectorGroupChanged = Event.Event(self._eventManager)
        self.onWaypointsForPlayerActivated = Event.Event(self._eventManager)
        self.onWaypointsRepetitionRulesChanged = Event.Event(self._eventManager)
        return

    def destroy(self):
        ClientArenaComponent.destroy(self)
        self.__sectors = []
        self.__sectorGroups.clear()
        self.__playerGroups.clear()

    def addSector(self, sector):
        self.__sectors.append(sector)
        sectorGroup = self.__sectorGroups.get(sector.groupID, None)
        if sectorGroup is None:
            self.__sectorGroups[sector.groupID] = sectorGroup = SectorGroup(sector.groupID)
        sectorGroup.addSector(sector)
        playerGroup = self.__playerGroups.get(sector.playerGroup, None)
        if playerGroup is None:
            self.__playerGroups[sector.playerGroup] = playerGroup = PlayerGroup(sector.playerGroup)
        playerGroup.addSector(sector)
        self.onSectorAdded(sector, sectorGroup)
        self.onSectorGroupUpdated(sectorGroup.id, sectorGroup.state, sectorGroup.center, sectorGroup.getBound())
        return

    def updateSector(self, sector, oldState=None):
        sectorGroup = self.__sectorGroups[sector.groupID]
        sectorGroup.updateSector(sector)
        self.onSectorGroupUpdated(sectorGroup.id, sectorGroup.state, sectorGroup.center, sectorGroup.getBound())
        if oldState:
            sectorWasInTransition = oldState in {SECTOR_STATE.TRANSITION, SECTOR_STATE.BOMBING}
            sectorInTransition = sectorGroup.state in {SECTOR_STATE.TRANSITION, SECTOR_STATE.BOMBING}
            if sectorInTransition or self.__currentPlayerSectorGroupID == sector.groupID:
                self.__activateWaypointsForPlayer()
            if sectorInTransition != sectorWasInTransition:
                if sectorInTransition:
                    self.updateSectorTransitionTime(sector, 0, sector.endOfTransitionPeriod)
                else:
                    self.updateSectorTransitionTime(sector, 0, 0)

    def updateSectorTransitionTime(self, sector, oldTime, newTime):
        self.onSectorTransitionTimeChanged(sector.sectorID, oldTime, newTime)
        self.onSectorGroupTransitionTimeChanged(sector.groupID, oldTime, newTime)

    def removeSector(self, sector):
        self.__sectors.remove(sector)

    def getSectorById(self, sectorID):
        for sector in self.__sectors:
            if sector.sectorID == sectorID:
                return sector

        LOG_WARNING('Requested Sector not found ', sectorID)
        return None

    def getSectorGroupById(self, sectorGroupID):
        return self.__sectorGroups[sectorGroupID]

    def getAllSectorsForPlayerGroup(self, playerGroup):
        playerGroupSectors = []
        for sector in self.__sectors:
            if sector.playerGroup == playerGroup:
                playerGroupSectors.append(sector)

        return playerGroupSectors

    def getNeighbouringSectorIdsByOwnSectorId(self, ownSectorId):
        ownSector = self.getSectorById(ownSectorId)
        values = [-1, 0, 1]
        lanes = [ self.playerGroups.get(ownSector.playerGroup + x, None) for x in values ]
        offsetsInLanes = [[0], [-1, 1], [0]]
        sectorsGroupIds = []
        for laneIdx, lane in [ item for item in enumerate(lanes) if item[1] is not None ]:
            sectorsGroupIds.extend([ sector for sector in [ lane.sectors.get(ownSector.IDInPlayerGroup + offset, None) for offset in offsetsInLanes[laneIdx] ] if sector is not None and sector != ownSectorId ])

        return sectorsGroupIds

    def getActiveWaypointSectorGroupForPlayer(self):
        if self.__currentPlayerSectorGroupID is None:
            return (None, None, 0)
        else:
            playerSector = self.getSectorById(self.__currentPlayerSectorID)
            if playerSector is None:
                return (None, None, 0)
            affectedSectorGroup, transitionSectorID, transitionEndTime = self.getActiveWaypointSectorGroupForPlayerGroup(playerSector.playerGroup)
            return (None, None, transitionEndTime) if playerSector.state not in {SECTOR_STATE.TRANSITION, SECTOR_STATE.CAPTURED} else (affectedSectorGroup, transitionSectorID, transitionEndTime)

    def getActiveWaypointSectorGroupForPlayerGroup(self, playerGroupID):
        transitionSector = next((sector for sector in self.getAllSectorsForPlayerGroup(playerGroupID) if sector.state == SECTOR_STATE.TRANSITION), None)
        return (None, None, 0) if transitionSector is None else (self.getSectorGroupById(transitionSector.groupID), transitionSector.sectorID, transitionSector.endOfTransitionPeriod)

    def getClosestWayPointForSectorAndTeam(self, sectorID, arenaType, teamID, position):
        waypointSector = self.getSectorById(sectorID)
        if teamID == EPIC_BATTLE_TEAM_ID.TEAM_DEFENDER:
            sectorsInCurrentPlayerGroup = self.__playerGroups[waypointSector.playerGroup].sectors
            waypointSector = self.getSectorById(sectorsInCurrentPlayerGroup[min(waypointSector.IDInPlayerGroup + 1, len(sectorsInCurrentPlayerGroup))])
        return self.getSectorGroupById(waypointSector.groupID).getClosestWayPointPosition(arenaType, teamID, position)

    def playerSectorGroupChanged(self, newSectorGroupID, isAllowed, oldSectorGroupID, wasAllowed, physicalSector):
        self.__currentPlayerSectorGroupID = newSectorGroupID
        self.__currentPlayerSectorID = physicalSector
        self.onPlayerSectorGroupChanged(newSectorGroupID, isAllowed, oldSectorGroupID, wasAllowed)
        self.__activateWaypointsForPlayer()

    def __activateWaypointsForPlayer(self):
        waypointSectorTimeTuple = self.getActiveWaypointSectorGroupForPlayer()
        if waypointSectorTimeTuple != self.__currentWayPointSector:
            self.__currentWayPointSector = waypointSectorTimeTuple
            self.onWaypointsForPlayerActivated(waypointSectorTimeTuple)

    def getWayPointBorderMarkerRepetitionRules(self, team):
        return self.__wayPointRepetitionRules[team]

    def setWayPointBorderMarkerRepetitionRules(self, teamID, rule):
        self.__wayPointRepetitionRules[teamID] = rule
        self.onWaypointsRepetitionRulesChanged()
