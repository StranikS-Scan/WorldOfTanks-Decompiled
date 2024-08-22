# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/battleground/simulation_movement_tracker.py
import itertools
from collections import namedtuple, deque
import BigWorld
import logging
from aih_constants import CTRL_MODE_NAME
from constants import ARENA_PERIOD
from gun_rotation_shared import decodeGunAngles
from helpers import isPlayerAvatar
from helpers.CallbackDelayer import CallbackDelayer
from PlayerEvents import g_playerEvents
_logger = logging.getLogger(__name__)
SimulationMovementData = namedtuple('SimulationMovementData', ['duration',
 'position',
 'direction',
 'turretYaw',
 'gunPitch',
 'trackState'])
ShotMapData = namedtuple('ShotMapData', ['dataID', 'lastDuration'])

class SimulationMovementTracker(CallbackDelayer):
    __MAX_TIME_TILL_DEATH = 60.0
    __PENDING_SHOT_ID = 'pending'

    def __init__(self, tickDelay, snapshotLength):
        CallbackDelayer.__init__(self)
        self.__isTrackingActive = False
        self.__tickDelay = tickDelay
        self.__snapshotLength = snapshotLength
        self.__maxDataPoints = self.__MAX_TIME_TILL_DEATH / self.__tickDelay
        self.__data = deque()
        self.__lastPointTime = 0.0
        self.__snapshots = {}
        self.__shotsMap = {}
        self.__snapshotsMap = {}
        self.__pointsCaptured = 0
        self.__isStartRequested = False
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange

    def create(self):
        self.start()

    def destroy(self):
        self.__isStartRequested = False
        self.stop()
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        CallbackDelayer.destroy(self)

    def start(self):
        if not BigWorld.player().isPostmortemFeatureEnabled(CTRL_MODE_NAME.KILL_CAM):
            return
        if not self.__isStartRequested:
            self.__isStartRequested = True
            return
        self.__data.clear()
        self.__snapshots.clear()
        self.stopCallback(self.__tick)
        self.__lastPointTime = BigWorld.serverTime()
        self.delayCallback(self.__tickDelay, self.__tick)
        self.__isTrackingActive = True
        g_playerEvents.onTracerReceived += self.__onTracerReceived

    def stop(self):
        g_playerEvents.onTracerReceived -= self.__onTracerReceived
        self.__isTrackingActive = False
        self.stopCallback(self.__tick)

    def getData(self, shotID):
        shotData = self.getSnapshot(shotID, False)
        killData = self.getSnapshot(shotID, True)
        return (shotData if shotData[0] else killData, killData if killData[0] else shotData)

    def getSnapshot(self, shotID, isKill):
        snapshotID = self.__makeSnapshotID(shotID, isKill)
        shotData = self.__shotsMap.get(snapshotID, None)
        if not shotData:
            _logger.info('SimulationMovementTracker.getSnapshot: Cannot get movement data for shot "%s"', snapshotID)
            return ([], 0.0)
        dataID = shotData.dataID
        lastDuration = shotData.lastDuration
        data = self.__snapshots.get(dataID, None)
        if not data:
            _logger.info('SimulationMovementTracker.getSnapshot: Cannot find data snapshot for shot "%s"', snapshotID)
            return ([], 0.0)
        else:
            return (data[:], lastDuration)

    def saveSnapshot(self, shotID=0, isKill=False):
        if not self.__isTrackingActive:
            return
        dataLength = len(self.__data)
        if not dataLength:
            return
        snapshotID = self.__makeSnapshotID(shotID, isKill)
        if not snapshotID:
            _logger.error('saveSnapshot: Cannot make snapshotID for shotID: "%s" (isKill: %s)', shotID, isKill)
            return
        snapshotData = list(itertools.islice(self.__data, max(0, dataLength - self.__snapshotLength), dataLength))
        self.__data = deque(snapshotData)
        self.__shotsMap[snapshotID] = ShotMapData(self.__pointsCaptured, BigWorld.serverTime() - self.__lastPointTime)
        if self.__pointsCaptured not in self.__snapshotsMap:
            self.__snapshotsMap[self.__pointsCaptured] = []
        self.__snapshotsMap[self.__pointsCaptured].append(snapshotID)
        if self.__pointsCaptured in self.__snapshots:
            return
        self.__snapshots[self.__pointsCaptured] = snapshotData

    def clearSnapshot(self, shotID, isKill=None):
        if isKill is None:
            self.clearSnapshot(shotID, False)
            self.clearSnapshot(shotID, True)
            return
        else:
            snapshotID = self.__makeSnapshotID(shotID, isKill)
            shotData = self.__shotsMap.get(snapshotID, None)
            if not shotData:
                return
            dataID = shotData.dataID
            self.__snapshotsMap[dataID].remove(snapshotID)
            del self.__shotsMap[snapshotID]
            if not self.__snapshotsMap[dataID]:
                del self.__snapshots[dataID]
                del self.__snapshotsMap[dataID]
            return

    def setPendingShotID(self, shotID):
        if not self.__isTrackingActive:
            return
        elif not shotID:
            _logger.error('setPendingShotID: Should always have shotID at this point!')
            self.clearSnapshot(self.__PENDING_SHOT_ID)
            return
        else:
            pendingID = self.__makeSnapshotID(self.__PENDING_SHOT_ID, isKill=True)
            shotData = self.__shotsMap.get(pendingID, None)
            if not shotData:
                _logger.error('setPendingShotID: Cannot find shot data for "%s"', pendingID)
                return
            snapshotID = self.__makeSnapshotID(shotID, True)
            dataID = shotData.dataID
            self.__shotsMap[snapshotID] = shotData
            self.__snapshotsMap[dataID].append(snapshotID)
            self.clearSnapshot(self.__PENDING_SHOT_ID, True)
            return

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == ARENA_PERIOD.BATTLE:
            self.start()
        else:
            self.stop()

    def __onTracerReceived(self, shotID):
        self.saveSnapshot(shotID, isKill=False)

    @staticmethod
    def __makeSnapshotID(shotID, isKill):
        if not shotID and isKill:
            shotID = SimulationMovementTracker.__PENDING_SHOT_ID
        return None if not shotID else '{0}_{1}'.format(shotID, 'kill' if isKill else 'shot')

    def __tick(self):
        player = BigWorld.player()
        currentTime = BigWorld.serverTime()
        if not player or not isPlayerAvatar():
            self.__lastPointTime = currentTime
            return self.__tickDelay
        vehicles = player.vehicles
        data = {}
        for vehicle in vehicles:
            if not vehicle or vehicle.isDestroyed or not vehicle.isStarted or not vehicle.isAlive():
                continue
            turretYaw, gunPitch = self.__getGunAngles(vehicle)
            trackStates = vehicle.appearance.getTrackStates()
            data[vehicle.id] = SimulationMovementData(currentTime - self.__lastPointTime, vehicle.position, (vehicle.roll, vehicle.pitch, vehicle.yaw), turretYaw, gunPitch, trackStates)

        self.__lastPointTime = currentTime
        self.__data.append(data)
        if len(self.__data) > self.__maxDataPoints:
            self.__data.popleft()
        if self.__pointsCaptured >= self.__maxDataPoints:
            self.__cleanupSnapshots()
        self.__pointsCaptured += 1
        return self.__tickDelay

    def __cleanupSnapshots(self):
        cleanupSnapshotID = self.__pointsCaptured - self.__maxDataPoints
        if cleanupSnapshotID not in self.__snapshotsMap:
            return
        shots = self.__snapshotsMap[cleanupSnapshotID]
        for shotID in shots:
            self.clearSnapshot(shotID, False)

        del self.__snapshotsMap[cleanupSnapshotID]

    @staticmethod
    def __getGunAngles(veh):
        if veh.typeDescriptor:
            turretYaw, gunPitch = decodeGunAngles(veh.gunAnglesPacked, veh.typeDescriptor.gun.pitchLimits['absolute'])
        else:
            turretYaw = gunPitch = 0.0
        return (turretYaw, gunPitch)
