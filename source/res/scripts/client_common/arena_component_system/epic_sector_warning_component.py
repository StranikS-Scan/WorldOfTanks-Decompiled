# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/arena_component_system/epic_sector_warning_component.py
import math
import weakref
from collections import defaultdict
from functools import partial
from math import copysign
import BigWorld
import Event
from arena_component_system.client_arena_component_system import ClientArenaComponent
from epic_constants import EPIC_BATTLE_TEAM_ID
from constants import SECTOR_STATE
from coordinate_system import AXIS_ALIGNED_DIRECTION as AAD
from debug_utils import LOG_WARNING
from gui.battle_control.avatar_getter import getArena, getPlayerTeam
from helpers.CallbackDelayer import CallbackDelayer
from Math import Vector2, Vector3
from PlayerEvents import g_playerEvents
from epic_constants import SECTOR_EDGE_STATE
from battleground.BorderVisual import BorderVisual

class MAPPED_SECTOR_STATE(object):
    GOOD = 0
    BAD = 1


class WARNING_TYPE(object):
    NONE = 0
    SAFE = 1
    BOMBING = 2
    PROTECTED = 3


SECTOR_STATE_TO_MAPPED_STATE = {EPIC_BATTLE_TEAM_ID.TEAM_ATTACKER: {SECTOR_STATE.CLOSED: MAPPED_SECTOR_STATE.BAD,
                                     SECTOR_STATE.OPEN: MAPPED_SECTOR_STATE.GOOD,
                                     SECTOR_STATE.TRANSITION: MAPPED_SECTOR_STATE.GOOD,
                                     SECTOR_STATE.CAPTURED: MAPPED_SECTOR_STATE.GOOD,
                                     SECTOR_STATE.BOMBING: MAPPED_SECTOR_STATE.GOOD},
 EPIC_BATTLE_TEAM_ID.TEAM_DEFENDER: {SECTOR_STATE.CLOSED: MAPPED_SECTOR_STATE.GOOD,
                                     SECTOR_STATE.OPEN: MAPPED_SECTOR_STATE.GOOD,
                                     SECTOR_STATE.TRANSITION: MAPPED_SECTOR_STATE.BAD,
                                     SECTOR_STATE.CAPTURED: MAPPED_SECTOR_STATE.GOOD,
                                     SECTOR_STATE.BOMBING: MAPPED_SECTOR_STATE.BAD}}
ADJACENT_MAPPED_STATES_TO_EDGE_STATE = {(MAPPED_SECTOR_STATE.GOOD, MAPPED_SECTOR_STATE.GOOD): SECTOR_EDGE_STATE.NONE,
 (MAPPED_SECTOR_STATE.GOOD, MAPPED_SECTOR_STATE.BAD): SECTOR_EDGE_STATE.DANGER,
 (MAPPED_SECTOR_STATE.BAD, MAPPED_SECTOR_STATE.GOOD): SECTOR_EDGE_STATE.SAFE,
 (MAPPED_SECTOR_STATE.BAD, MAPPED_SECTOR_STATE.BAD): SECTOR_EDGE_STATE.DANGER}
MAX_NUM_NODES = 10

def makeEdgeId(a, b):
    if a is None or b is None:
        return
    else:
        return MAX_NUM_NODES * a + b if a < b else MAX_NUM_NODES * b + a


def decomposeEdgeId(edgeId):
    return (int(edgeId / MAX_NUM_NODES), edgeId % MAX_NUM_NODES)


class _SectorGroupNode(object):

    def __init__(self):
        self.neighbours = []
        self.mappedState = None
        return


class _SectorGroupEdge(object):

    def __init__(self):
        self.state = None
        self.start = None
        self.end = None
        return

    def getEdgePoints(self):
        return (self.start, self.end)


class _ProtectionZoneSetting(object):

    def __init__(self):
        self.mappedState = None
        self.geometry = None
        self.edgeState = None
        self.isActive = False
        self.team = 0
        return


class _SectorWarning(object):

    def __init__(self, warningType, targetNode):
        self.type = warningType
        self.targetSectorGroup = targetNode


