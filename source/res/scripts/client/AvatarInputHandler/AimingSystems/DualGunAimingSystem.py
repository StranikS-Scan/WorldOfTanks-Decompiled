# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/AimingSystems/DualGunAimingSystem.py
from functools import partial
import BigWorld
import GUI
import math_utils
from AvatarInputHandler import AimingSystems
from AvatarInputHandler.AimingSystems import IAimingSystem
from AvatarInputHandler.AimingSystems.SniperAimingSystem import SniperAimingSystem
from Math import Vector3, Matrix, slerp
from constants import DUAL_GUN
from gui.battle_control import event_dispatcher as gui_event_dispatcher

class GunMatCalc(object):
    __slots__ = ('__currentGun',)

    @staticmethod
    def gunShotOffset(vehicleDescr, currentGun):
        if vehicleDescr.isDualgunVehicle and vehicleDescr.turret.multiGun is not None:
            if 0 <= currentGun < len(vehicleDescr.turret.multiGun):
                return vehicleDescr.turret.multiGun[currentGun].shotPosition
        return vehicleDescr.activeGunShotPosition

    @staticmethod
    def turretOffset(vehicleDescr):
        return vehicleDescr.chassis.hullPosition + vehicleDescr.hull.turretPositions[0]

    def __init__(self, gun):
        self.__currentGun = gun

    def __call__(self, yaw, pitch):
        player = BigWorld.player()
        if player.vehicle is not None:
            vehicleTypeDescriptor = player.vehicle.typeDescriptor
        else:
            vehicleTypeDescriptor = player.getVehicleAttached().typeDescriptor
        vehicleMat = player.inputHandler.steadyVehicleMatrixCalculator.outputMProv
        turretMat = self.__turretJointMat(vehicleMat, yaw, vehicleTypeDescriptor)
        gunMat = self.__gunJointMat(turretMat, pitch, vehicleTypeDescriptor)
        return gunMat

    def __turretJointMat(self, vehicleMat, turretYaw, vehicleDescr):
        turretOffset = self.turretOffset(vehicleDescr)
        turretMat = math_utils.createRTMatrix(Vector3(turretYaw, 0.0, 0.0), turretOffset)
        turretMat.postMultiply(vehicleMat)
        return turretMat

    def __gunJointMat(self, turretMat, gunPitch, vehicleDescr):
        gunShotOffset = self.gunShotOffset(vehicleDescr, self.__currentGun)
        gunMat = math_utils.createRTMatrix(Vector3(0.0, gunPitch, 0.0), gunShotOffset)
        gunMat.postMultiply(turretMat)
        return gunMat


class ShadowEffect(object):

    def __init__(self):
        self.__texturePath = 'system/maps/shadow.dds'
        self.__startPositionX = 2.0
        self.__shadowUpInitialPosition = (self.__startPositionX, 0.5, 1.0)
        self.__shadowDownInitialPosition = (self.__startPositionX, -0.5, 1.0)
        self.__size = (3, 1)
        self.__shadowUp = None
        self.__shadowDown = None
        self.cachedPosition = 2.0
        return

    def destroy(self):
        if self.__shadowUp is not None:
            GUI.delRoot(self.__shadowUp)
            self.__shadowUp = None
        if self.__shadowDown is not None:
            GUI.delRoot(self.__shadowDown)
            self.__shadowDown = None
        return

    def __spawnShadow(self, position, path, rotateAngle=None):
        shadow = GUI.Simple(path)
        if rotateAngle is not None:
            shadow.angle = rotateAngle
        shadow.position = position
        shadow.size = self.__size
        shadow.materialFX = 'BLEND'
        shadow.filterType = 'LINEAR'
        shadow.visible = False
        GUI.addRoot(shadow)
        return shadow

    def onGunIndexChanged(self, gunIndex):
        if gunIndex == DUAL_GUN.ACTIVE_GUN.RIGHT:
            self.cachedPosition = self.__startPositionX
        else:
            self.cachedPosition = -self.__startPositionX
        self.move(self.cachedPosition)

    def spawn(self):
        if self.__shadowUp is None or self.__shadowDown is None:
            self.__shadowUp = self.__spawnShadow(self.__shadowUpInitialPosition, self.__texturePath)
            self.__shadowDown = self.__spawnShadow(self.__shadowDownInitialPosition, self.__texturePath, 180)
        return

    def show(self):
        self.__shadowUp.visible = True
        self.__shadowDown.visible = True

    def hide(self):
        self.__shadowUp.visible = False
        self.__shadowDown.visible = False

    def move(self, positionX):
        self.__shadowUp.position[0] = positionX
        self.__shadowDown.position[0] = positionX

    def update(self, coefficient):
        shadowPositionX = round(math_utils.lerp(self.cachedPosition, -self.cachedPosition, coefficient), 1)
        self.move(shadowPositionX)


