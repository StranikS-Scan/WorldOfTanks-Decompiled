# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/VideoCamera.py
import math
import time
import Math
from Math import Vector3, Matrix
import BigWorld
from AvatarInputHandler import mathUtils, AimingSystems
from avatar_helpers.aim_global_binding import CTRL_MODE_NAME
from helpers.CallbackDelayer import CallbackDelayer, TimeDeltaMeter
import GUI
import Keys
from ProjectileMover import collideDynamicAndStatic
import BattleReplay
from gui.battle_control import g_sessionProvider
from gui.battle_control import event_dispatcher as gui_event_dispatcher
from helpers import isPlayerAvatar
from DetachedTurret import DetachedTurret

class KeySensor:

    def __init__(self, keyMappings, sensitivity, sensitivityIncDecKeys=None, sensitivityAcceleration=None):
        self.keyMappings = keyMappings
        self.sensitivity = self.defaultSensitivity = sensitivity
        self.__sensitivityKeys = {}
        if sensitivityIncDecKeys is not None:
            self.__sensitivityKeys[sensitivityIncDecKeys[0]] = sensitivityAcceleration
            self.__sensitivityKeys[sensitivityIncDecKeys[1]] = -sensitivityAcceleration
        self.currentVelocity = None
        self.__currentKeys = set()
        return

    def addVelocity(self, velocity):
        if self.currentVelocity is None:
            self.currentVelocity = velocity
        else:
            self.currentVelocity += velocity
        return

    def reset(self, defaultVelocity):
        self.__currentKeys.clear()
        self.currentVelocity = defaultVelocity

    def resetKeys(self):
        self.__currentKeys.clear()

    def handleKeyEvent(self, key, isDown):
        for senseKey, acceleration in self.__sensitivityKeys.iteritems():
            if senseKey == key:
                if isDown:
                    self.__currentKeys.add(key)
                else:
                    self.__currentKeys.discard(key)
                return True

        for mappingKey, shift in self.keyMappings.iteritems():
            if mappingKey == key:
                if isDown:
                    self.__currentKeys.add(key)
                else:
                    self.__currentKeys.discard(key)
                return True

        return False

    def update(self, delta):
        for senseKey, acceleration in self.__sensitivityKeys.iteritems():
            if senseKey in self.__currentKeys:
                self.sensitivity += acceleration * delta

        for mappingKey, shift in self.keyMappings.iteritems():
            if mappingKey in self.__currentKeys:
                addValue = shift * self.sensitivity
                if self.currentVelocity is None:
                    self.currentVelocity = addValue * self.sensitivity
                else:
                    self.currentVelocity += addValue * self.sensitivity

        return


class _Inertia(object):

    def __init__(self, frictionCoeff):
        self.frictionCoeff = frictionCoeff

    def integrate(self, thrust, velocity, delta):
        acc = thrust - self.frictionCoeff * velocity
        if acc.x * thrust.x < 0:
            acc.x = 0.0
        if acc.y * thrust.y < 0:
            acc.y = 0.0
        if acc.z * thrust.z < 0:
            acc.z = 0.0
        return velocity + acc * delta


class _AlignerToLand:
    MIN_HEIGHT = 0.5
    enabled = property(lambda self: self.__desiredHeightShift is not None)
    ignoreTerrain = property(lambda self: self.__ignoreTerrain)

    def __init__(self):
        self.__desiredHeightShift = None
        self.__ignoreTerrain = False
        return

    def enable(self, position, aboveSeaLevel=False):
        self.__ignoreTerrain = aboveSeaLevel
        landPosition = self.__getLandAt(position)
        if landPosition is not None:
            self.__desiredHeightShift = position - landPosition
            if self.__desiredHeightShift.y < _AlignerToLand.MIN_HEIGHT and not aboveSeaLevel:
                self.__desiredHeightShift.y = _AlignerToLand.MIN_HEIGHT
        else:
            self.__desiredHeightShift = None
        return

    def disable(self):
        self.__desiredHeightShift = None
        self.__ignoreTerrain = False
        return

    def __getLandAt(self, position):
        if self.__ignoreTerrain:
            return Vector3(position.x, 0, position.z)
        else:
            spaceID = BigWorld.player().spaceID
            if spaceID is None:
                return
            upPoint = Math.Vector3(position)
            upPoint.y += 1000
            downPoint = Math.Vector3(position)
            downPoint.y = -1000
            collideRes = BigWorld.wg_collideSegment(spaceID, upPoint, downPoint, 16, 8)
            return None if collideRes is None else collideRes[0]

    def getAlignedPosition(self, position):
        if self.__desiredHeightShift is None:
            return position
        else:
            landPos = self.__getLandAt(position)
            return position if landPos is None else landPos + self.__desiredHeightShift


