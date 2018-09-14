# Embedded file name: scripts/client/ClientArena.py
import Math
import BigWorld, ResMgr
import ArenaType
from items import vehicles
import constants
import cPickle, zlib
import Event
from constants import ARENA_PERIOD, ARENA_UPDATE, FLAG_STATE
from PlayerEvents import g_playerEvents
from debug_utils import *
from CTFManager import g_ctfManager
from helpers.EffectsList import FalloutDestroyEffect

class ClientArena(object):
    __onUpdate = {ARENA_UPDATE.VEHICLE_LIST: '_ClientArena__onVehicleListUpdate',
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
     ARENA_UPDATE.RESPAWN_AVAILABLE_VEHICLES: '_ClientArena__onRespawnAvailableVehicles',
     ARENA_UPDATE.RESPAWN_COOLDOWNS: '_ClientArena__onRespawnCooldowns',
     ARENA_UPDATE.RESPAWN_RANDOM_VEHICLE: '_ClientArena__onRespawnRandomVehicle',
     ARENA_UPDATE.RESPAWN_RESURRECTED: '_ClientArena__onRespawnResurrected',
     ARENA_UPDATE.FLAG_TEAMS: '_ClientArena__onFlagTeamsReceived',
     ARENA_UPDATE.FLAG_STATE_CHANGED: '_ClientArena__onFlagStateChanged',
     ARENA_UPDATE.INTERACTIVE_STATS: '_ClientArena__onInteractiveStats',
     ARENA_UPDATE.DISAPPEAR_BEFORE_RESPAWN: '_ClientArena__onDisappearVehicleBeforeRespawn',
     ARENA_UPDATE.RESOURCE_POINT_STATE_CHANGED: '_ClientArena__onResourcePointStateChanged',
     ARENA_UPDATE.OWN_VEHICLE_INSIDE_RP: '_ClientArena__onOwnVehicleInsideRP',
     ARENA_UPDATE.OWN_VEHICLE_LOCKED_FOR_RP: '_ClientArena__onOwnVehicleLockedForRP'}

    def __init__(self, arenaUniqueID, arenaTypeID, arenaBonusType, arenaGuiType, arenaExtraData, weatherPresetID):
        self.__vehicles = {}
        self.__vehicleIndexToId = {}
        self.__positions = {}
        self.__statistics = {}
        self.__periodInfo = (ARENA_PERIOD.WAITING,
         0,
         0,
         None)
        self.__eventManager = Event.EventManager()
        em = self.__eventManager
        self.onNewVehicleListReceived = Event.Event(em)
        self.onVehicleAdded = Event.Event(em)
        self.onVehicleUpdated = Event.Event(em)
        self.onPositionsUpdated = Event.Event(em)
        self.onPeriodChange = Event.Event(em)
        self.onNewStatisticsReceived = Event.Event(em)
        self.onVehicleStatisticsUpdate = Event.Event(em)
        self.onVehicleKilled = Event.Event(em)
        self.onAvatarReady = Event.Event(em)
        self.onTeamBasePointsUpdate = Event.Event(em)
        self.onTeamBaseCaptured = Event.Event(em)
        self.onTeamKiller = Event.Event(em)
        self.onCombatEquipmentUsed = Event.Event(em)
        self.onRespawnAvailableVehicles = Event.Event(em)
        self.onRespawnCooldowns = Event.Event(em)
        self.onRespawnRandomVehicle = Event.Event(em)
        self.onRespawnResurrected = Event.Event(em)
        self.onInteractiveStats = Event.Event(em)
        self.onVehicleWillRespawn = Event.Event(em)
        self.arenaUniqueID = arenaUniqueID
        self.arenaType = ArenaType.g_cache.get(arenaTypeID, None)
        if self.arenaType is None:
            LOG_ERROR('Arena ID not found ', arenaTypeID)
        self.bonusType = arenaBonusType
        self.guiType = arenaGuiType
        self.extraData = arenaExtraData
        self.__arenaBBCollider = None
        self.__spaceBBCollider = None
        return

    vehicles = property(lambda self: self.__vehicles)
    positions = property(lambda self: self.__positions)
    statistics = property(lambda self: self.__statistics)
    period = property(lambda self: self.__periodInfo[0])
    periodEndTime = property(lambda self: self.__periodInfo[1])
    periodLength = property(lambda self: self.__periodInfo[2])
    periodAdditionalInfo = property(lambda self: self.__periodInfo[3])

    def destroy(self):
        self.__eventManager.clear()

    def update(self, updateType, argStr):
        delegateName = self.__onUpdate.get(updateType, None)
        if delegateName is not None:
            getattr(self, delegateName)(argStr)
        return

    def updatePositions(self, indices, positions):
        self.__positions.clear()
        lenPos = indices and len(positions)
        lenInd = len(indices)
        if not lenPos == 2 * lenInd:
            raise AssertionError
            indexToId = self.__vehicleIndexToId
            for i in xrange(0, lenInd):
                if indices[i] in indexToId:
                    positionTuple = (positions[2 * i], 0, positions[2 * i + 1])
                    self.__positions[indexToId[indices[i]]] = positionTuple

        self.onPositionsUpdated()

    def collideWithArenaBB(self, start, end):
        if self.__arenaBBCollider is None:
            if not self.__setupBBColliders():
                return
        return self.__arenaBBCollider.collide(start, end)

    def collideWithSpaceBB(self, start, end):
        if self.__spaceBBCollider is None:
            if not self.__setupBBColliders():
                return
        return self.__spaceBBCollider.collide(start, end)

    def __setupBBColliders(self):
        if BigWorld.wg_getSpaceBounds().length == 0.0:
            return False
        arenaBB = self.arenaType.boundingBox
        spaceBB = _convertToList(BigWorld.wg_getSpaceBounds())
        self.__arenaBBCollider = _BBCollider(arenaBB, (-500.0, 500.0))
        self.__spaceBBCollider = _BBCollider(spaceBB, (-500.0, 500.0))
        return True

    def __onVehicleListUpdate(self, argStr):
        list = cPickle.loads(zlib.decompress(argStr))
        vehicles = self.__vehicles
        vehicles.clear()
        for infoAsTuple in list:
            id, info = self.__vehicleInfoAsDict(infoAsTuple)
            vehicles[id] = info

        self.__rebuildIndexToId()
        self.onNewVehicleListReceived()

    def __onVehicleAddedUpdate(self, argStr):
        infoAsTuple = cPickle.loads(zlib.decompress(argStr))
        id, info = self.__vehicleInfoAsDict(infoAsTuple)
        self.__vehicles[id] = info
        self.__rebuildIndexToId()
        self.onVehicleAdded(id)

    def __onVehicleUpdatedUpdate(self, argStr):
        infoAsTuple = cPickle.loads(zlib.decompress(argStr))
        id, info = self.__vehicleInfoAsDict(infoAsTuple)
        self.__vehicles[id] = info
        self.onVehicleUpdated(id)

    def __onPeriodInfoUpdate(self, argStr):
        self.__periodInfo = cPickle.loads(zlib.decompress(argStr))
        self.onPeriodChange(*self.__periodInfo)
        g_playerEvents.onArenaPeriodChange(*self.__periodInfo)

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
        victimID, killerID, equipmentID, reason = cPickle.loads(argStr)
        vehInfo = self.__vehicles.get(victimID, None)
        if vehInfo is not None:
            vehInfo['isAlive'] = False
            self.onVehicleKilled(victimID, killerID, equipmentID, reason)
        return

    def __onAvatarReady(self, argStr):
        vehicleID = cPickle.loads(argStr)
        vehInfo = self.__vehicles.get(vehicleID, None)
        if vehInfo is not None:
            vehInfo['isAvatarReady'] = True
            self.onAvatarReady(vehicleID)
        return

    def __onBasePointsUpdate(self, argStr):
        team, baseID, points, capturingStopped = cPickle.loads(argStr)
        self.onTeamBasePointsUpdate(team, baseID, points, capturingStopped)

    def __onBaseCaptured(self, argStr):
        team, baseID = cPickle.loads(argStr)
        self.onTeamBaseCaptured(team, baseID)

    def __onTeamKiller(self, argStr):
        vehicleID = cPickle.loads(argStr)
        vehInfo = self.__vehicles.get(vehicleID, None)
        if vehInfo is not None:
            vehInfo['isTeamKiller'] = True
            self.onTeamKiller(vehicleID)
        return

    def __onCombatEquipmentUsed(self, argStr):
        shooterID, equipmentID = cPickle.loads(argStr)
        self.onCombatEquipmentUsed(shooterID, equipmentID)

    def __onRespawnAvailableVehicles(self, argStr):
        vehsList = cPickle.loads(zlib.decompress(argStr))
        self.onRespawnAvailableVehicles(vehsList)
        LOG_TU('[RESPAWN] onRespawnAvailableVehicles', vehsList)

    def __onRespawnCooldowns(self, argStr):
        cooldowns = cPickle.loads(zlib.decompress(argStr))
        self.onRespawnCooldowns(cooldowns)

    def __onRespawnRandomVehicle(self, argStr):
        respawnInfo = cPickle.loads(zlib.decompress(argStr))
        self.onRespawnRandomVehicle(respawnInfo)

    def __onRespawnResurrected(self, argStr):
        respawnInfo = cPickle.loads(zlib.decompress(argStr))
        self.onRespawnResurrected(respawnInfo)

    def __onDisappearVehicleBeforeRespawn(self, argStr):
        vehID = cPickle.loads(argStr)
        FalloutDestroyEffect.play(vehID)
        self.onVehicleWillRespawn(vehID)

    def __onFlagTeamsReceived(self, argStr):
        data = cPickle.loads(argStr)
        LOG_DEBUG('[FLAGS] flag teams', data)
        g_ctfManager.onFlagTeamsReceived(data)

    def __onFlagStateChanged(self, argStr):
        data = cPickle.loads(argStr)
        LOG_DEBUG('[FLAGS] flag state changed', data)
        g_ctfManager.onFlagStateChanged(data)

    def __onResourcePointStateChanged(self, argStr):
        data = cPickle.loads(argStr)
        LOG_DEBUG('[RESOURCE POINTS] state changed', data)
        g_ctfManager.onResourcePointStateChanged(data)

    def __onOwnVehicleInsideRP(self, argStr):
        pointInfo = cPickle.loads(argStr)
        LOG_DEBUG('[RESOURCE POINTS] own vehicle inside point', pointInfo)
        g_ctfManager.onOwnVehicleInsideRP(pointInfo)

    def __onOwnVehicleLockedForRP(self, argStr):
        unlockTime = cPickle.loads(argStr)
        LOG_DEBUG('[RESOURCE POINTS] own vehicle is locked', unlockTime)
        g_ctfManager.onOwnVehicleLockedForRP(unlockTime)

    def __onInteractiveStats(self, argStr):
        stats = cPickle.loads(zlib.decompress(argStr))
        self.onInteractiveStats(stats)
        LOG_TU('[RESPAWN] onInteractiveStats', stats)

    def __rebuildIndexToId(self):
        vehicles = self.__vehicles
        self.__vehicleIndexToId = dict(zip(range(len(vehicles)), sorted(vehicles.keys())))

    def __vehicleInfoAsDict(self, info):
        getVehicleType = lambda cd: (None if cd is None else vehicles.VehicleDescr(compactDescr=cd))
        infoAsDict = {'vehicleType': getVehicleType(info[1]),
         'name': info[2],
         'team': info[3],
         'isAlive': info[4],
         'isAvatarReady': info[5],
         'isTeamKiller': info[6],
         'accountDBID': info[7],
         'clanAbbrev': info[8],
         'clanDBID': info[9],
         'prebattleID': info[10],
         'isPrebattleCreator': bool(info[11]),
         'forbidInBattleInvitations': bool(info[12]),
         'events': info[13],
         'igrType': info[14],
         'potapovQuestIDs': info[15]}
        return (info[0], infoAsDict)

    def __vehicleStatisticsAsDict(self, stats):
        return (stats[0], {'frags': stats[1]})


