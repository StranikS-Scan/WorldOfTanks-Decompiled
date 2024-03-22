# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/KillCamDataComponent.py
import logging
import BigWorld
import Math
from avatar_components.avatar_postmortem_component import SimulatedVehicleType
from constants import KILL_CAM_STATUS_CODE, BATTLE_LOG_SHELL_TYPES
from gun_rotation_shared import decodeGunAngles
from items.vehicles import getItemByCompactDescr
_logger = logging.getLogger(__name__)

class KillCamDataComponent(BigWorld.DynamicScriptComponent):

    def __init__(self):
        super(KillCamDataComponent, self).__init__()
        self.processedData = None
        return

    def set_capturedKillCamData(self, _=None):
        self.__updateSimulationData()

    def getSimulationData(self):
        self.__updateLateAttackerData()
        return self.processedData

    def __updateSimulationData(self):
        statusCode = self.capturedKillCamData['statusCode']
        if statusCode != KILL_CAM_STATUS_CODE.SUCCESS:
            _logger.debug('Data from server were not received, error reason %s', KILL_CAM_STATUS_CODE(statusCode).name)
            return
        avatar = BigWorld.player()
        vehicles = avatar.vehicles
        self.__captureKillCamSimulationData(vehicles, avatar.playerVehicleID)

    def __captureKillCamSimulationData(self, vehicles, playerID):
        playerData = self.__captureVehSimulationData(BigWorld.entity(playerID))
        if not playerData:
            return None
        else:
            serverKillCamData = self.capturedKillCamData
            attackerID = serverKillCamData['attacker']['attackerID']
            playerServerData = serverKillCamData['victim']
            playerData.update(playerServerData)
            playerData['simulationType'] = SimulatedVehicleType.PLAYER
            playerData['damageStickers'] = list(playerData.get('damageStickers', []))
            projectileData = {}
            projectileData.update(serverKillCamData['projectile']['unspottedData'])
            shellData = self.__unpackShellData(projectileData['shellCompDescr'])
            projectileData.update(shellData)
            projectileDataSpotted = serverKillCamData['projectile']['spottedData']
            if projectileDataSpotted:
                projectileData.update(projectileDataSpotted)
            self.processedData = {'attacker': self.__getAttackerData(),
             'player': playerData,
             'projectile': projectileData,
             'others': self.__collectOtherVehiclesForKillCam(vehicles, attackerID, playerID),
             'time': BigWorld.time()}
            return None

    def __getAttackerData(self):
        serverKillCamData = self.capturedKillCamData
        attackerID = serverKillCamData['attacker']['attackerID']
        attackerData = self.__captureVehSimulationData(BigWorld.entity(attackerID))
        if attackerData is None:
            attackerData = self.__captureUnspottedVehSimulationData(attackerID)
        attackerServerData = serverKillCamData['attacker']['spottedData']
        attackerData['hasSpottedData'] = attackerServerData is not None
        if attackerServerData:
            attackerData.update(attackerServerData)
        attackerServerData = serverKillCamData['attacker']['unspottedData']
        if attackerServerData:
            attackerData.update(attackerServerData)
        attackerData['simulationType'] = SimulatedVehicleType.ATTACKER
        return attackerData

    def __updateLateAttackerData(self):
        if not self.processedData:
            return
        attackerData = self.processedData['attacker']
        if attackerData['spotted']:
            return
        if not attackerData['hasSpottedData']:
            return
        self.processedData['attacker'] = self.__getAttackerData()

    def __collectOtherVehiclesForKillCam(self, vehicles, attackerID, playerID):
        return [ self.__captureVehSimulationData(veh) for veh in vehicles if veh.id not in (attackerID, playerID) and not veh.isDestroyed and veh.isStarted ]

    def __captureVehSimulationData(self, vehicle):
        if vehicle is None or vehicle.isDestroyed or not vehicle.isStarted:
            return
        else:
            matrix = Math.Matrix(vehicle.matrix)
            return {'vehicleID': vehicle.id,
             'position': matrix.translation.tuple(),
             'rotation': (matrix.roll, matrix.pitch, matrix.yaw),
             'health': vehicle.health,
             'gunAngles': self.__getGunAngles(vehicle),
             'turretAndGunSpeed': self.__getTurretAndGunSpeed(vehicle),
             'burnoutLevel': vehicle.burnoutLevel,
             'simulationType': SimulatedVehicleType.VEHICLE,
             'damageStickers': vehicle.damageStickers,
             'velocity': vehicle.filter.velocity,
             'spotted': True,
             'publicInfo': dict(vehicle.publicInfo),
             'brokenTracks': vehicle.appearance.getTrackStates(),
             'siegeState': vehicle.siegeState,
             'wheelsState': vehicle.appearance.wheelsState,
             'wheelsSteering': vehicle.appearance.wheelsSteering,
             'trackInAir': (vehicle.appearance.isLeftSideFlying, vehicle.appearance.isRightSideFlying)}

    def __captureUnspottedVehSimulationData(self, vehicleID):
        return {'vehicleID': vehicleID,
         'position': (0, 0, 0),
         'rotation': (0, 0, 0),
         'health': 0,
         'gunAngles': (0, 0),
         'burnoutLevel': 0,
         'simulationType': SimulatedVehicleType.VEHICLE,
         'damageStickers': frozenset(),
         'velocity': 0,
         'spotted': False}

    def __getGunAngles(self, veh):
        if veh.typeDescriptor:
            turretYaw, gunPitch = decodeGunAngles(veh.gunAnglesPacked, veh.typeDescriptor.gun.pitchLimits['absolute'])
        else:
            turretYaw = gunPitch = 0.0
        return (turretYaw, gunPitch)

    def __getTurretAndGunSpeed(self, veh):
        if veh.typeDescriptor:
            turretVelocity = veh.typeDescriptor.turret.rotationSpeed
            gunVelocity = veh.typeDescriptor.gun.rotationSpeed
        else:
            turretVelocity = gunVelocity = 0.0
        return (turretVelocity, gunVelocity)

    def __unpackShellData(self, shellCompDescr):
        shellDescr = getItemByCompactDescr(shellCompDescr)
        return {'shellType': BATTLE_LOG_SHELL_TYPES.getShellType(shellDescr),
         'shellKind': shellDescr.kind,
         'shellIcon': shellDescr.iconName,
         'shellCaliber': shellDescr.caliber,
         'averageDamageOfShell': shellDescr.armorDamage[0],
         'hasDistanceFalloff': shellDescr.isDamageMutable}