class _VehicleBounder(object):
    SELECT_CHASSIS = 0
    SELECT_TURRET = 1
    SELECT_GUN = 2
    SELECT_LOOK_AT = 3
    __MAX_SELECT = 4
    SELECT_DETACHED_TURRET = 4

    def __getLookAtPosition(self):
        return None if self.__lookAtProvider is None else Matrix(self.__lookAtProvider).translation

    isBound = property(lambda self: self.__vehicle is not None)
    lookAtPosition = property(__getLookAtPosition)

    def __init__(self):
        self.matrix = mathUtils.createIdentityMatrix()
        self.__boundLocalPos = None
        self.__vehicle = None
        self.__lookAtProvider = None
        self.__placement = _VehicleBounder.SELECT_CHASSIS
        return

    def bind(self, vehicle, bindWorldPos=None):
        self.__vehicle = vehicle
        if vehicle is None:
            self.matrix = mathUtils.createIdentityMatrix()
            self.__lookAtProvider = None
            return
        else:
            toLocalMat = Matrix(vehicle.matrix)
            toLocalMat.invert()
            self.__boundLocalPos = None if bindWorldPos is None else toLocalMat.applyPoint(bindWorldPos)
            self.selectPlacement(_VehicleBounder.SELECT_CHASSIS)
            return

    def selectPlacement(self, placement):
        if self.__vehicle is None:
            return
        else:
            self.__placement = placement
            self.__lookAtProvider = None
            if placement == _VehicleBounder.SELECT_CHASSIS:
                self.matrix = self.__vehicle.matrix
            elif placement == _VehicleBounder.SELECT_TURRET:
                self.matrix = AimingSystems.getTurretMatrixProvider(self.__vehicle.typeDescriptor, self.__vehicle.matrix, self.__vehicle.appearance.turretMatrix)
            elif placement == _VehicleBounder.SELECT_GUN:
                turretMatrixProv = AimingSystems.getTurretMatrixProvider(self.__vehicle.typeDescriptor, self.__vehicle.matrix, self.__vehicle.appearance.turretMatrix)
                self.matrix = AimingSystems.getGunMatrixProvider(self.__vehicle.typeDescriptor, turretMatrixProv, self.__vehicle.appearance.gunMatrix)
            elif placement == _VehicleBounder.SELECT_LOOK_AT:
                self.matrix = mathUtils.createIdentityMatrix()
                self.__lookAtProvider = mathUtils.MatrixProviders.product(mathUtils.createTranslationMatrix(self.__boundLocalPos), self.__vehicle.matrix)
            return

    def selectNextPlacement(self):
        self.selectPlacement((self.__placement + 1) % _VehicleBounder.__MAX_SELECT)

    def checkTurretDetachment(self, worldPos):
        if self.__vehicle is None:
            return
        elif self.__vehicle.isTurretDetached and not self.__placement == _VehicleBounder.SELECT_DETACHED_TURRET:
            turretFound = None
            for turret in DetachedTurret.allTurrets:
                if turret.vehicleID == self.__vehicle.id and turret.model.visible:
                    turretFound = turret
                    break

            if turretFound is None:
                return
            turretToGoalShift = worldPos - turretFound.position
            toTurretMat = Matrix(turretFound.matrix)
            toTurretMat.invert()
            turretToGoalShift = toTurretMat.applyVector(turretToGoalShift)
            self.matrix = turretFound.matrix
            self.__lookAtProvider = None
            self.__placement = _VehicleBounder.SELECT_DETACHED_TURRET
            return turretToGoalShift
        else:
            return


class _VehiclePicker(object):

    def pick(self):
        x, y = GUI.mcursor().position
        from AvatarInputHandler import cameras
        dir, start = cameras.getWorldRayAndPoint(x, y)
        end = start + dir.scale(100000.0)
        posColldata = collideDynamicAndStatic(start, end, (), 0)
        if posColldata is None:
            return (None, None)
        else:
            pos, collData = posColldata
            return (None, None) if collData is None or not collData.isVehicle() else (collData[0], pos)


