# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/extensions/football/cell/ArenaFootballMechanics.py
import BigWorld
from components import DynamicComponentMailbox
import PhysicsWorld
import time
from Vehicle import Vehicle
from Ball import Ball
import ArenaType
from items import vehicles
from constants import DESTRUCTIBLE_MATKIND, OBSTACLE_KIND
from math import isnan
from collections import defaultdict
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION, LOG_CODEPOINT_WARNING, LOG_DEBUG_DEV
from itertools import izip
from PhysicalObject import PhysicalObject
from HistoryLogger import HistoryLogger, isNeedToLogArena
from constants import SERVER_TICK_LENGTH
from server_constants import HIST_LOG_CONFIG, KAFKA_LOG_OPERATION_TYPE, PERIPHERY
import cPickle
import zlib
import Math
import ResMgr
from items import _xml
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from wotdecorators import noexcept
HarmMailbox = DynamicComponentMailbox('harm')

class ArenaFootballMechanics(BigWorld.ScriptComponent):

    def __init__(self):
        LOG_DEBUG_DEV('[ArenaFootballMechanics] - __init__')
        if not self.isFootballEvent():
            return
        self.__makeLocalProperties()

    def __makeLocalProperties(self):
        self.__collectorTimerID = None
        self.__vehiclesEntity = None
        self.__vehiclesDBID = None
        self.__ballEntity = None
        self.__historyLogger = None
        settings = ArenaType.g_cache[self.entity.cellTypeID].football
        points = self.__readCell(settings.cellModel)
        points = [ x + settings.cellPosition for x in points ]
        x, y, z = zip(*points)
        self.__cageBounds = (Math.Vector3(min(x), min(y), min(z)), Math.Vector3(max(x), max(y), max(z)))
        return

    def __readCell(self, fileName):
        points = list()
        rootSection = ResMgr.openSection(fileName, False)
        for name, value in _xml.getChildren(None, rootSection, 'points'):
            if name == 'point':
                points.append(value['geometry'].asVector3)

        return points

    def onCreateVehicles(self):
        if not self.isFootballEvent():
            return
        if isNeedToLogArena(self.entity.uniqueID):
            self.startAnticheatCollector()

    def reuse(self, typeID, fogOfWar, uniqueID, historyLoggingFlags, heatmapLoggingFlags, bonusType):
        if not self.isFootballEvent():
            return
        self.stopAnticheatCollector()

    def reset(self):
        if not self.isFootballEvent():
            return
        self.stopAnticheatCollector()

    def stop(self):
        if not self.isFootballEvent():
            return
        self.stopAnticheatCollector()

    def onDestroy(self):
        if not self.isFootballEvent():
            return
        self.stopAnticheatCollector()

    def onRestore(self):
        if not self.isFootballEvent():
            return
        self.__makeLocalProperties()

    def onEnteredCell(self):
        if not self.isFootballEvent():
            return
        self.__makeLocalProperties()

    def startAnticheatCollector(self):
        LOG_DEBUG_DEV('Starting anticheat collector', self.entity.uniqueID)
        if not self.isFootballEvent():
            return
        elif self.__collectorTimerID is not None:
            LOG_ERROR('Anticheat collector already started', self.entity.uniqueID)
            return
        else:
            self.__vehiclesEntity = list()
            self.__vehiclesDBID = list()
            for entity in PhysicsWorld.getWorld().enumObjects(self.entity.spaceID, 'vehicles'):
                if isinstance(entity, Vehicle):
                    self.__vehiclesEntity.append(entity)
                    self.__vehiclesDBID.append(entity.accountDBID)

            alSize = BigWorld.globalData.get('football_arenaLoggerSize', HIST_LOG_CONFIG.FOOTBALL_ARENA_LOGGER_SIZE)
            alStep = BigWorld.globalData.get('football_arenaLoggerFrequency', HIST_LOG_CONFIG.FOOTBALL_ARENA_LOGGER_FREQUENCY)
            self.__historyLogger = HistoryLogger(self.__logData, alSize, alStep, self.__cageBounds)
            self.__collectorTimerID = BigWorld.addTimer(self.__onAnticheatCollector, SERVER_TICK_LENGTH, SERVER_TICK_LENGTH)
            return

    def stopAnticheatCollector(self):
        if not self.isFootballEvent():
            return
        else:
            if self.__collectorTimerID:
                LOG_DEBUG_DEV('Stopping anticheat collector', self.entity.uniqueID)
                BigWorld.delTimer(self.__collectorTimerID)
                self.__collectorTimerID = None
                self.__historyLogger.commit()
            self.__historyLogger = None
            self.__vehiclesEntity = None
            self.__vehiclesDBID = None
            self.__ballEntity = None
            return

    def updateBallID(self, ballID):
        if not self.isFootballEvent():
            return
        else:
            self.__ballEntity = BigWorld.entities.get(ballID, None)
            return

    def __logData(self, values, bounds):
        if not HIST_LOG_CONFIG.isLogEnabled('football_anticheat_data', BigWorld.globalData):
            return
        cageMin = bounds[0]
        cageMax = bounds[1]
        cageBounds = [cageMin.x, cageMin.y, cageMin.z]
        cageBounds.extend([cageMax.x, cageMax.y, cageMax.z])
        ballPositions = list()
        positions = list()
        relAimings = list()
        worldAimings = list()
        for ball, vehicles in values:
            packVector3ToByteList(ball, ballPositions)
            for vehPosition, vehRelAiming, vehWorldAiming in vehicles:
                packVector3ToByteList(vehPosition, positions)
                packVector3ToByteList(vehRelAiming, relAimings)
                packVector3ToByteList(vehWorldAiming, worldAimings)

        arenaID = self.entity.uniqueID
        params = {'object_id': arenaID,
         'data': {'opType': KAFKA_LOG_OPERATION_TYPE.FOOTBALL_ARENA_STATES,
                  'body': {'periphery_id': PERIPHERY.ID,
                           'arena_id': arenaID,
                           'date_time': time.time(),
                           'ball': str(bytearray(ballPositions)),
                           'vehicles_id': self.__vehiclesDBID if self.__vehiclesDBID else [],
                           'positions': str(bytearray(positions)),
                           'rel_aimings': str(bytearray(relAimings)),
                           'world_aimings': str(bytearray(worldAimings)),
                           'cage_bounds': cageBounds}}}
        BigWorld.services['KafkaReliablePublisher'].publishPacked('log_football_arena_states', zlib.compress(cPickle.dumps(params, 2)))

    def __onAnticheatCollector(self, timerID, _):
        if self.__collectorTimerID is None:
            return
        else:
            vehiclesPosition = list()
            cageBounds = self.__cageBounds
            cageMin = cageBounds[0]
            cageMax = cageBounds[1]
            minX = cageMin.x
            minY = cageMin.y
            minZ = cageMin.z
            maxX = cageMax.x
            maxY = cageMax.y
            maxZ = cageMax.z
            for vehicle in self.__vehiclesEntity:
                if not vehicle.isDestroyed:
                    vehPos = vehicle.position
                    relativeAiming = vehicle.VehicleFootball.getLastRelativeAiming()
                    worldAiming = vehicle.VehicleFootball.getLastWorldAiming()
                    vehiclesPosition.append(((clamp16(vehPos[0], minX, maxX), clamp16(vehPos[1], minY, maxY), clamp16(vehPos[2], minZ, maxZ)), (clamp16(relativeAiming[0], minX, maxX), clamp16(relativeAiming[1], minY, maxY), clamp16(relativeAiming[2], minZ, maxZ)), (clamp16(worldAiming[0], minX, maxX), clamp16(worldAiming[1], minY, maxY), clamp16(worldAiming[2], minZ, maxZ))))
                vehiclesPosition.append(((0, 0, 0), (0, 0, 0), (0, 0, 0)))

            if self.__ballEntity is not None and not self.__ballEntity.isDestroyed:
                ballPosition = self.__ballEntity.position
                ballPosition = (clamp16(ballPosition[0], minX, maxX), clamp16(ballPosition[1], minY, maxY), clamp16(ballPosition[2], minZ, maxZ))
            else:
                ballPosition = (0, 0, 0)
            self.__historyLogger.append((ballPosition, vehiclesPosition))
            return

    @noexcept
    def isFootballEvent(self):
        return BONUS_CAPS.checkAny(self.entity.cellBonusType, BONUS_CAPS.FOOTBALL, BONUS_CAPS.FOOTBALL_OVERTIME_MECHANICS)


def clamp16(value, minValue, maxValue):
    return int(round((value - minValue) / (maxValue - minValue) * 65535))


def packVector3ToByteList(vector, byteList):
    byteList.extend([255 & vector[0],
     (65280 & vector[0]) >> 8,
     255 & vector[1],
     (65280 & vector[1]) >> 8,
     255 & vector[2],
     (65280 & vector[2]) >> 8])
