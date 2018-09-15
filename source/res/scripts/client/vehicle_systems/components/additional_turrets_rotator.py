# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/additional_turrets_rotator.py
import BigWorld
import Math
import svarog_script.py_component
from VehicleGunRotator import _MatrixAnimator
from AvatarInputHandler import mathUtils
from constants import SERVER_TICK_LENGTH
from debug_utils import LOG_DEBUG

class AdditionalTurretsRotator(svarog_script.py_component.Component):

    def __init__(self, allTurretCount):
        super(AdditionalTurretsRotator, self).__init__()
        self.__turretsAnimators = []
        self.__gunsAnimators = []
        self.__turretsAnimators.append(None)
        self.__gunsAnimators.append(None)
        self.__isTurretLocked = []
        self.__isTurretLocked.append(False)
        for i in range(1, allTurretCount):
            turretAnimator = _MatrixAnimator(None)
            self.__turretsAnimators.append(turretAnimator)
            gunAnimator = _MatrixAnimator(None)
            self.__gunsAnimators.append(gunAnimator)
            self.__isTurretLocked.append(False)

        return

    def getTurretYaw(self, turretIndex):
        return Math.Matrix(self.getTurretMatrix(turretIndex)).yaw

    def getGunPitch(self, turretIndex):
        return Math.Matrix(self.getGunMatrix(turretIndex)).pitch

    def getTurretMatrix(self, index):
        if index >= len(self.__turretsAnimators):
            return None
        else:
            turretAnimator = self.__turretsAnimators[index]
            return turretAnimator.matrix

    def getGunMatrix(self, index):
        if index >= len(self.__gunsAnimators):
            return None
        else:
            gunAnimator = self.__gunsAnimators[index]
            return gunAnimator.matrix

    def activate(self):
        pass

    def deactivate(self):
        pass

    def lock(self, isLocked, turretIndex):
        if turretIndex < len(self.__isTurretLocked):
            self.__isTurretLocked[turretIndex] = isLocked

    def destroy(self):
        self.deactivate()

    def updateGunAngles(self, yaw, pitch, turretIndex):
        if turretIndex >= len(self.__turretsAnimators):
            return
        if turretIndex >= len(self.__isTurretLocked) or self.__isTurretLocked[turretIndex]:
            return
        turretMatrix = mathUtils.createRotationMatrix(Math.Vector3(yaw, 0, 0))
        turretAnimator = self.__turretsAnimators[turretIndex]
        turretAnimator.update(turretMatrix, SERVER_TICK_LENGTH)
        if turretIndex >= len(self.__gunsAnimators):
            return
        gunMatrix = mathUtils.createRotationMatrix(Math.Vector3(0, pitch, 0))
        gunAnimator = self.__gunsAnimators[turretIndex]
        gunAnimator.update(gunMatrix, SERVER_TICK_LENGTH)