class VideoCamera(CallbackDelayer, TimeDeltaMeter):

    def __init__(self, configDataSec):
        CallbackDelayer.__init__(self)
        TimeDeltaMeter.__init__(self, time.clock)
        self.__cam = BigWorld.FreeCamera()
        self.__cam.invViewProvider = Math.MatrixProduct()
        self.__ypr = Math.Vector3()
        self.__position = Math.Vector3()
        self.__defaultFov = BigWorld.projection().fov
        self.__velocity = Math.Vector3()
        self.__isVerticalVelocitySeparated = False
        self.__yprVelocity = Math.Vector3()
        self.__zoomVelocity = 0.0
        self.__inertiaEnabled = False
        self.__movementInertia = None
        self.__rotationInertia = None
        self.__movementSensor = None
        self.__verticalMovementSensor = None
        self.__rotationSensor = None
        self.__zoomSensor = None
        self.__targetRadiusSensor = None
        self.__mouseSensitivity = 0.0
        self.__scrollSensitivity = 0.0
        self.__rotateAroundPointEnabled = False
        self.__rotationRadius = 40.0
        self.__alignerToLand = _AlignerToLand()
        self.__predefinedVelocities = {}
        self.__predefinedVerticalVelocities = {}
        self.__keySwitches = {}
        self.__readCfg(configDataSec)
        self.__isModeOverride = False
        self.__basisMProv = _VehicleBounder()
        self.__entityPicker = _VehiclePicker()
        return

    def getReasonsAffectCameraDirectly(self):
        pass

    def applyImpulse(self, position, impulse, reason=1):
        pass

    def create(self):
        pass

    def destroy(self):
        CallbackDelayer.destroy(self)
        self.__cam = None
        return

    def enable(self, **args):
        self.measureDeltaTime()
        self.delayCallback(0.0, self.__update)
        camMatrix = args.get('camMatrix', BigWorld.camera().matrix)
        self.__cam.set(camMatrix)
        self.__cam.invViewProvider.a = camMatrix
        self.__cam.invViewProvider.b = mathUtils.createIdentityMatrix()
        BigWorld.camera(self.__cam)
        worldMat = Math.Matrix(self.__cam.invViewMatrix)
        self.__ypr = Math.Vector3(worldMat.yaw, worldMat.pitch, worldMat.roll)
        self.__position = worldMat.translation
        self.__velocity = Math.Vector3()
        self.__yprVelocity = Math.Vector3()
        self.__zoomVelocity = 0.0
        self.__resetSenses()
        self.__basisMProv.bind(None)
        self.__rotateAroundPointEnabled = False
        self.__alignerToLand.disable()
        if isPlayerAvatar() and g_sessionProvider.getCtx().isPlayerObserver():
            BigWorld.player().positionControl.moveTo(self.__position)
            BigWorld.player().positionControl.followCamera(True)
        return

    def disable(self):
        self.stopCallback(self.__update)
        BigWorld.projection().fov = self.__defaultFov
        BigWorld.camera(None)
        self.__alignerToLand.disable()
        if isPlayerAvatar():
            BigWorld.player().positionControl.followCamera(False)
        self.__isModeOverride = False
        return

    def handleKeyEvent(self, key, isDown):
        if key is None:
            return False
        else:
            if isDown:
                if self.__keySwitches['keySwitchInertia'] == key:
                    self.__inertiaEnabled = not self.__inertiaEnabled
                    return True
                if self.__keySwitches['keySwitchRotateAroundPoint'] == key:
                    self.__rotateAroundPointEnabled = not self.__rotateAroundPointEnabled
                    return True
                if self.__keySwitches['keySwitchLandCamera'] == key:
                    if self.__alignerToLand.enabled or self.__basisMProv.isBound:
                        self.__alignerToLand.disable()
                    else:
                        self.__alignerToLand.enable(self.__position, BigWorld.isKeyDown(Keys.KEY_LALT) or BigWorld.isKeyDown(Keys.KEY_RALT))
                    return True
                if self.__keySwitches['keySetDefaultFov'] == key:
                    BigWorld.projection().fov = self.__defaultFov
                    return True
                if self.__keySwitches['keySetDefaultRoll'] == key:
                    self.__ypr.z = 0.0
                    return True
                if self.__keySwitches['keyRevertVerticalVelocity'] == key:
                    self.__isVerticalVelocitySeparated = False
                    return True
                if self.__keySwitches['keyBindToVehicle'] == key:
                    self.__processBindToVehicleKey()
                    return True
                if BigWorld.isKeyDown(Keys.KEY_LSHIFT) or BigWorld.isKeyDown(Keys.KEY_RSHIFT):
                    if self.__verticalMovementSensor.handleKeyEvent(key, isDown) and key not in self.__verticalMovementSensor.keyMappings:
                        self.__isVerticalVelocitySeparated = True
                        return True
                    for velocityKey, velocity in self.__predefinedVerticalVelocities.iteritems():
                        if velocityKey == key:
                            self.__verticalMovementSensor.sensitivity = velocity
                            self.__isVerticalVelocitySeparated = True
                            return True

                for velocityKey, velocity in self.__predefinedVelocities.iteritems():
                    if velocityKey == key:
                        self.__movementSensor.sensitivity = velocity
                        return True

            if key in self.__verticalMovementSensor.keyMappings:
                self.__verticalMovementSensor.handleKeyEvent(key, isDown)
            return self.__movementSensor.handleKeyEvent(key, isDown) or self.__rotationSensor.handleKeyEvent(key, isDown) or self.__zoomSensor.handleKeyEvent(key, isDown) or self.__targetRadiusSensor.handleKeyEvent(key, isDown)

    def resetMovement(self):
        self.__movementSensor.resetKeys()

    def handleMouseEvent(self, dx, dy, dz):
        relativeSenseGrowth = self.__rotationSensor.sensitivity / self.__rotationSensor.defaultSensitivity
        self.__rotationSensor.addVelocity(Math.Vector3(dx, dy, 0) * self.__mouseSensitivity * relativeSenseGrowth)
        movementShift = Vector3(0, dz * self.__movementSensor.sensitivity * self.__scrollSensitivity, 0)
        self.__movementSensor.addVelocity(movementShift)
        GUI.mcursor().position = Math.Vector2(0, 0)

    def __calcCurrentDeltaAdjusted(self):
        delta = self.measureDeltaTime()
        if delta > 1.0:
            delta = 0.0
        return delta
        replaySpeed = BattleReplay.g_replayCtrl.playbackSpeed
        if replaySpeed == 0:
            replaySpeed = 1e-08
        delta = delta / replaySpeed
        if delta > 1.0:
            delta = 0.0
        return delta

    def __getMovementDirections(self):
        m = mathUtils.createRotationMatrix(self.__ypr)
        result = (m.applyVector(Vector3(1, 0, 0)), Vector3(0, 1, 0), m.applyVector(Vector3(0, 0, 1)))
        if self.__alignerToLand.enabled:
            result[0].y = 0.0
            result[2].y = 0.0
        return result

    def __update(self):
        worldMatrix = Matrix(self.__cam.invViewMatrix)
        desiredPosition = self.__basisMProv.checkTurretDetachment(worldMatrix.translation)
        if desiredPosition is not None:
            self.__position = desiredPosition
        prevPos = Math.Vector3(self.__position)
        delta = self.__calcCurrentDeltaAdjusted()
        self.__updateSenses(delta)
        self.__rotationRadius += self.__targetRadiusSensor.currentVelocity * delta
        if self.__isVerticalVelocitySeparated:
            self.__verticalMovementSensor.update(delta)
        else:
            self.__verticalMovementSensor.currentVelocity = self.__movementSensor.currentVelocity.y
            self.__verticalMovementSensor.sensitivity = self.__movementSensor.sensitivity
        if self.__inertiaEnabled:
            self.__inertialMovement(delta)
        else:
            self.__simpleMovement(delta)
        self.__ypr += self.__yprVelocity * delta
        self.__position += self.__velocity * delta
        if self.__rotateAroundPointEnabled:
            self.__position = self.__getAlignedToPointPosition(mathUtils.createRotationMatrix(self.__ypr))
        if self.__alignerToLand.enabled and not self.__basisMProv.isBound:
            if abs(self.__velocity.y) > 0.1:
                self.__alignerToLand.enable(self.__position, self.__alignerToLand.ignoreTerrain)
            self.__position = self.__alignerToLand.getAlignedPosition(self.__position)
        lookAtPosition = self.__basisMProv.lookAtPosition
        if lookAtPosition is not None:
            self.__ypr = self.__getLookAtYPR(lookAtPosition)
        self.__ypr = self.__clampYPR(self.__ypr)
        self.__position = self.__checkSpaceBounds(prevPos, self.__position)
        self.__cam.invViewProvider.a = mathUtils.createRTMatrix(self.__ypr, self.__position)
        self.__cam.invViewProvider.b = self.__basisMProv.matrix
        BigWorld.projection().fov = self.__calcFov()
        self.__resetSenses()
        return 0.0

    def __simpleMovement(self, delta):
        self.__yprVelocity = self.__rotationSensor.currentVelocity
        shift = self.__movementSensor.currentVelocity
        shift.y = self.__verticalMovementSensor.currentVelocity
        moveDirs = self.__getMovementDirections()
        self.__velocity = moveDirs[0] * shift.x + moveDirs[1] * shift.y + moveDirs[2] * shift.z

    def __inertialMovement(self, delta):
        self.__yprVelocity = self.__rotationInertia.integrate(self.__rotationSensor.currentVelocity, self.__yprVelocity, delta)
        thrust = self.__movementSensor.currentVelocity
        thrust.y = self.__verticalMovementSensor.currentVelocity
        moveDirs = self.__getMovementDirections()
        thrust = moveDirs[0] * thrust.x + moveDirs[1] * thrust.y + moveDirs[2] * thrust.z
        self.__velocity = self.__movementInertia.integrate(thrust, self.__velocity, delta)

    def __getAlignedToPointPosition(self, rotationMat):
        dirVector = Math.Vector3(0, 0, self.__rotationRadius)
        camMat = Math.Matrix(self.__cam.invViewProvider.a)
        point = camMat.applyPoint(dirVector)
        return point + rotationMat.applyVector(-dirVector)

    def __readCfg(self, configDataSec):
        movementMappings = dict()
        movementMappings[getattr(Keys, configDataSec.readString('keyMoveLeft', 'KEY_A'))] = Vector3(-1, 0, 0)
        movementMappings[getattr(Keys, configDataSec.readString('keyMoveRight', 'KEY_D'))] = Vector3(1, 0, 0)
        keyMoveUp = getattr(Keys, configDataSec.readString('keyMoveUp', 'KEY_PGUP'))
        keyMoveDown = getattr(Keys, configDataSec.readString('keyMoveDown', 'KEY_PGDN'))
        movementMappings[keyMoveUp] = Vector3(0, 1, 0)
        movementMappings[keyMoveDown] = Vector3(0, -1, 0)
        movementMappings[getattr(Keys, configDataSec.readString('keyMoveForward', 'KEY_W'))] = Vector3(0, 0, 1)
        movementMappings[getattr(Keys, configDataSec.readString('keyMoveBackward', 'KEY_S'))] = Vector3(0, 0, -1)
        linearSensitivity = configDataSec.readFloat('linearVelocity', 40.0)
        linearSensitivityAcc = configDataSec.readFloat('linearVelocityAcceleration', 30.0)
        linearIncDecKeys = (getattr(Keys, configDataSec.readString('keyLinearVelocityIncrement', 'KEY_I')), getattr(Keys, configDataSec.readString('keyLinearVelocityDecrement', 'KEY_K')))
        self.__movementSensor = KeySensor(movementMappings, linearSensitivity, linearIncDecKeys, linearSensitivityAcc)
        self.__verticalMovementSensor = KeySensor({keyMoveUp: 1,
         keyMoveDown: -1}, linearSensitivity, linearIncDecKeys, linearSensitivityAcc)
        self.__movementSensor.currentVelocity = Math.Vector3()
        self.__keySwitches['keyRevertVerticalVelocity'] = getattr(Keys, configDataSec.readString('keyRevertVerticalVelocity', 'KEY_Z'))
        self.__mouseSensitivity = configDataSec.readFloat('sensitivity', 1.0)
        self.__scrollSensitivity = configDataSec.readFloat('scrollSensitivity', 1.0)
        rotationMappings = dict()
        rotationMappings[getattr(Keys, configDataSec.readString('keyRotateLeft', 'KEY_LEFTARROW'))] = Vector3(-1, 0, 0)
        rotationMappings[getattr(Keys, configDataSec.readString('keyRotateRight', 'KEY_RIGHTARROW'))] = Vector3(1, 0, 0)
        rotationMappings[getattr(Keys, configDataSec.readString('keyRotateUp', 'KEY_UPARROW'))] = Vector3(0, -1, 0)
        rotationMappings[getattr(Keys, configDataSec.readString('keyRotateDown', 'KEY_DOWNARROW'))] = Vector3(0, 1, 0)
        rotationMappings[getattr(Keys, configDataSec.readString('keyRotateClockwise', 'KEY_HOME'))] = Vector3(0, 0, -1)
        rotationMappings[getattr(Keys, configDataSec.readString('keyRotateCClockwise', 'KEY_END'))] = Vector3(0, 0, 1)
        rotationSensitivity = configDataSec.readFloat('angularVelocity', 0.7)
        rotationSensitivityAcc = configDataSec.readFloat('angularVelocityAcceleration', 0.8)
        rotationIncDecKeys = (getattr(Keys, configDataSec.readString('keyAngularVelocityIncrement', 'KEY_O')), getattr(Keys, configDataSec.readString('keyAngularVelocityDecrement', 'KEY_L')))
        self.__rotationSensor = KeySensor(rotationMappings, rotationSensitivity, rotationIncDecKeys, rotationSensitivityAcc)
        self.__rotationSensor.currentVelocity = Math.Vector3()
        self.__keySwitches['keySetDefaultRoll'] = getattr(Keys, configDataSec.readString('keySetDefaultRoll', 'KEY_R'))
        zoomMappings = dict()
        zoomMappings[getattr(Keys, configDataSec.readString('keyZoomGrowUp', 'KEY_INSERT'))] = -1
        zoomMappings[getattr(Keys, configDataSec.readString('keyZoomGrowDown', 'KEY_DELETE'))] = 1
        zoomSensitivity = configDataSec.readFloat('zoomVelocity', 2.0)
        zoomSensitivityAcc = configDataSec.readFloat('zoomVelocityAcceleration', 1.5)
        zoomIncDecKeys = (getattr(Keys, configDataSec.readString('keyZoomVelocityIncrement', 'KEY_NUMPADMINUS')), getattr(Keys, configDataSec.readString('keyZoomVelocityDecrement', 'KEY_ADD')))
        self.__zoomSensor = KeySensor(zoomMappings, zoomSensitivity, zoomIncDecKeys, zoomSensitivityAcc)
        self.__zoomSensor.currentVelocity = 0.0
        self.__keySwitches['keySwitchInertia'] = getattr(Keys, configDataSec.readString('keySwitchInertia', 'KEY_P'))
        self.__movementInertia = _Inertia(configDataSec.readFloat('linearFriction', 0.1))
        self.__rotationInertia = _Inertia(configDataSec.readFloat('rotationFriction', 0.1))
        self.__keySwitches['keySwitchRotateAroundPoint'] = getattr(Keys, configDataSec.readString('keySwitchRotateAroundPoint', 'KEY_C'))
        aroundPointMappings = dict()
        aroundPointMappings[getattr(Keys, configDataSec.readString('keyTargetRadiusIncrement', 'KEY_NUMPAD7'))] = 1
        aroundPointMappings[getattr(Keys, configDataSec.readString('keyTargetRadiusDecrement', 'KEY_NUMPAD1'))] = -1
        aroundPointRadiusVelocity = configDataSec.readFloat('targetRadiusVelocity', 3.0)
        self.__targetRadiusSensor = KeySensor(aroundPointMappings, aroundPointRadiusVelocity)
        self.__targetRadiusSensor.currentVelocity = 0.0
        self.__keySwitches['keySwitchLandCamera'] = getattr(Keys, configDataSec.readString('keySwitchLandCamera', 'KEY_L'))
        self.__keySwitches['keySetDefaultFov'] = getattr(Keys, configDataSec.readString('keySetDefaultFov', 'KEY_F'))
        self.__keySwitches['keyBindToVehicle'] = getattr(Keys, configDataSec.readString('keyBindToVehicle', 'KEY_B'), None)
        predefVelocitySec = configDataSec['predefinedVelocities']
        if predefVelocitySec is not None:
            for v in predefVelocitySec.items():
                key = getattr(Keys, v[0], None)
                if key is not None:
                    self.__predefinedVelocities[key] = v[1].asFloat

        predefVelocitySec = configDataSec['predefinedVerticalVelocities']
        if predefVelocitySec is not None:
            for v in predefVelocitySec.items():
                key = getattr(Keys, v[0], None)
                if key is not None:
                    self.__predefinedVerticalVelocities[key] = v[1].asFloat

        return

    def __getLookAtYPR(self, lookAtPosition):
        lookDir = lookAtPosition - self.__position
        camMat = Matrix()
        camMat.lookAt(self.__position, lookDir, Vector3(0, 1, 0))
        camMat.invert()
        yaw = camMat.yaw
        pitch = camMat.pitch
        return Vector3(yaw, pitch, self.__ypr.z)

    def __toggleView(self):
        if not isPlayerAvatar():
            return
        self.__isModeOverride = not self.__isModeOverride
        if self.__isModeOverride:
            gui_event_dispatcher.overrideCrosshairView(CTRL_MODE_NAME.POSTMORTEM)
        else:
            gui_event_dispatcher.overrideCrosshairView(CTRL_MODE_NAME.VIDEO)

    def __clampYPR(self, ypr):
        return Vector3(math.fmod(self.__ypr[0], 2 * math.pi), max(-0.9 * math.pi / 2, min(0.9 * math.pi / 2, self.__ypr[1])), math.fmod(self.__ypr[2], 2 * math.pi))

    def __calcFov(self):
        fov = BigWorld.projection().fov + self.__zoomSensor.currentVelocity
        return mathUtils.clamp(0.1, math.pi - 0.1, fov)

    def __updateSenses(self, delta):
        self.__movementSensor.update(delta)
        self.__rotationSensor.update(delta)
        self.__zoomSensor.update(delta)
        self.__targetRadiusSensor.update(delta)

    def __resetSenses(self):
        self.__movementSensor.currentVelocity = Math.Vector3()
        self.__verticalMovementSensor.currentVelocity = 0.0
        self.__rotationSensor.currentVelocity = Math.Vector3()
        self.__zoomSensor.currentVelocity = 0.0
        self.__targetRadiusSensor.currentVelocity = 0.0

    def __checkSpaceBounds(self, startPos, endPos):
        if not isPlayerAvatar():
            return endPos
        else:
            moveDir = endPos - startPos
            moveDir.normalise()
            collisionPointWithBorders = BigWorld.player().arena.collideWithSpaceBB(startPos - moveDir, endPos + moveDir)
            return collisionPointWithBorders if collisionPointWithBorders is not None else endPos

    def __processBindToVehicleKey(self):
        if BigWorld.isKeyDown(Keys.KEY_LSHIFT) or BigWorld.isKeyDown(Keys.KEY_RSHIFT):
            self.__toggleView()
        elif BigWorld.isKeyDown(Keys.KEY_LALT) or BigWorld.isKeyDown(Keys.KEY_RALT):
            worldMat = Math.Matrix(self.__cam.invViewProvider)
            self.__basisMProv.selectNextPlacement()
            boundMatrixInv = Matrix(self.__basisMProv.matrix)
            boundMatrixInv.invert()
            worldMat.postMultiply(boundMatrixInv)
            self.__position = worldMat.translation
            self.__ypr = Vector3(worldMat.yaw, worldMat.pitch, worldMat.roll)
        else:
            self.__switchBind()

    def __switchBind(self):
        if self.__basisMProv.isBound:
            self.__basisMProv.bind(None)
        else:
            self.__basisMProv.bind(*self.__entityPicker.pick())
        localMat = Matrix(self.__cam.invViewMatrix)
        basisInv = Matrix(self.__basisMProv.matrix)
        basisInv.invert()
        localMat.postMultiply(basisInv)
        self.__position = localMat.translation
        self.__ypr.set(localMat.yaw, localMat.pitch, localMat.roll)
        return

    def setViewMatrix(self, matrix):
        invMatrix = Matrix(matrix)
        invMatrix.invert()
        self.__position = invMatrix.translation
        self.__ypr = Vector3(invMatrix.yaw, invMatrix.pitch, invMatrix.roll)