class EpicSectorWarningComponent(ClientArenaComponent, CallbackDelayer):
    edges = property(lambda self: self.__edges)
    protectionZones = property(lambda self: self.__protectionZones)
    warnings = property(lambda self: self.__activeWarnings)

    def __init__(self, componentSystem):
        ClientArenaComponent.__init__(self, componentSystem)
        CallbackDelayer.__init__(self)
        self.__sectorComponent = None
        self.__playerDataComponent = None
        self.__protectionZoneComponent = None
        self.__teamId = None
        self.__nodes = None
        self.__edges = None
        self.__protectionZones = None
        self.__activeWarnings = None
        self.__transitionEndTimes = None
        self.__visual = None
        self.onShowSectorWarning = Event.Event(self._eventManager)
        self.onTransitionTimerUpdated = Event.Event(self._eventManager)
        return

    def activate(self):
        super(EpicSectorWarningComponent, self).activate()
        g_playerEvents.onAvatarReady += self.__onAvatarReady

    def deactivate(self):
        super(EpicSectorWarningComponent, self).deactivate()
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
        if self.__sectorComponent:
            self.__sectorComponent.onSectorAdded -= self.__onSectorAdded
            self.__sectorComponent.onSectorGroupUpdated -= self.__onSectorGroupUpdated
            self.__sectorComponent.onSectorGroupTransitionTimeChanged -= self.__onSectorGroupTransitionTimeChanged
            self.__sectorComponent.onPlayerSectorGroupChanged -= self.__onPlayerSectorGroupChanged
        if self.__protectionZoneComponent:
            self.__protectionZoneComponent.onProtectionZoneAdded -= self.__onProtectionZoneAdded
            self.__protectionZoneComponent.onProtectionZoneActive -= self.__onProtectionZoneActive
            self.__protectionZoneComponent.onPlayerInProtectedZoneAction -= self.__onPlayerInProtectionZone
        if self.__visual is not None:
            self.__visual.destroy()
        return

    def destroy(self):
        self.__teamId = None
        self.__nodes = None
        self.__edges = None
        self.__protectionZones = None
        self.__activeWarnings = None
        ClientArenaComponent.destroy(self)
        CallbackDelayer.destroy(self)
        return

    def getEdgeByID(self, edgeID):
        return self.__edges.get(edgeID, None)

    def getEdgeIdsByNodeId(self, nodeId):
        return map(partial(makeEdgeId, nodeId), self.__nodes[nodeId].neighbours)

    def __onAvatarReady(self):
        if self._componentSystem() is None:
            return
        else:
            self.__sectorComponent = weakref.proxy(self._componentSystem().sectorComponent)
            self.__playerDataComponent = weakref.proxy(self._componentSystem().playerDataComponent)
            self.__protectionZoneComponent = weakref.proxy(self._componentSystem().protectionZoneComponent)
            self.__teamId = getPlayerTeam()
            self.__transitionEndTimes = {}
            self.__nodes = defaultdict(_SectorGroupNode)
            self.__edges = defaultdict(_SectorGroupEdge)
            self.__protectionZones = defaultdict(_ProtectionZoneSetting)
            self.__activeWarnings = {}
            self.__visual = SectorBorderVisualisation(self)
            self.__sectorComponent.onSectorAdded += self.__onSectorAdded
            for sector in self.__sectorComponent.sectors:
                self.__onSectorAdded(sector, self.__sectorComponent.getSectorGroupById(sector.groupID))

            self.__sectorComponent.onSectorGroupUpdated += self.__onSectorGroupUpdated
            sectorGroups = self.__sectorComponent.sectorGroups
            for groupId in sectorGroups:
                group = sectorGroups[groupId]
                self.__onSectorGroupUpdated(group.id, group.state, group.center, group.getBound())

            self.__sectorComponent.onSectorGroupTransitionTimeChanged += self.__onSectorGroupTransitionTimeChanged
            self.__protectionZoneComponent.onProtectionZoneAdded += self.__onProtectionZoneAdded
            self.__protectionZoneComponent.onProtectionZoneActive += self.__onProtectionZoneActive
            for _, zone in self.__protectionZoneComponent.protectionZones.items():
                self.__onProtectionZoneAdded(zone.zoneID, zone.position, zone.bound)
                if zone.isActive:
                    self.__onProtectionZoneActive(zone.zoneID, zone.isActive)

            self.__sectorComponent.onPlayerSectorGroupChanged += self.__onPlayerSectorGroupChanged
            groupId = self.__playerDataComponent.physicalSectorGroup
            if groupId is not None:
                self.__onPlayerSectorGroupChanged(groupId, None, None, None)
            self.__protectionZoneComponent.onPlayerInProtectedZoneAction += self.__onPlayerInProtectionZone
            for _, zone in [ x for _, x in self.__protectionZoneComponent.protectionZones.items() if self.__protectionZoneComponent.isPlayerInProtectedZone(x.zoneID) ]:
                self.__onPlayerInProtectionZone(zone.zoneID, True)

            return

    def __onSectorAdded(self, sector, sectorGroup):
        groupId = sectorGroup.id
        node = self.__nodes[groupId]
        node.mappedState = SECTOR_STATE_TO_MAPPED_STATE[self.__teamId][sectorGroup.state]
        neighbours = [ neighbour for neighbour in (self.__sectorComponent.getSectorById(sectorId) for sectorId in self.__sectorComponent.getNeighbouringSectorIdsByOwnSectorId(sector.sectorID)) if neighbour.groupID != groupId ]
        for neighbour in neighbours:
            neighbourGrpId = neighbour.groupID
            if neighbourGrpId not in node.neighbours:
                node.neighbours.append(neighbourGrpId)
            neighboursOfNeighbour = self.__nodes[neighbourGrpId].neighbours
            if groupId not in neighboursOfNeighbour:
                neighboursOfNeighbour.append(groupId)
            newEdgeId = makeEdgeId(groupId, neighbourGrpId)
            edge = self.__edges[newEdgeId]
            edge.start, edge.end = self.__calcEdgeLine(groupId, neighbourGrpId)
            if edge.state is None:
                edge.state = SECTOR_EDGE_STATE.NONE
            if self.__sectorComponent.currentPlayerSectorId is not None:
                continue
            self.__showEdgeState(newEdgeId, edge, edge.state, forceUpdate=True)

        return

    def __onProtectionZoneAdded(self, zoneId, position, bound):
        zone = self.__protectionZones[zoneId]
        protectionZone = self.__protectionZoneComponent.getProtectionZoneById(zoneId)
        zone.team = protectionZone.team
        zone.geometry = (Vector2(position.x, position.z),
         bound[0],
         bound[1],
         bound[1] - bound[0])
        zone.mappedState = MAPPED_SECTOR_STATE.GOOD if self.__teamId == protectionZone.team else MAPPED_SECTOR_STATE.BAD

    def __onProtectionZoneActive(self, zoneId, isActive):
        isInZone = self.__protectionZoneComponent.isPlayerInProtectedZone(zoneId)
        self.__updateProtectionZone(zoneId, isInZone, isActive)

    def __onPlayerInProtectionZone(self, zoneId, isInZone):
        self.__updateProtectionZone(zoneId, isInZone, self.__protectionZoneComponent.isProtectionZoneActive(zoneId))

    def __updateProtectionZone(self, zoneId, isInZone, isZoneActive):
        zone = self.__protectionZones.get(zoneId, None)
        if zone is None:
            return
        else:
            if not isZoneActive:
                state = SECTOR_EDGE_STATE.NONE
            elif isInZone:
                state = ADJACENT_MAPPED_STATES_TO_EDGE_STATE[zone.mappedState, MAPPED_SECTOR_STATE.GOOD]
            else:
                state = ADJACENT_MAPPED_STATES_TO_EDGE_STATE[MAPPED_SECTOR_STATE.GOOD, zone.mappedState]
            zone.edgeState = state
            zone.isActive = isZoneActive
            self.__visual.showProtectionZone(zoneId, state, zone.team, self.protectionZones)
            return

    def __onPlayerSectorGroupChanged(self, newNodeID, *args):
        if newNodeID is None:
            return
        else:
            adjacentEdges = self.getEdgeIdsByNodeId(newNodeID)
            currentActiveWarnings = self.__activeWarnings.keys()
            for activeEdgeId in currentActiveWarnings:
                if activeEdgeId not in adjacentEdges:
                    fromId, toId = decomposeEdgeId(activeEdgeId)
                    self.__showWarning(fromId, toId, WARNING_TYPE.NONE)

            localState = self.__nodes[newNodeID].mappedState
            for edgeId, edge in self.__edges.iteritems():
                adjacentNodes = decomposeEdgeId(edgeId)
                adjacentStates = [ self.__nodes[nodeId].mappedState for nodeId in adjacentNodes ]
                if newNodeID in adjacentNodes:
                    toState = adjacentStates[1] if adjacentNodes[0] == newNodeID else adjacentStates[0]
                    self.__showEdgeState(edgeId, edge, ADJACENT_MAPPED_STATES_TO_EDGE_STATE[localState, toState])
                if MAPPED_SECTOR_STATE.BAD in adjacentStates:
                    self.__showEdgeState(edgeId, edge, ADJACENT_MAPPED_STATES_TO_EDGE_STATE[MAPPED_SECTOR_STATE.GOOD, MAPPED_SECTOR_STATE.BAD])
                self.__showEdgeState(edgeId, edge, ADJACENT_MAPPED_STATES_TO_EDGE_STATE[MAPPED_SECTOR_STATE.GOOD, MAPPED_SECTOR_STATE.GOOD])

            for neighbourId in self.__nodes[newNodeID].neighbours:
                edgeId = makeEdgeId(newNodeID, neighbourId)
                edge = self.__edges.get(edgeId, None)
                if edge and edge.state == SECTOR_EDGE_STATE.DANGER:
                    if neighbourId != 0:
                        adjacentSectorState = self.__sectorComponent.getSectorGroupById(self.__sectorComponent.getSectorById(neighbourId).groupID).state
                    else:
                        adjacentSectorState = -1
                    if adjacentSectorState in (SECTOR_STATE.BOMBING, SECTOR_STATE.TRANSITION):
                        self.__showWarning(newNodeID, neighbourId, WARNING_TYPE.BOMBING)
                    else:
                        self.__showWarning(newNodeID, neighbourId, WARNING_TYPE.PROTECTED)
                if edgeId in self.__activeWarnings:
                    self.__showWarning(newNodeID, neighbourId, WARNING_TYPE.NONE)

            return

    def __showEdgeState(self, edgeId, edge, state, forceUpdate=False):
        if forceUpdate:
            edge.state = state
            self.__visual.showSectorBorder(edgeId, edge.state, self.edges)
            return
        previousState = edge.state
        edge.state = state
        if previousState != edge.state:
            self.__visual.showSectorBorder(edgeId, edge.state, self.edges)

    def __showWarning(self, fromNodeId, toNodeId, warningType):
        edgeId = makeEdgeId(fromNodeId, toNodeId)
        previousWarning = self.__activeWarnings.get(edgeId, _SectorWarning(None, -1))
        if previousWarning.type != warningType:
            if warningType in (WARNING_TYPE.NONE, WARNING_TYPE.SAFE):
                self.__activeWarnings.pop(edgeId, None)
            else:
                self.__activeWarnings[edgeId] = _SectorWarning(warningType, toNodeId)
            self.onShowSectorWarning(edgeId, warningType, toNodeId)
        return

    def __onSectorGroupUpdated(self, groupId, state, center, bounds):
        node = self.__nodes[groupId]
        if node.mappedState is not None:
            node.mappedState = SECTOR_STATE_TO_MAPPED_STATE[self.__teamId][state]
            playerSectorId = self.__sectorComponent.currentPlayerSectorId
            if playerSectorId is not None:
                self.__onPlayerSectorGroupChanged(self.__sectorComponent.getSectorById(playerSectorId).groupID)
        else:
            LOG_WARNING('[EpicSectorWarningComponent] A Sector has been updated but not yet initialized.')
        return

    def __calcEdgeLine(self, nodeIdA, nodeIdB):
        if nodeIdA == nodeIdB:
            pass
        centerA, _, _, dimensionsA = self.__getNodeGeometry(nodeIdA)
        centerB, _, _, dimensionsB = self.__getNodeGeometry(nodeIdB)
        sectorA = sectorB = None
        sectorIdsA = [ sector.sectorID for sector in self.__sectorComponent.getSectorGroupById(nodeIdA).sectors ]
        for sectorOfB in self.__sectorComponent.getSectorGroupById(nodeIdB).sectors:
            for neighbourOfBId in self.__sectorComponent.getNeighbouringSectorIdsByOwnSectorId(sectorOfB.sectorID):
                if neighbourOfBId in sectorIdsA:
                    sectorA = self.__sectorComponent.getSectorById(neighbourOfBId)
                    sectorB = sectorOfB
                    break

        if None in (sectorA, sectorB):
            return (None, None)
        else:
            if getArena().arenaType.epicSectorGrid.mainDirection in (AAD.PLUS_Z, AAD.MINUS_Z):
                isHorizontal = sectorA.playerGroup == sectorB.playerGroup
            else:
                isHorizontal = sectorA.IDInPlayerGroup == sectorB.IDInPlayerGroup
            comparisonFunc = (lambda a, b: a.x <= b.x) if isHorizontal else (lambda a, b: a.z <= b.z)
            shortWidth, shortHeight, longWidth, longHeight, shortCenter, longCenter = (dimensionsA.x,
             dimensionsA.z,
             dimensionsB.x,
             dimensionsB.z,
             centerA,
             centerB) if comparisonFunc(dimensionsA, dimensionsB) else (dimensionsB.x,
             dimensionsB.z,
             dimensionsA.x,
             dimensionsA.z,
             centerB,
             centerA)
            if isHorizontal:
                z = longCenter.z + copysign(longHeight * 0.5, shortCenter.z - longCenter.z)
                return (Vector3(shortCenter.x - shortWidth * 0.5, 0, z), Vector3(shortCenter.x + shortWidth * 0.5, 0, z))
            x = longCenter.x + copysign(longWidth * 0.5, shortCenter.x - longCenter.x)
            return (Vector3(x, 0, shortCenter.z - shortHeight * 0.5), Vector3(x, 0, shortCenter.z + shortHeight * 0.5))

    def __getNodeGeometry(self, nodeId):
        sectorGroup = self.__sectorComponent.getSectorGroupById(nodeId)
        center = sectorGroup.center
        minBound, maxBound = sectorGroup.getBound()
        return (center,
         minBound,
         maxBound,
         maxBound - minBound)

    def __onSectorGroupTransitionTimeChanged(self, sectorGroupId, oldTime, newTime):
        self.__transitionEndTimes[sectorGroupId] = newTime
        self.__startCountdownTimer(sectorGroupId)

    def __startCountdownTimer(self, sectorGroupId):
        diffTime = math.ceil(self.__transitionEndTimes[sectorGroupId] - BigWorld.serverTime())
        if diffTime >= 0:
            self.onTransitionTimerUpdated(sectorGroupId, diffTime)
            self.delayCallback(1, self.__tick)

    def __tick(self):
        transitionTimesToDel = []
        for sectorGroupId, endTime in self.__transitionEndTimes.iteritems():
            diffTime = math.ceil(endTime - BigWorld.serverTime())
            if diffTime >= 0:
                self.onTransitionTimerUpdated(sectorGroupId, diffTime)
            self.onTransitionTimerUpdated(sectorGroupId, -1)
            transitionTimesToDel.append(sectorGroupId)

        for groupId in transitionTimesToDel:
            del self.__transitionEndTimes[groupId]

        return 1.0 if self.__transitionEndTimes else None


