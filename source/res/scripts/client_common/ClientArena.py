# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/ClientArena.py
import cPickle
import zlib
from collections import namedtuple, defaultdict
from typing import Dict
import ArenaType
import BigWorld
import CGF
import Event
import Math
import arena_component_system.client_arena_component_assembler as assembler
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from battle_modifiers_common import BattleModifiers, EXT_DATA_MODIFIERS_KEY
from constants import ARENA_PERIOD, ARENA_UPDATE
from debug_utils import LOG_DEBUG, LOG_DEBUG_DEV
from helpers.bots import preprocessBotName
from items import vehicles
from PlayerEvents import g_playerEvents
from post_progression_common import EXT_DATA_PROGRESSION_KEY, EXT_DATA_SLOT_KEY
from visual_script.misc import ASPECT
from visual_script.multi_plan_provider import makeMultiPlanProvider, CallableProviderType
TeamBaseProvider = namedtuple('TeamBaseProvider', ('points', 'invadersCnt', 'capturingStopped'))

class ClientArena(object):
    __onUpdate = {ARENA_UPDATE.SETTINGS: '_ClientArena__onArenaSettingsUpdate',
     ARENA_UPDATE.VEHICLE_LIST: '_ClientArena__onVehicleListUpdate',
     ARENA_UPDATE.VEHICLE_ADDED: '_ClientArena__onVehicleAddedUpdate',
     ARENA_UPDATE.PERIOD: '_ClientArena__onPeriodInfoUpdate',
     ARENA_UPDATE.STATISTICS: '_ClientArena__onStatisticsUpdate',
     ARENA_UPDATE.VEHICLE_STATISTICS: '_ClientArena__onVehicleStatisticsUpdate',
     ARENA_UPDATE.VEHICLE_KILLED: '_ClientArena__onVehicleKilled',
     ARENA_UPDATE.AVATAR_READY: '_ClientArena__onAvatarReady',
     ARENA_UPDATE.BASE_POINTS: '_ClientArena__onBasePointsUpdate',
     ARENA_UPDATE.BASE_CAPTURED: '_ClientArena__onBaseCaptured',
     ARENA_UPDATE.TEAM_KILLER: '_ClientArena__onTeamKiller',
     ARENA_UPDATE.VEHICLE_UPDATED: '_ClientArena__onVehicleUpdatedUpdate',
     ARENA_UPDATE.COMBAT_EQUIPMENT_USED: '_ClientArena__onCombatEquipmentUsed',
     ARENA_UPDATE.FLAG_TEAMS: '_ClientArena__onFlagTeamsReceived',
     ARENA_UPDATE.FLAG_STATE_CHANGED: '_ClientArena__onFlagStateChanged',
     ARENA_UPDATE.INTERACTIVE_STATS: '_ClientArena__onInteractiveStats',
     ARENA_UPDATE.RESOURCE_POINT_STATE_CHANGED: '_ClientArena__onResourcePointStateChanged',
     ARENA_UPDATE.OWN_VEHICLE_INSIDE_RP: '_ClientArena__onOwnVehicleInsideRP',
     ARENA_UPDATE.OWN_VEHICLE_LOCKED_FOR_RP: '_ClientArena__onOwnVehicleLockedForRP',
     ARENA_UPDATE.VIEW_POINTS: '_ClientArena__onViewPoints',
     ARENA_UPDATE.VEHICLE_RECOVERED: '_ClientArena__onVehicleRecovered',
     ARENA_UPDATE.FOG_OF_WAR: '_ClientArena__onFogOfWar',
     ARENA_UPDATE.RADAR_INFO_RECEIVED: '_ClientArena__onRadarInfoReceived',
     ARENA_UPDATE.VEHICLE_DESCR: '_ClientArena__onVehicleDescrUpdate'}
    DEFAULT_ARENA_WORLD_ID = -1

    def __init__(self, arenaUniqueID, arenaTypeID, arenaBonusType, arenaGuiType, arenaExtraData, spaceID):
        self.__vehicles = {}
        self.__vehicleIndexToId = {}
        self.__positions = {}
        self.__statistics = {}
        self.__teamBasesData = defaultdict(dict)
        self.__periodInfo = (ARENA_PERIOD.WAITING,
         0,
         0,
         None)
        self.__viewPoints = []
        self.__isFogOfWarEnabled = False
        self.__hasFogOfWarHiddenVehicles = False
        self.__arenaInfo = None
        self.__teamInfo = None
        self.__settings = {}
        self.__eventManager = Event.EventManager()
        em = self.__eventManager
        self.onArenaSettingsReceived = Event.Event(em)
        self.onNewVehicleListReceived = Event.Event(em)
        self.onVehicleAdded = Event.Event(em)
        self.onVehicleUpdated = Event.Event(em)
        self.onPositionsUpdated = Event.Event(em)
        self.onPeriodChange = Event.Event(em)
        self.onNewStatisticsReceived = Event.Event(em)
        self.onVehicleStatisticsUpdate = Event.Event(em)
        self.onVehicleKilled = Event.Event(em)
        self.onVehicleHealthChanged = Event.Event(em)
        self.onVehicleRecovered = Event.Event(em)
        self.onAvatarReady = Event.Event(em)
        self.onTeamBasePointsUpdate = Event.Event(em)
        self.onTeamBasePointsUpdateAlt = Event.Event(em)
        self.onTeamBaseCaptured = Event.Event(em)
        self.onTeamKiller = Event.Event(em)
        self.onCombatEquipmentUsed = Event.Event(em)
        self.onInteractiveStats = Event.Event(em)
        self.onGameModeSpecificStats = Event.Event(em)
        self.onViewPoints = Event.Event(em)
        self.onFogOfWarEnabled = Event.Event(em)
        self.onFogOfWarHiddenVehiclesSet = Event.Event(em)
        self.onTeamHealthPercentUpdate = Event.Event(em)
        self.onChatCommandTargetUpdate = Event.Event(em)
        self.onChatCommandTriggered = Event.Event(em)
        self.onRadarInfoReceived = Event.Event(em)
        self.onTeamInfoRegistered = Event.Event(em)
        self.onTeamInfoUnregistered = Event.Event(em)
        self.arenaUniqueID = arenaUniqueID
        self._vsePlans = makeMultiPlanProvider(ASPECT.CLIENT, CallableProviderType.ARENA, arenaBonusType)
        self.arenaType = ArenaType.g_cache.get(arenaTypeID, None)
        self.bonusType = arenaBonusType
        self.guiType = arenaGuiType
        self.extraData = arenaExtraData
        battleModifiersDescr = arenaExtraData.get('battleModifiersDescr', ()) if arenaExtraData else ()
        self.battleModifiers = BattleModifiers(battleModifiersDescr)
        self.__arenaBBCollider = None
        self.__spaceBBCollider = None
        if spaceID == 0:
            spaceID = self.DEFAULT_ARENA_WORLD_ID
        self.gameSpace = CGF.World(spaceID)
        self.componentSystem = assembler.createComponentSystem(self, self.bonusType, self.arenaType)
        return

    settings = property(lambda self: self.__settings)

    @property
    def vehicles(self):
        return self.__vehicles

    positions = property(lambda self: self.__positions)
    statistics = property(lambda self: self.__statistics)
    period = property(lambda self: self.__periodInfo[0])
    periodEndTime = property(lambda self: self.__periodInfo[1])
    periodLength = property(lambda self: self.__periodInfo[2])
    periodAdditionalInfo = property(lambda self: self.__periodInfo[3])
    viewPoints = property(lambda self: self.__viewPoints)
    isFogOfWarEnabled = property(lambda self: self.__isFogOfWarEnabled)
    hasFogOfWarHiddenVehicles = property(lambda self: self.__hasFogOfWarHiddenVehicles)
    hasObservers = property(lambda self: any(('observer' in v['vehicleType'].type.tags for v in self.__vehicles.itervalues() if v['vehicleType'] is not None)) or ARENA_BONUS_TYPE_CAPS.checkAny(self.bonusType, ARENA_BONUS_TYPE_CAPS.SSR))
    teamBasesData = property(lambda self: self.__teamBasesData)
    arenaInfo = property(lambda self: self.__arenaInfo)
    teamInfo = property(lambda self: self.__teamInfo)

    def destroy(self):
        self.__eventManager.clear()
        assembler.destroyComponentSystem(self.componentSystem)
        self._vsePlans.destroy()
        self._vsePlans = None
        return

    def update(self, updateType, argStr):
        delegateName = self.__onUpdate.get(updateType, None)
        if delegateName is not None:
            getattr(self, delegateName)(argStr)
        self.componentSystem.update(updateType, argStr)
        return

    def updatePositions(self, indices, positions):
        self.__positions.clear()
        if indices:
            lenPos = len(positions)
            lenInd = len(indices)
            indexToId = self.__vehicleIndexToId
            for i in xrange(0, lenInd):
                if indices[i] in indexToId:
                    positionTuple = (positions[2 * i], 0, positions[2 * i + 1])
                    self.__positions[indexToId[indices[i]]] = positionTuple

        self.onPositionsUpdated()

    def updateTeamHealthPercent(self, percents):
        self.onTeamHealthPercentUpdate(percents)

    def collideWithArenaBB(self, start, end):
        return None if self.__arenaBBCollider is None and not self.__setupBBColliders() else self.__arenaBBCollider.collide(start, end)

    def getArenaBB(self):
        return (None, None) if self.__arenaBBCollider is None and not self.__setupBBColliders() else (self.__arenaBBCollider.getMinBounds(), self.__arenaBBCollider.getMaxBounds())

    def getClosestPointOnArenaBB(self, point):
        return None if self.__arenaBBCollider is None and not self.__setupBBColliders() else self.__arenaBBCollider.getClosestPointOnBB(point)

    def collideWithSpaceBB(self, start, end):
        return (None, None) if self.__spaceBBCollider is None and not self.__setupBBColliders() else self.__spaceBBCollider.collide(start, end)

    def getSpaceBB(self):
        return (None, None) if self.__spaceBBCollider is None and not self.__setupBBColliders() else (self.__spaceBBCollider.getMinBounds(), self.__spaceBBCollider.getMaxBounds())

    def isPointInsideArenaBB(self, point):
        return None if self.__arenaBBCollider is None and not self.__setupBBColliders() else self.__arenaBBCollider.isPointInsideBB(point)

    def registerArenaInfo(self, arenaInfo):
        self.__arenaInfo = arenaInfo

    def unregisterArenaInfo(self, arenaInfo):
        self.__arenaInfo = None
        return

    def registerTeamInfo(self, teamInfo):
        self.__teamInfo = teamInfo
        self.onTeamInfoRegistered(teamInfo)

    def unregisterTeamInfo(self, teamInfo):
        self.__teamInfo = None
        self.onTeamInfoUnregistered(teamInfo)
        return

    def __setupBBColliders(self):
        if BigWorld.wg_getSpaceBounds().length == 0.0:
            return False
        arenaBB = self.arenaType.boundingBox
        spaceBB = self.arenaType.spaceBoundingBox
        self.__arenaBBCollider = _BBCollider(arenaBB, (-500.0, 500.0))
        self.__spaceBBCollider = _BBCollider(spaceBB, (-500.0, 500.0))
        return True

    def __onArenaSettingsUpdate(self, argStr):
        arenaSettings = cPickle.loads(argStr)
        LOG_DEBUG_DEV('__onArenaSettingsUpdate', arenaSettings)
        self.__settings = arenaSettings
        self.onArenaSettingsReceived()

    def __onVehicleListUpdate(self, argStr):
        vehiclesList = cPickle.loads(zlib.decompress(argStr))
        LOG_DEBUG_DEV('__onVehicleListUpdate', vehiclesList)
        vehs = self.__vehicles
        vehs.clear()
        for infoAsTuple in vehiclesList:
            vehID, info = self.__vehicleInfoAsDict(infoAsTuple)
            vehs[vehID] = self.__preprocessVehicleInfo(info)

        self.__rebuildIndexToId()
        self.onNewVehicleListReceived()

    def __onVehicleAddedUpdate(self, argStr):
        infoAsTuple = cPickle.loads(zlib.decompress(argStr))
        LOG_DEBUG_DEV('__onVehicleAddedUpdate', infoAsTuple)
        vehID, info = self.__vehicleInfoAsDict(infoAsTuple)
        self.__vehicles[vehID] = self.__preprocessVehicleInfo(info)
        self.__rebuildIndexToId()
        self.onVehicleAdded(vehID)

    def __onVehicleUpdatedUpdate(self, argStr):
        infoAsTuple = cPickle.loads(zlib.decompress(argStr))
        vehID, info = self.__vehicleInfoAsDict(infoAsTuple)
        self.__vehicles[vehID] = self.__preprocessVehicleInfo(info)
        self.onVehicleUpdated(vehID)

    def __onVehicleDescrUpdate(self, argStr):
        vehID, compactDescr, maxHealth = cPickle.loads(argStr)
        info = self.__vehicles[vehID]
        extVehicleTypeData = {EXT_DATA_PROGRESSION_KEY: info['vehPostProgression'],
         EXT_DATA_SLOT_KEY: info['customRoleSlotTypeId'],
         EXT_DATA_MODIFIERS_KEY: self.battleModifiers}
        self.__vehicles[vehID]['vehicleType'] = self.__getVehicleType(compactDescr, extVehicleTypeData)
        self.__vehicles[vehID]['maxHealth'] = maxHealth
        self.onVehicleUpdated(vehID)

    def __onPeriodInfoUpdate(self, argStr):
        self.__periodInfo = cPickle.loads(zlib.decompress(argStr))
        self.onPeriodChange(*self.__periodInfo)
        g_playerEvents.onArenaPeriodChange(*self.__periodInfo)

    def __onViewPoints(self, argStr):
        self.__viewPoints = cPickle.loads(zlib.decompress(argStr))
        LOG_DEBUG('[VIEW POINTS] received view points', self.__viewPoints)
        self.onViewPoints(self.__viewPoints)

    def __onFogOfWar(self, argStr):
        status = cPickle.loads(argStr)
        self.__isFogOfWarEnabled = bool(status & 1)
        self.onFogOfWarEnabled(self.__isFogOfWarEnabled)
        self.__hasFogOfWarHiddenVehicles = bool(status & 2)
        self.onFogOfWarHiddenVehiclesSet(self.__hasFogOfWarHiddenVehicles)

    def __onRadarInfoReceived(self, argStr):
        status = cPickle.loads(argStr)
        self.onRadarInfoReceived(status)

    def __onStatisticsUpdate(self, argStr):
        self.__statistics = {}
        statList = cPickle.loads(zlib.decompress(argStr))
        for s in statList:
            vehicleID, stats = self.__vehicleStatisticsAsDict(s)
            self.__statistics[vehicleID] = stats

        self.onNewStatisticsReceived()

    def __onVehicleStatisticsUpdate(self, argStr):
        vehicleID, stats = self.__vehicleStatisticsAsDict(cPickle.loads(zlib.decompress(argStr)))
        self.__statistics[vehicleID] = stats
        self.onVehicleStatisticsUpdate(vehicleID)

    def __onVehicleKilled(self, argStr):
        victimID, killerID, equipmentID, reason, numVehiclesAffected = cPickle.loads(argStr)
        vehInfo = self.__vehicles.get(victimID, None)
        if vehInfo is not None:
            vehInfo['isAlive'] = False
            self.onVehicleKilled(victimID, killerID, equipmentID, reason, numVehiclesAffected)
        return

    def __onAvatarReady(self, argStr):
        vehicleID = cPickle.loads(argStr)
        vehInfo = self.__vehicles.get(vehicleID, None)
        if vehInfo is not None:
            vehInfo['isAvatarReady'] = True
            self.onAvatarReady(vehicleID)
        if self.arenaType is not None and self._vsePlans is not None:
            self._vsePlans.load(self.arenaType.visualScript[ASPECT.CLIENT])
            self._vsePlans.start()
        return

    def loadVsePlans(self):
        self._vsePlans.load(self.arenaType.visualScript[ASPECT.CLIENT], autoStart=True)

    def __onBasePointsUpdate(self, argStr):
        team, baseID, points, timeLeft, invadersCnt, capturingStopped = cPickle.loads(argStr)
        self.onTeamBasePointsUpdate(team, baseID, points, timeLeft, invadersCnt, capturingStopped)
        teamBases = self.__teamBasesData[team]
        lastData = teamBases.get(baseID, TeamBaseProvider(0, 0, False))
        teamBases[baseID] = currData = TeamBaseProvider(points, invadersCnt, capturingStopped)
        self.onTeamBasePointsUpdateAlt(team, baseID, lastData, currData)

    def __onBaseCaptured(self, argStr):
        team, baseID = cPickle.loads(argStr)
        self.onTeamBaseCaptured(team, baseID)

    def __onTeamKiller(self, argStr):
        vehicleID, value = cPickle.loads(argStr)
        vehInfo = self.__vehicles.get(vehicleID, None)
        if vehInfo is not None:
            vehInfo['isTeamKiller'] = value
            self.onTeamKiller(vehicleID, value)
        return

    def __onCombatEquipmentUsed(self, argStr):
        shooterID, equipmentID = cPickle.loads(argStr)
        self.onCombatEquipmentUsed(shooterID, equipmentID)

    def __onVehicleRecovered(self, argStr):
        vehID = cPickle.loads(argStr)
        vehInfo = self.__vehicles.get(vehID, None)
        if vehInfo is not None and vehID != BigWorld.player().playerVehicleID:
            vehInfo['isAlive'] = False
            self.onVehicleRecovered(vehID)
        return

    def __onFlagTeamsReceived(self, argStr):
        pass

    def __onFlagStateChanged(self, argStr):
        pass

    def __onResourcePointStateChanged(self, argStr):
        pass

    def __onOwnVehicleInsideRP(self, argStr):
        pass

    def __onOwnVehicleLockedForRP(self, argStr):
        pass

    def __onInteractiveStats(self, argStr):
        stats = cPickle.loads(zlib.decompress(argStr))
        self.onInteractiveStats(stats)
        LOG_DEBUG_DEV('[RESPAWN] onInteractiveStats', stats)

    def __rebuildIndexToId(self):
        vehs = self.__vehicles
        self.__vehicleIndexToId = dict(zip(range(len(vehs)), sorted(vehs.keys())))

    def __vehicleInfoAsDict(self, info):
        extVehicleTypeData = {EXT_DATA_PROGRESSION_KEY: info[25],
         EXT_DATA_SLOT_KEY: info[26],
         EXT_DATA_MODIFIERS_KEY: self.battleModifiers}
        infoAsDict = {'vehicleType': self.__getVehicleType(info[1], extVehicleTypeData),
         'name': info[2],
         'team': info[3],
         'isAlive': info[4],
         'isAvatarReady': info[5],
         'isTeamKiller': info[6],
         'accountDBID': info[7],
         'clanAbbrev': info[8],
         'clanDBID': info[9],
         'prebattleID': int(info[10]),
         'isPrebattleCreator': bool(info[11]),
         'forbidInBattleInvitations': bool(info[12]),
         'events': info[13],
         'igrType': info[14],
         'personalMissionIDs': info[15],
         'personalMissionInfo': info[16],
         'ranked': info[17],
         'outfitCD': info[18],
         'avatarSessionID': info[19],
         'wtr': int(info[20]),
         'fakeName': info[21],
         'badges': info[22],
         'overriddenBadge': info[23],
         'maxHealth': info[24],
         'vehPostProgression': info[25],
         'customRoleSlotTypeId': info[26],
         'botDisplayStatus': info[27],
         'isClientConnected': info[28]}
        return (info[0], infoAsDict)

    def __getVehicleType(self, compactDescr, extData):
        return None if compactDescr is None else vehicles.VehicleDescr(compactDescr=compactDescr, extData=extData)

    def __vehicleStatisticsAsDict(self, stats):
        return (stats[0], {'frags': stats[1]})

    def runVsePlan(self, planName, params, key='', context=None):
        if self._vsePlans is not None:
            self._vsePlans.startPlan(planName, params, key, context)
        return

    def stopVsePlan(self, planName, key=''):
        if self._vsePlans is not None:
            self._vsePlans.stopPlan(planName, key)
        return

    def getVseContextInstance(self, contextName):
        pass

    def __preprocessVehicleInfo(self, info):
        if not info['avatarSessionID']:
            info['name'] = preprocessBotName(info['name'], self.bonusType)
        return info


