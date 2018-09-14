# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/mark_turret.py
import BigWorld
import random
from AvatarInputHandler import mathUtils
from Math import Vector3
from VehicleGunRotator import _MatrixAnimator
from constants import SERVER_TICK_LENGTH
from helpers.CallbackDelayer import CallbackDelayer
from vehicle_systems.assembly_utility import ComponentSystem, AutoProperty

class MarkTurret(ComponentSystem, CallbackDelayer):
    gunRecoil = AutoProperty()
    turretMatrix = AutoProperty()
    gunMatrix = AutoProperty()
    __DEMO_DELAY = 2

    def __init__(self):
        ComponentSystem.__init__(self)
        CallbackDelayer.__init__(self)
        self.__turretAnimator = _MatrixAnimator(None)
        self.__gunAnimator = _MatrixAnimator(None)
        self.__turretMatrix = self.__turretAnimator.matrix
        self.__gunMatrix = self.__gunAnimator.matrix
        return

    def runDemo(self):
        self.delayCallback(0, self.__demoCallback)

    def __demoCallback(self):
        self.__turretAnimator.update(mathUtils.createRotationMatrix((random.random() * 3.14 / 2, 0, 0)), MarkTurret.__DEMO_DELAY)
        self.__gunAnimator.update(mathUtils.createRotationMatrix((0, (random.random() - 0.5) * 3.14 / 3, 0)), MarkTurret.__DEMO_DELAY)
        dice = random.randint(0, 2)
        if not dice & 1:
            BigWorld.player().vehicle.showShooting(1, 0, True)
        if not dice & 2:
            BigWorld.player().vehicle.showShooting(1, 1, True)
        return MarkTurret.__DEMO_DELAY

    def destroy(self):
        CallbackDelayer.destroy(self)
        ComponentSystem.destroy(self)

    def updateGunAngles(self, yaw, pitch):
        turretMat = mathUtils.createRotationMatrix(Vector3(yaw, 0, 0))
        self.__turretAnimator.update(turretMat, SERVER_TICK_LENGTH)
        gunMat = mathUtils.createRotationMatrix(Vector3(0, pitch, 0))
        self.__gunAnimator.update(gunMat, SERVER_TICK_LENGTH)