class GunTransitionInterpolator(object):
    __slots__ = ('__enabled', '__initialState', '__finalState', '__totalTime', '__elapsedTime', '__prevTime', '__shadowEffect')
    _EASING_METHOD = math_utils.easeInOutQuad
    enabled = property(lambda self: self.__enabled)
    matrix = property(lambda self: self.__update())

    def __init__(self, shadowEffect):
        self.__enabled = False
        self.__initialState = None
        self.__finalState = None
        self.__totalTime = None
        self.__elapsedTime = 0.0
        self.__prevTime = 0.0
        self.__shadowEffect = shadowEffect
        return

    def enable(self, initialState, finalState, transitionTime):
        self.__enabled = True
        self.__shadowEffect.show()
        self.__totalTime = transitionTime
        self.__prevTime = BigWorld.timeExact()
        if self.__elapsedTime > 0.0:
            self.__elapsedTime = self.__totalTime - self.__elapsedTime
        self.__initialState = initialState
        self.__finalState = finalState

    def disable(self):
        self.__enabled = False
        self.__elapsedTime = 0.0
        self.__initialState = None
        self.__finalState = None
        self.__shadowEffect.hide()
        return

    def __update(self):
        currentTime = BigWorld.timeExact()
        self.__elapsedTime += currentTime - self.__prevTime
        self.__prevTime = currentTime
        interpolationCoefficient = math_utils.easeInOutQuad(self.__elapsedTime, 1.0, self.__totalTime)
        interpolationCoefficient = math_utils.clamp(0.0, 1.0, interpolationCoefficient)
        iSource = self.__initialState.matrix
        iTarget = self.__finalState.matrix
        mat = slerp(iSource, iTarget, interpolationCoefficient)
        mat.translation = math_utils.lerp(iSource.translation, iTarget.translation, interpolationCoefficient)
        self.__shadowEffect.update(interpolationCoefficient)
        if self.__elapsedTime > self.__totalTime:
            self.disable()
        return mat


class SingleGunAimingSystem(SniperAimingSystem):

    def __init__(self, gunIndex):
        super(SingleGunAimingSystem, self).__init__()
        self.__gunIndex = gunIndex

    def _getTurretYawGunPitch(self, targetPos, compensateGravity=False):
        vehicleMatrix = Matrix(self._vehicleMProv)
        turretOffset = GunMatCalc.turretOffset(self._vehicleTypeDescriptor)
        gunShotOffset = GunMatCalc.gunShotOffset(self._vehicleTypeDescriptor, self.__gunIndex)
        speed = self._vehicleTypeDescriptor.shot.speed
        gravity = self._vehicleTypeDescriptor.shot.gravity if not compensateGravity else 0.0
        turretYaw, gunPitch = BigWorld.wg_getShotAngles(turretOffset, gunShotOffset, vehicleMatrix, speed, gravity, 0.0, 0.0, targetPos, False)
        rotation = math_utils.createRotationMatrix((turretYaw, gunPitch, 0.0))
        rotation.postMultiply(vehicleMatrix)
        invertSteady = Matrix(self._vehicleMProv)
        invertSteady.invert()
        rotation.postMultiply(invertSteady)
        return (rotation.yaw, rotation.pitch)