def _convertToList(vec4):
    return ((vec4.x, vec4.y), (vec4.z, vec4.w))


def _pointInBB(bottomLeft2D, upperRight2D, point3D, minMaxHeight):
    if bottomLeft2D[0] < point3D[0] < upperRight2D[0] and bottomLeft2D[1] < point3D[2] < upperRight2D[1] and minMaxHeight[0] < point3D[1] < minMaxHeight[1]:
        return True
    else:
        return False


class _BBCollider():

    def __init__(self, bb, heightLimits):
        self.__planes = list()
        self.__bb = bb
        self.__heightLimits = heightLimits
        self.__planes.append(Plane(Math.Vector3(0.0, 0.0, 1.0), bb[0][1]))
        self.__planes.append(Plane(Math.Vector3(0.0, 0.0, -1.0), -bb[1][1]))
        self.__planes.append(Plane(Math.Vector3(1.0, 0.0, 0.0), bb[0][0]))
        self.__planes.append(Plane(Math.Vector3(-1.0, 0.0, 0.0), -bb[1][0]))
        self.__planes.append(Plane(Math.Vector3(0.0, 1.0, 0.0), heightLimits[0]))
        self.__planes.append(Plane(Math.Vector3(0.0, -1.0, 0.0), -heightLimits[1]))

    def collide(self, start, end):
        if not _pointInBB(self.__bb[0], self.__bb[1], end, self.__heightLimits):
            finalPoint = None
            dist = 0
            for plane in self.__planes:
                intersecPoint = plane.intersectSegment(start, end)
                if intersecPoint:
                    tmpDist = (intersecPoint - start).length
                    if tmpDist < dist or dist == 0:
                        dist = tmpDist
                        finalPoint = intersecPoint

            if finalPoint is not None:
                return finalPoint
            else:
                return start
        return


class Plane():

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
            if t >= 0.0 and t <= 1.0:
                return a + ab.scale(t)
            return None

    def testPoint(self, point):
        if self.n.dot(point) - self.d >= 0.0:
            return True
        return False
