# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VehicleObserverGunRotator.py
import BigWorld
import Math
import BattleReplay
from VehicleGunRotator import VehicleGunRotator

class VehicleObserverGunRotator(VehicleGunRotator):

    def __init__(self, avatar):
        self.__avatar = avatar
        super(VehicleObserverGunRotator, self).__init__(avatar)

    def start(self):
        if not self.__avatar.isVehicleAlive:
            return
        super(VehicleObserverGunRotator, self).start()

    def update(self, turretYaw, gunPitch, maxTurretRotationSpeed, maxGunRotationSpeed):
        player = BigWorld.player()
        vehicle = player.getVehicleAttached()
        tY = turretYaw
        gP = gunPitch
        if vehicle is not None:
            tY, gP = vehicle.getAimParams()
        super(VehicleObserverGunRotator, self).update(tY, gP, maxTurretRotationSpeed, maxGunRotationSpeed)
        return

    def setShotPosition(self, vehicleID, shotPos, shotVec, dispersionAngle, forceValueRefresh=False):
        self.__avatar.observedVehicleData[vehicleID].dispAngle = dispersionAngle
        super(VehicleObserverGunRotator, self).setShotPosition(vehicleID, shotPos, shotVec, dispersionAngle, True)

    def updateRotationAndGunMarker(self, shotPoint, timeDiff):
        pass

    def getNextTurretYaw(self, curAngle, shotAngle, speedLimit, angleLimits):
        replayCtrl = BattleReplay.g_replayCtrl
        player = BigWorld.player()
        if not replayCtrl.isPlaying:
            vehicle = player.getVehicleAttached()
            if vehicle is not None:
                turretYaw, gunPitch = vehicle.getAimParams()
                return turretYaw
        return super(VehicleObserverGunRotator, self).getNextTurretYaw(curAngle, shotAngle, speedLimit, angleLimits)

    def getNextGunPitch(self, curAngle, shotAngle, timeDiff, angleLimits):
        replayCtrl = BattleReplay.g_replayCtrl
        player = BigWorld.player()
        if not replayCtrl.isPlaying:
            vehicle = player.getVehicleAttached()
            if vehicle is not None:
                turretYaw, gunPitch = vehicle.getAimParams()
                return gunPitch
        return super(VehicleObserverGunRotator, self).getNextGunPitch(curAngle, shotAngle, timeDiff, angleLimits)

    def getAvatarOwnVehicleStabilisedMatrix(self):
        player = BigWorld.player()
        vehicle = player.getVehicleAttached()
        return Math.Matrix(vehicle.matrix) if vehicle is not None else super(VehicleObserverGunRotator, self).getAvatarOwnVehicleStabilisedMatrix()

    def getAttachedVehicleID(self):
        vehicle = self.__avatar.getVehicleAttached()
        return vehicle.id if vehicle is not None else super(VehicleObserverGunRotator, self).getAttachedVehicleID()