class DualGunAimingSystem(IAimingSystem):
    __TRANSITION_TIME = 0.3
    __TRANSITION_DELAY = 0.0
    turretYaw = property(lambda self: self.__turretYaw())
    gunPitch = property(lambda self: self.__gunPitch())

    @staticmethod
    def setTransitionTime(seconds):
        DualGunAimingSystem.__TRANSITION_TIME = seconds

    @staticmethod
    def setTransitionDelay(seconds):
        DualGunAimingSystem.__TRANSITION_DELAY = seconds

    def __init__(self):
        super(DualGunAimingSystem, self).__init__()
        self._aim = (SingleGunAimingSystem(DUAL_GUN.ACTIVE_GUN.LEFT), SingleGunAimingSystem(DUAL_GUN.ACTIVE_GUN.RIGHT))
        self.__activeAim = self._aim[DUAL_GUN.ACTIVE_GUN.LEFT]
        self.__activeGun = DUAL_GUN.ACTIVE_GUN.LEFT
        self.__shadowEffect = ShadowEffect()
        self.__shadowEffect.spawn()
        self.__interpolator = GunTransitionInterpolator(self.__shadowEffect)
        self.__transitionCallbackID = None
        self.__pendingGunIndex = None
        return

    def destroy(self):
        super(DualGunAimingSystem, self).destroy()
        self.__interpolator.disable()
        if self.__transitionCallbackID is not None:
            BigWorld.cancelCallback(self.__transitionCallbackID)
        self.__shadowEffect.destroy()
        return

    def enableHorizontalStabilizerRuntime(self, enable):
        for aim in self._aim:
            aim.enableHorizontalStabilizerRuntime(enable)

    def forceFullStabilization(self, enable):
        for aim in self._aim:
            aim.forceFullStabilization(enable)

    def enable(self, targetPos, playerGunMatFunction=AimingSystems.getPlayerGunMat):
        player = BigWorld.player()
        if player.isObserver():
            vehicle = player.getVehicleAttached()
        else:
            vehicle = player.vehicle
        if vehicle is None:
            vehicle = player.getVehicleAttached()
        self.__switchActiveAim(vehicle.activeGunIndex)
        self.__activeAim.enable(targetPos, GunMatCalc(self.__activeGun))
        return

    def disable(self):
        if self.__interpolator.enabled:
            self.__interpolator.disable()
            for aim in self._aim:
                aim.disable()

        else:
            self.__activeAim.disable()
        if self.__transitionCallbackID is not None:
            BigWorld.cancelCallback(self.__transitionCallbackID)
            self.__transitionCallbackID = None
        if self.__pendingGunIndex is not None:
            self.__pendingGunIndex = None
        return

    def focusOnPos(self, preferredPos):
        if self.__interpolator.enabled:
            for aim in self._aim:
                aim.focusOnPos(preferredPos)

            self._matrix.set(self.__interpolator.matrix)
        else:
            self.__activeAim.focusOnPos(preferredPos)
            self._matrix.set(self.__activeAim.matrix)

    def onActiveGunChanged(self, newState, switchDelay):
        if self.__pendingGunIndex != newState:
            if self.__transitionCallbackID is not None:
                BigWorld.cancelCallback(self.__transitionCallbackID)
                self.__transitionCallbackID = None
                targetPoint = self.getDesiredShotPoint()
                self.__activeAim.disable()
                self.__switchActiveAim(self.__pendingGunIndex)
                self.__activeAim.enable(targetPoint, GunMatCalc(self.__activeGun))
            self.__pendingGunIndex = newState
            self.__transitionCallbackID = BigWorld.callback(switchDelay, partial(self.__onStartTransition, self.__activeGun, newState))
        return

    def onSiegeStateChanged(self, siegeState):
        pass

    def __onStartTransition(self, initialGunIndex, finalGunIndex):
        targetPoint = self.getDesiredShotPoint()
        self.__switchActiveAim(finalGunIndex)
        self.enable(targetPoint)
        self.__interpolator.enable(self._aim[initialGunIndex], self._aim[finalGunIndex], self.__TRANSITION_TIME)
        self.__transitionCallbackID = BigWorld.callback(self.__TRANSITION_TIME, partial(self.__onEndTransition, initialGunIndex))
        gui_event_dispatcher.sniperCameraTransition(self.__TRANSITION_TIME, finalGunIndex)

    def __onEndTransition(self, initialGunIndex):
        self.__pendingGunIndex = None
        self.__transitionCallbackID = None
        self._aim[initialGunIndex].disable()
        self.__interpolator.disable()
        return

    def getDesiredShotPoint(self):
        return self.__activeAim.getDesiredShotPoint()

    def resetIdealDirection(self):
        self._aim[self.__activeGun].resetIdealDirection()

    def handleMovement(self, dx, dy):
        if self.__interpolator.enabled:
            for aim in self._aim:
                aim.handleMovement(dx, dy)

            self._matrix.set(self.__interpolator.matrix)
        else:
            self.__activeAim.handleMovement(dx, dy)
            self._matrix.set(self.__activeAim.matrix)

    def update(self, dt):
        if self.__interpolator.enabled:
            for aim in self._aim:
                aim.update(dt)

            self._matrix.set(self.__interpolator.matrix)
        else:
            self.__activeAim.update(dt)
            self._matrix.set(self._aim[self.__activeGun].matrix)

    def getShotPoint(self):
        return self.getDesiredShotPoint()

    def getZoom(self):
        return self.__activeAim.getZoom()

    def overrideZoom(self, zoom):
        for aim in self._aim:
            aim.overrideZoom(zoom)

        return zoom

    def __turretYaw(self):
        return self.__activeAim.turretYaw

    def __gunPitch(self):
        return self.__activeAim.gunPitch

    def __switchActiveAim(self, activeGun):
        gunIndex = activeGun if activeGun is not None else DUAL_GUN.ACTIVE_GUN.LEFT
        if self.__activeGun != gunIndex:
            self.__activeGun = gunIndex
            self.__activeAim = self._aim[gunIndex]
        self.__shadowEffect.onGunIndexChanged(gunIndex)
        return