class SectorBorderVisualisation(object):
    _TEAM_BORDER_DIRS = {EPIC_BATTLE_TEAM_ID.TEAM_ATTACKER: (AAD.PLUS_Z,),
     EPIC_BATTLE_TEAM_ID.TEAM_DEFENDER: (AAD.MINUS_Z,)}

    def __init__(self, sectorWarningComponent):
        self.__sectorVisuals = {}
        self.__protectionVisuals = {}

    def destroy(self):
        for borderVisual in self.__sectorVisuals.values():
            borderVisual.destroy()

        for borderVisuals in self.__protectionVisuals.values():
            for borderVisual in borderVisuals:
                borderVisual.destroy()

        self.__sectorVisuals = None
        self.__protectionVisuals = None
        return

    def showSectorBorder(self, edgeId, edgeState, edges):
        border = self.__sectorVisuals.get(edgeId, None)
        if border is None:
            self.__sectorVisuals[edgeId] = border = BorderVisual()
            fromPos, toPos = edges[edgeId].getEdgePoints()
            border.create(fromPos, toPos, edgeState)
        border.showState(edgeState)
        return

    def showProtectionZone(self, zoneId, edgeState, owningTeam, protectionZones):
        borders = self.__protectionVisuals.get(zoneId, None)
        if borders is None:
            borders = []
            for borderDir in self._TEAM_BORDER_DIRS[owningTeam]:
                visual = BorderVisual()
                borders.append(visual)
                bounds = protectionZones[zoneId].geometry[1:3]
                fromPos, toPos = AAD.getBoundingBoxSegmentByDirection3D(bounds, borderDir)
                visual.create(fromPos, toPos, edgeState)

            self.__protectionVisuals[zoneId] = borders
        for border in borders:
            border.showState(edgeState)

        return
