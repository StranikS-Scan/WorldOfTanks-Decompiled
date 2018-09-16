# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/extensions/football/cell/VehicleFootball.py
import time
import BigWorld
import Math
import random
from HistoryLogger import HistoryLogger, isNeedToLogArena
from debug_utils import LOG_DEBUG, LOG_DEBUG_DEV
from constants import SERVER_TICK_LENGTH
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from server_constants import VEHICLE_STATUS, KAFKA_LOG_OPERATION_TYPE, PERIPHERY, HIST_LOG_CONFIG
from vehicle_constants import GUN_LOCK_FLAGS
from vehicle_extras import _getEquipment
import AntiCheatMetrics
from wotdecorators import noexcept

class VehicleFootball(BigWorld.ScriptComponent):

    def __init__(self):
        if not self.isFootballEvent():
            return
        LOG_DEBUG_DEV('[VehicleFootball] - CELL __init__')
        self.__registerForEvents()
        self.__makeLocalProperties()

    def getLastRelativeAiming(self):
        return None if not self.isFootballEvent() else self.__lastRelativeAiming

    def getLastWorldAiming(self):
        return None if not self.isFootballEvent() else self.__lastWorldAiming

    def __registerForEvents(self):
        vehicle = self.entity
        vehicle.onShoot += self.__onShoot
        vehicle.events.onGunReload += self.__onGunReload
        vehicle.onTrackWorldPointWithGun += self.__onTrackWorldPointWithGun
        vehicle.onTrackRelativePointWithGun += self.__onTrackRelativePointWithGun
        vehicle.onOneTickTimer += self.__onOneTickTimer

    def __unregisterForEvents(self):
        vehicle = self.entity
        vehicle.onShoot -= self.__onShoot
        vehicle.events.onGunReload -= self.__onGunReload
        vehicle.onTrackWorldPointWithGun -= self.__onTrackWorldPointWithGun
        vehicle.onTrackRelativePointWithGun -= self.__onTrackRelativePointWithGun
        vehicle.onOneTickTimer -= self.__onOneTickTimer

    def __makeLocalProperties(self):
        self.__ball = None
        self.__lastRelativeAiming = (None, None, None)
        self.__lastWorldAiming = (None, None, None)
        self.__shootHistory = HistoryLogger(self.__logShoot, 30, 1, None)
        self.__antiCheatMetricsData = dict()
        self.__antiCheatMetricsCollector = AntiCheatMetrics.AntiCheatMetricsCollector(self.__antiCheatMetricsData)
        return

    def onRestore(self):
        if not self.isFootballEvent():
            return
        self.__registerForEvents()
        self.__makeLocalProperties()

    @noexcept
    def isFootballEvent(self):
        return BONUS_CAPS.checkAny(self.entity.arenaBonusType, BONUS_CAPS.FOOTBALL, BONUS_CAPS.FOOTBALL_OVERTIME_MECHANICS)

    def __onOneTickTimer(self, onOneTickTimer):
        if not self.isFootballEvent():
            return
        self.__updateAntiCheatMetrics()

    def __onGunReload(self, vehicleEntity, isReloading):
        if not self.isFootballEvent():
            return
        if vehicleEntity.id != self.entity.id:
            return
        vehicle = self.entity
        extra = vehicle.typeDescriptor.extrasDict['lastchance']
        extra.onGunReload(vehicle, isReloading)

    def __updateAntiCheatMetrics(self):
        vehicle = self.entity
        gunRotator = vehicle._Vehicle__p['gunRotator']
        if not vehicle.isClientConnected or vehicle.status < 0 or gunRotator.isTakesAim or not gunRotator.isClientTarget or gunRotator.isFixed or gunRotator.isLocked:
            return
        else:
            clientAimPoint = gunRotator.targetPoint
            if clientAimPoint is None:
                return
            if self.__ball is None:
                return
            ball = self.__ball
            mover = self.entity.mover
            histBallPosition = ball.position - ball.velocity * (mover.physics.stabilisedMatrixLatency + SERVER_TICK_LENGTH)
            histPosition = mover.stabilisedMatrix.translation
            self.__antiCheatMetricsCollector.tick(histPosition, clientAimPoint, histBallPosition)
            return

    def onDestroy(self):
        if not self.isFootballEvent():
            return
        else:
            self.__unregisterForEvents()
            self.__shootHistory.commit()
            self.__shootHistory = None
            return

    def updateBallID(self, ballID):
        if not self.isFootballEvent():
            return
        else:
            self.__ball = BigWorld.entities.get(ballID, None)
            return

    def restrictVehicleMovement(self, position, yaw):
        if not self.isFootballEvent():
            return
        vehicle = self.entity
        if vehicle.isObserver():
            return
        vehicle.gunRotator.setTargetVehicle(0)
        vehicle._lockGun(GUN_LOCK_FLAGS.OVERTURN)
        vehicle.gunRotator._VehicleGunRotator__impl.gunPitch = 0.0
        vehicle.gunRotator._VehicleGunRotator__impl.turretYaw = 0.0
        vehicle.mover.physics.velocity = Math.Vector3(0, 0, 0)
        vehicle.mover.physics.angVelocity = Math.Vector3(0, 0, 0)
        vehicle.mover.moveWith(0)
        vehicle.repair({'healVehicle': True,
         'healCrew': True,
         'healDevices': True})
        vehicle.status = VEHICLE_STATUS.BEFORE_ARENA
        vehicle.teleportTo(position, yaw)
        self.removeAmmoOnReset()

    def removeAmmoOnReset(self):
        if not self.isFootballEvent():
            return
        vehicle = self.entity
        ammo = vehicle.ammo
        if 'clip' in vehicle.typeDescriptor.gun.tags:
            LOG_DEBUG_DEV('clip was in the descriptor')
            for ammoIdx in xrange(0, len(ammo), 2):
                vehicle.cp['clipSizeLeft'] = 0
                vehicle.updateVehicleAmmo(vehicle.ammo[ammoIdx], vehicle.ammo[ammoIdx + 1], 0, 0, 0)

            LOG_DEBUG_DEV('self.typeDescriptor.extrasDict[clipReload].stopFor(self)')
            vehicle.typeDescriptor.extrasDict['clipReload'].stopFor(vehicle)
        LOG_DEBUG_DEV('self.typeDescriptor.extrasDict[gunReload].stopFor(self)')
        vehicle.typeDescriptor.extrasDict['gunReload'].stopFor(vehicle)
        vehicle._sendAmmoStatus()
        vehicle._lockGun(GUN_LOCK_FLAGS.OVERTURN)
        vehicle._stopExtras()

    def onResetAndLock(self, position, yaw, isPreppingOT=False):
        if not self.isFootballEvent():
            return
        if isPreppingOT:
            self.entity.replenishAmmo()
        self.restrictVehicleMovement(position, yaw)
        self.entity._notifyRunningExtras('onResetVehicle')

    def allowVehicleMovement(self):
        if not self.isFootballEvent():
            return
        else:
            vehicle = self.entity
            vehicle.status = VEHICLE_STATUS.FIGHTING
            vehicle._unlockGun(GUN_LOCK_FLAGS.OVERTURN)
            LOG_DEBUG_DEV('self.__reloadGun()')
            vehicle._Vehicle__reloadGun()
            LOG_DEBUG_DEV('self.typeDescriptor.extrasDict[clipReload].startFor(self)')
            if not vehicle._isExtraRunning('clipReload'):
                vehicle.typeDescriptor.extrasDict['clipReload'].startFor(vehicle)
            LOG_DEBUG_DEV('self._updateReloadState(self.ammo, self.currentShellIndexInAmmo)')
            vehicle._updateReloadState(vehicle.ammo, vehicle.currentShellIndexInAmmo)
            vehicle = self.entity
            extrasDict = vehicle.typeDescriptor.extrasDict
            extraName = None
            if 'lightTank' in self.entity.typeDescriptor.type.tags:
                extraName = 'lastchance'
            elif 'mediumTank' in self.entity.typeDescriptor.type.tags:
                extraName = 'afterburning'
            if extraName is not None:
                extra = extrasDict[extraName]
                extraData = vehicle._extras.get(extra.index)
                if extraData is None:
                    extra.startFor(vehicle)
            return

    def onResumePlay(self):
        if not self.isFootballEvent():
            return
        self.allowVehicleMovement()
        self.entity._notifyRunningExtras('onResumePlay')

    def onFootballGoal(self, selfGoal):
        if not self.isFootballEvent():
            return
        self.entity.p['statsCollector'].onFootballGoal(selfGoal)

    def onFootballAssist(self):
        if not self.isFootballEvent():
            return
        self.entity.p['statsCollector'].onFootballAssist()

    def onBattleRunning(self, isPrematureLeave, isBattleRunning):
        if not self.isFootballEvent():
            return
        if isBattleRunning and self.entity.status == VEHICLE_STATUS.FIGHTING:
            if 'lightTank' in self.entity.typeDescriptor.type.tags:
                self.entity._addEquipment(_getEquipment('lastchance').compactDescr)
            elif 'mediumTank' in self.entity.typeDescriptor.type.tags:
                self.entity._addEquipment(_getEquipment('afterburning').compactDescr)

    def sendFinalStats(self, arenaResults):
        if not self.isFootballEvent():
            return
        LOG_DEBUG('Vehicle.VehicleFootball.sendFinalStats', self.entity.id, self.entity.arenaUniqueID)
        self.__aggregatedAimingLogger()

    def __onTrackWorldPointWithGun(self, calledID, point):
        if not self.isFootballEvent():
            return
        self.__lastWorldAiming = point

    def __onTrackRelativePointWithGun(self, calledID, point):
        if not self.isFootballEvent():
            return
        self.__lastRelativeAiming = point

    def __aggregatedAimingLogger(self):
        vehicle = self.entity
        dbid = vehicle.accountDBID
        metrics = self.__antiCheatMetricsCollector.allMetrics
        BigWorld.services['KafkaReliablePublisher'].publish('log_football_aggregated_vehicle_aiming', {'object_id': dbid,
         'data': {'opType': KAFKA_LOG_OPERATION_TYPE.FOOTBALL_VEHICLE_AIMING,
                  'body': {'account_dbid': dbid,
                           'periphery_id': PERIPHERY.ID,
                           'arena_id': vehicle.arenaUniqueID,
                           'vehicle_id': vehicle.id,
                           'team_id': vehicle.publicInfo['team'],
                           'position_similarity': metrics[0],
                           'movement_similarity_linear': metrics[1],
                           'movement_similarity': metrics[2]}}})

    def __onShoot(self):
        if not self.isFootballEvent() or not isNeedToLogArena(self.entity.arenaUniqueID):
            return
        if not self.__shootHistory.isNeedToLog():
            return
        self.__shootHistory.append(time.time())

    def __logShoot(self, values, bounds):
        if not self.isFootballEvent() or not HIST_LOG_CONFIG.isLogEnabled('football_anticheat_data', BigWorld.globalData):
            return
        dbid = self.entity.accountDBID
        BigWorld.services['KafkaReliablePublisher'].publish('log_football_vehicle_shooting', {'object_id': dbid,
         'data': {'opType': KAFKA_LOG_OPERATION_TYPE.FOOTBALL_VEHICLE_SHOOTING,
                  'body': {'account_dbid': dbid,
                           'periphery_id': PERIPHERY.ID,
                           'arena_id': self.entity.arenaUniqueID,
                           'date_time': values}}})