def _convertToList(vec4):
    return ((vec4.x, vec4.y), (vec4.z, vec4.w))


class CollisionResult(object):
    INSIDE = 0
    INTERSECTION = 1
    OUTSIDE = 2


class _BBCollider(object):

    def __init__(self, bb, heightLimits):
        self.__min = Math.Vector3(bb[0][0], heightLimits[0], bb[0][1])
        self.__max = Math.Vector3(bb[1][0], heightLimits[1], bb[1][1])
        self.__center = Math.Vector3((self.__min + self.__max) * 0.5)
        self.__planes = list()
        self.__planes.append(Plane(Math.Vector3(0.0, 0.0, 1.0), self.__min.z))
        self.__planes.append(Plane(Math.Vector3(0.0, 0.0, -1.0), -self.__max.z))
        self.__planes.append(Plane(Math.Vector3(1.0, 0.0, 0.0), self.__min.x))
        self.__planes.append(Plane(Math.Vector3(-1.0, 0.0, 0.0), -self.__max.x))
        self.__planes.append(Plane(Math.Vector3(0.0, 1.0, 0.0), self.__min.y))
        self.__planes.append(Plane(Math.Vector3(0.0, -1.0, 0.0), -self.__max.y))

    def getMinBounds(self):
        return Math.Vector3(self.__min)

    def getMaxBounds(self):
        return Math.Vector3(self.__max)

    def isPointInsideBB(self, point3D):
        return self.__min.x <= point3D[0] <= self.__max.x and self.__min.y <= point3D[1] <= self.__max.y and self.__min.z <= point3D[2] <= self.__max.z

    def getClosestPointOnBB(self, point):
        return self._findClosestPointInside(point) if self.isPointInsideBB(point) else self._findClosestPointOutside(point)

    def _findClosestPointInside(self, point):
        nearestX = self.__min.x if point.x < self.__center.x else self.__max.x
        nearestY = self.__min.y if point.y < self.__center.y else self.__max.y
        nearestZ = self.__min.z if point.z < self.__center.z else self.__max.z
        offsetX = abs(nearestX - point.x)
        offsetY = abs(nearestY - point.y)
        offsetZ = abs(nearestZ - point.z)
        if offsetX <= offsetY and offsetX <= offsetZ:
            return Math.Vector3(nearestX, point.y, point.z)
        return Math.Vector3(point.x, nearestY, point.z) if offsetY <= offsetX and offsetY <= offsetZ else Math.Vector3(point.x, point.y, nearestZ)

    def _findClosestPointOutside(self, point):
        return Math.Vector3(self.__max.x if point.x > self.__max.x else (self.__min.x if point.x < self.__min.x else point.x), self.__max.y if point.y > self.__max.y else (self.__min.y if point.y < self.__min.y else point.y), self.__max.z if point.z > self.__max.z else (self.__min.z if point.z < self.__min.z else point.z))

    def collide(self, start, end):
        startIsInside = self.isPointInsideBB(start)
        endIsInside = self.isPointInsideBB(end)
        if startIsInside == endIsInside:
            return (CollisionResult.INSIDE if startIsInside else CollisionResult.OUTSIDE, None)
        else:
            finalPoint = None
            dist = 0
            for plane in self.__planes:
                intersecPoint = plane.intersectSegment(start, end)
                if intersecPoint:
                    tmpDist = (intersecPoint - start).length
                    if tmpDist < dist or dist == 0:
                        dist = tmpDist
                        finalPoint = intersecPoint

            return (CollisionResult.INTERSECTION, finalPoint)


class Plane(object):

    def __init__(self, n, d):
        self.n = n
        self.d = d

    def intersectSegment(self, a, b):
        ab = b - a
        normalDotDir = self.n.dot(ab)
        if normalDotDir == 0:
            return None
        else:
            t = (self.d - self.n.dot(a)) / normalDotDir
            return a + ab.scale(t) if 0.0 <= t <= 1.0 else None

    def testPoint(self, point):
        return True if self.n.dot(point) - self.d >= 0.0 else False
