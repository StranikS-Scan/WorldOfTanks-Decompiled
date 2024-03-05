# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/DynamicCameras/AssaultCamera.py
import math
from math import pi, copysign, atan2
import BigWorld
from Math import Vector3, Matrix, MatrixProduct
import BattleReplay
import Settings
import math_utils
from AvatarInputHandler import aih_global_binding
from AvatarInputHandler.DynamicCameras import CameraWithSettings
from AvatarInputHandler.cameras import readFloat, readInt, readVec2
from ProjectileMover import collideDynamicAndStatic
from debug_utils import LOG_WARNING, LOG_DEBUG_DEV
from helpers.CallbackDelayer import CallbackDelayer
MAX_COLLISION_DISTANCE = 3500.0
MAX_COLLISION_DISTANCE_FROM_SCREEN = 5500.0
COLLISION_EPS = 0.01

def getCameraAsSettingsHolder(settingsDataSec):
    return AssaultCamera(settingsDataSec)


class AssaultCamera(CameraWithSettings, CallbackDelayer):
    _DYNAMIC_ENABLED = True

    @staticmethod
    def enableDynamicCamera(enable):
        AssaultCamera._DYNAMIC_ENABLED = enable

    @staticmethod
    def isCameraDynamic():
        return AssaultCamera._DYNAMIC_ENABLED

    camera = property(lambda self: self.__cam)
    aimingSystem = property(lambda self: self._aimingSystem)
    __aimOffset = aih_global_binding.bindRW(aih_global_binding.BINDING_ID.AIM_OFFSET)

    def __init__(self, dataSec):
        super(AssaultCamera, self).__init__()
        CallbackDelayer.__init__(self)
        self.isAimOffsetEnabled = True
        self._readConfigs(dataSec)
        self.__cam = BigWorld.CursorCamera()
        self.__curSense = self._cfg['sensitivity']
        self._aimingSystem = None
        self.__prevTime = 0.0
        self.__prevAimPoint = Vector3()
        self.__dxdydz = Vector3(0.0, 0.0, 0.0)
        self.__autoUpdatePosition = False
        self.__sourceMatrix = None
        self.__targetMatrix = None
        self.__cameraDirection = Vector3(0.0, 0.0, 0.0)
        states = self._cfg['states']
        self.__countOfStates = self._cfg['statesCount']
        self.__currentState = self._cfg['initialStateIndex']
        self.__curDistRange = states[self.__currentState]['distRange']
        self.__boundaryDistRange = (states[0]['distRange'][0], states[len(states) - 1]['distRange'][-1])
        self.__curPitchAngle = self._cfg['states'][self.__currentState]['angle']
        self.__minPitchAngle = self._cfg['states'][0]['angle']
        self.__maxPitchAngle = self._cfg['states'][self.__countOfStates - 1]['angle']
        self.__collisionSphereRadius = self._cfg['collisionSphereRadius']
        self.__prevVehiclePosition = Vector3()
        return

    @staticmethod
    def _getConfigsKey():
        return AssaultCamera.__name__

    @staticmethod
    def _createAimingSystem():
        return BigWorld.AssaultAimingSystem()

    def getZoom(self):
        return 1 - float(self.__currentState) / (self.__countOfStates - 1)

    def __getTargetYawDirection(self, targetPos):
        position, _, _ = BigWorld.player().gunRotator.getShotParams(targetPos)
        vehToCamDir = targetPos - position
        vehToCamDir.normalise()
        cameraYaw = atan2(vehToCamDir.x, vehToCamDir.z)
        return cameraYaw

    def getMinStateDirection(self, targetPos):
        cameraYaw = self.__getTargetYawDirection(targetPos)
        direction = Vector3()
        direction.setPitchYaw(self.__minPitchAngle, cameraYaw)
        return direction

    def getMaxStateDirection(self, targetPos):
        cameraYaw = self.__getTargetYawDirection(targetPos)
        direction = Vector3()
        direction.setPitchYaw(self.__maxPitchAngle, cameraYaw)
        return direction

    def create(self, onChangeControlMode=None):
        super(AssaultCamera, self).create()
        self._aimingSystem = self._createAimingSystem()
        self.__cam.pivotMaxDist = 0.0
        self.__cam.maxDistHalfLife = 0.01
        self.__cam.movementHalfLife = 0.0
        self.__cam.turningHalfLife = -1
        self.__cam.pivotPosition = Vector3(0.0, 0.0, 0.0)
        self.__sourceMatrix = Matrix()
        self.__targetMatrix = Matrix()

    def destroy(self):
        self.disable()
        self.__cam = None
        if self._aimingSystem is not None:
            self._aimingSystem.destroy()
            self._aimingSystem = None
        CallbackDelayer.destroy(self)
        CameraWithSettings.destroy(self)
        return

    def setup(self, targetPos):
        if self.__trySetupCamera(targetPos, self.__currentState):
            return True
        for stateIndex in range(self.__countOfStates):
            if stateIndex != self.__currentState and self.__trySetupCamera(targetPos, stateIndex):
                return True

        return False

    def __trySetupCamera(self, targetPos, stateIndex):
        distRange = self._cfg['states'][stateIndex]['distRange']
        pitchAngle = self._cfg['states'][stateIndex]['angle']
        camTarget = MatrixProduct()
        position, _, _ = BigWorld.player().gunRotator.getShotParams(targetPos)
        vehToCamDir = targetPos - position
        vehToCamDir.normalise()
        cameraYaw = atan2(vehToCamDir.x, vehToCamDir.z)
        self.__cam.target = camTarget
        self.__cam.target.b = self.__targetMatrix
        self.__sourceMatrix = math_utils.createRotationMatrix((cameraYaw, -pitchAngle, 0.0))
        self.__cam.source = self.__sourceMatrix
        self.__cam.forceUpdate()
        self.__cameraDirection = self.__cam.direction
        targetPos -= self.__cameraDirection.scale(COLLISION_EPS)
        collisionDist = -1.0
        collision = collideDynamicAndStatic(targetPos, targetPos - self.__cameraDirection.scale(distRange[1] + self.__collisionSphereRadius), (BigWorld.player().playerVehicleID,), 0, skipGun=True)
        if collision is not None:
            collisionDist = (collision[0] - targetPos).length
        if collisionDist < 0.0:
            collisionDist = distRange[1] + self.__collisionSphereRadius
        if 0.0 <= collisionDist < distRange[0] or collisionDist <= 2.0 * self.__collisionSphereRadius:
            LOG_DEBUG_DEV('AssaultCamera.setup: collisionDist is too small', collisionDist)
            return False
        else:
            startSafePos = targetPos - self.__cameraDirection.scale(self.__collisionSphereRadius)
            endSafePos = targetPos - self.__cameraDirection.scale(collisionDist - self.__collisionSphereRadius)
            planeDistance = self._aimingSystem.clampAimingMovement(startSafePos, self.__cameraDirection)
            desiredSpherePosition = self._aimingSystem.planePosition - self.__cameraDirection.scale(planeDistance)
            testCollisionVec = desiredSpherePosition - startSafePos
            safeSpherePositionAdvance = self._aimingSystem.findSphereNoCollisionAdvance(startSafePos, endSafePos, testCollisionVec, self.__collisionSphereRadius)
            if safeSpherePositionAdvance < 0.0:
                LOG_DEBUG_DEV('AssaultCamera.setup: Could not find safe position for camera after clamping!')
                return False
            safeSpherePosition = startSafePos + (endSafePos - startSafePos) * safeSpherePositionAdvance + testCollisionVec
            newTargetPosDist = self.__getCollsionDist(safeSpherePosition)
            additionalOffset = distRange[1] - newTargetPosDist
            destinationOffset = safeSpherePosition - self.__cameraDirection.scale(additionalOffset)
            sphereCollisionOffset = self._aimingSystem.getSphereCollsionDist(safeSpherePosition, destinationOffset, self.__collisionSphereRadius)
            if sphereCollisionOffset < 0.0:
                sphereCollisionOffset = additionalOffset
            if 0.0 <= newTargetPosDist + sphereCollisionOffset < distRange[0]:
                LOG_DEBUG_DEV('AssaultCamera.setup: Final sphere is too close to target point', newTargetPosDist + sphereCollisionOffset)
                return False
            self.__targetMatrix.translation = safeSpherePosition - self.__cameraDirection.scale(sphereCollisionOffset)
            self.__currentState = stateIndex
            self.__curDistRang = distRange
            self.__curPitchAngle = pitchAngle
            return True

    def enable(self, targetPos, saveDist, switchToPos=None, switchToPlace=None):
        BigWorld.wg_trajectory_drawer().setStrategicMode(False)
        self.__prevTime = 0.0
        self.__prevVehiclePosition = BigWorld.player().getVehicleAttached().position
        BigWorld.camera(self.__cam)
        BigWorld.player().positionControl.moveTo(targetPos)
        BigWorld.player().positionControl.followCamera(False)
        self.__cameraUpdate()
        self.delayCallback(0.01, self.__cameraUpdate)

    def disable(self):
        if self._aimingSystem is not None:
            self._aimingSystem.disable()
        self.stopCallback(self.__cameraUpdate)
        return

    def update(self, dx, dy, dz, updateByKeyboard=False):
        self.__curSense = self._cfg['keySensitivity'] if updateByKeyboard else self._cfg['sensitivity']
        self.__autoUpdatePosition = updateByKeyboard
        self.__dxdydz = Vector3(dx if not self._cfg['horzInvert'] else -dx, dy if not self._cfg['vertInvert'] else -dy, dz)

    def writeUserPreferences(self):
        ds = Settings.g_instance.userPrefs
        if not ds.has_key(Settings.KEY_CONTROL_MODE):
            ds.write(Settings.KEY_CONTROL_MODE, '')
        ucfg = self._userCfg
        ds = ds[Settings.KEY_CONTROL_MODE]
        ds.writeBool('assaultSPG/camera/horzInvert', ucfg['horzInvert'])
        ds.writeBool('assaultSPG/camera/vertInvert', ucfg['vertInvert'])
        ds.writeFloat('assaultSPG/camera/keySensitivity', ucfg['keySensitivity'])
        ds.writeFloat('assaultSPG/camera/sensitivity', ucfg['sensitivity'])

    def getCamDistRange(self):
        return self.__boundaryDistRange

    def getCamTransitionDist(self):
        return self.__boundaryDistRange[-1] / 2

    def getCurrentCamDist(self):
        return self.__targetMatrix.translation.y

    def getCountOfStates(self):
        return self.__countOfStates

    def __updateTrajectoryDrawer(self):
        shotDescr = BigWorld.player().getVehicleDescriptor().shot
        BigWorld.wg_trajectory_drawer().setParams(shotDescr.maxDistance, Vector3(0, -shotDescr.gravity, 0), self.__aimOffset)

    def __updateTime(self):
        curTime = BigWorld.timeExact()
        deltaTime = curTime - self.__prevTime
        self.__prevTime = curTime
        return deltaTime

    def __updateState(self):
        if self.__dxdydz.z < 0:
            self.__currentState += 1
        elif self.__dxdydz.z > 0:
            self.__currentState -= 1
        self.__currentState = math_utils.clamp(0, self.__countOfStates - 1, self.__currentState)
        self.__curDistRange = self._cfg['states'][self.__currentState]['distRange']
        self.__curPitchAngle = self._cfg['states'][self.__currentState]['angle']

    def __handleMovement(self):
        vehiclePosition = BigWorld.player().getVehicleAttached().position
        vehicleMoveDiff = vehiclePosition - self.__prevVehiclePosition
        vehicleMoveDiff.y = 0.0
        self.__prevVehiclePosition = vehiclePosition
        rotMat = math_utils.createRotationMatrix((self.__sourceMatrix.yaw, 0, 0))
        moveVector = rotMat.applyVector(Vector3(self.__dxdydz.x * self.__curSense, 0, -self.__dxdydz.y * self.__curSense))
        desiredPosition = self.__targetMatrix.translation + moveVector + vehicleMoveDiff
        return self._aimingSystem.resolveCameraCollisions(self.__targetMatrix.translation, desiredPosition, self.__collisionSphereRadius)

    def __getShiftCameraPosition(self, startPos, desiredPos, shiftCollisionDist):
        anglePosDir = desiredPos - startPos
        anglePosDir.normalise()
        newAnglePos = startPos + anglePosDir * shiftCollisionDist
        return newAnglePos

    def __resolveYawShiftCollisions(self, startPos, desiredPos, targetPos):
        shiftCollisionDist = self._aimingSystem.getSphereCollsionDist(startPos, desiredPos, self.__collisionSphereRadius)
        if shiftCollisionDist >= 0.0:
            newAnglePos = self.__getShiftCameraPosition(startPos, desiredPos, shiftCollisionDist)
            newCamDir = targetPos - newAnglePos
            newCamDir.normalise()
            newYaw = math.atan2(newCamDir.x, newCamDir.z)
            self.__cameraDirection.setPitchYaw(self.__cameraDirection.pitch, newYaw)
            return newAnglePos
        return desiredPos

    def __resolvePitchShiftCollisions(self, startPos, desiredPos, targetPos):
        shiftCollisionDist = self._aimingSystem.getSphereCollsionDist(startPos, desiredPos, self.__collisionSphereRadius)
        if shiftCollisionDist >= 0.0:
            newAnglePos = self.__getShiftCameraPosition(startPos, desiredPos, shiftCollisionDist)
            newCamDir = targetPos - newAnglePos
            newCamDir.normalise()
            newPitch = math.asin(newCamDir.y)
            self.__cameraDirection.setPitchYaw(-newPitch, self.__cameraDirection.yaw)
            return newAnglePos
        return desiredPos

    def __getCollsionDist(self, startPos):
        endPoint = startPos + self.__cameraDirection.scale(MAX_COLLISION_DISTANCE)
        collision = collideDynamicAndStatic(startPos, endPoint, (BigWorld.player().playerVehicleID,), 0)
        if collision is not None:
            self._aimingSystem.aimPoint = collision[0]
        collisionDist = (startPos - self._aimingSystem.aimPoint).length
        waterCollisionDist = BigWorld.wg_collideWater(startPos, endPoint, False)
        if -1.0 < waterCollisionDist < collisionDist:
            collisionDist = waterCollisionDist
            targetDiff = self._aimingSystem.aimPoint - startPos
            targetDiff.normalise()
            self._aimingSystem.aimPoint = startPos + targetDiff.scale(collisionDist)
        return collisionDist

    def __getDistInterpolationParam(self, collisionDist, deltaTime):
        if collisionDist < self.__curDistRange[0]:
            return math_utils.clamp(0.0, 1.0, self._cfg['rMinInterpolationSpeed'] * deltaTime)
        return math_utils.clamp(0.0, 1.0, self._cfg['rDefaultInterpolationSpeed'] * deltaTime) if collisionDist < self.__curDistRange[1] else math_utils.clamp(0.0, 1.0, self._cfg['rMaxInterpolationSpeed'] * deltaTime)

    def __cameraUpdate(self):
        deltaTime = self.__updateTime()
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isControllingCamera:
            self.__cam.forceUpdate()
            endPoint = self.camera.position + self.__cam.direction.scale(MAX_COLLISION_DISTANCE)
            collision = collideDynamicAndStatic(self.camera.position, endPoint, (BigWorld.player().playerVehicleID, 0))
            if collision is not None:
                self._aimingSystem.aimPoint = collision[0]
            waterCollisionDist = BigWorld.wg_collideWater(self.camera.position, endPoint, False)
            if waterCollisionDist > -1.0 and (collision is None or waterCollisionDist < (collision[0] - self.camera.position).length):
                self._aimingSystem.aimPoint = self.camera.position + self.__cam.direction * waterCollisionDist
            self.__updateTrajectoryDrawer()
            return 0.01
        else:
            self.__updateState()
            newMovePos = self.__handleMovement()
            distance = self._aimingSystem.clampAimingMovement(newMovePos, self.__cameraDirection)
            desiredClampedPos = self._aimingSystem.planePosition - self.__cameraDirection.scale(distance)
            clampSphereCollisionDist = self._aimingSystem.getSphereCollsionDist(newMovePos, desiredClampedPos, self.__collisionSphereRadius)
            if clampSphereCollisionDist >= 0.0:
                newMovePos = self.__targetMatrix.translation
                self._aimingSystem.updatePlanePoint(newMovePos, self.__cameraDirection)
            position, _, _ = BigWorld.player().gunRotator.getShotParams(self._aimingSystem.planePosition)
            vehToCamDir = self._aimingSystem.planePosition - position
            vehToCamDir.normalise()
            yaw = math.atan2(vehToCamDir.x, vehToCamDir.z)
            self.__cameraDirection.setPitchYaw(self.__cameraDirection.pitch, yaw)
            newYawPos = self._aimingSystem.planePosition - self.__cameraDirection.scale(distance)
            newYawPos = self.__resolveYawShiftCollisions(newMovePos, newYawPos, self._aimingSystem.planePosition)
            self.__targetMatrix.translation = newYawPos
            collisionDist = self.__getCollsionDist(self.__targetMatrix.translation)
            angleLerpParam = math_utils.clamp(0.0, 1.0, self._cfg['angleInterpolationSpeed'] * deltaTime)
            pitch = -self.__cameraDirection.pitch
            pitch = math_utils.lerp(pitch, -self.__curPitchAngle, angleLerpParam)
            self.__cameraDirection.setPitchYaw(-pitch, self.__cameraDirection.yaw)
            desiredPitchPos = self._aimingSystem.aimPoint - self.__cameraDirection.scale(collisionDist)
            desiredPitchPos = self.__resolvePitchShiftCollisions(self.__targetMatrix.translation, desiredPitchPos, self._aimingSystem.aimPoint)
            self.__targetMatrix.translation = desiredPitchPos
            collisionDist = self.__getCollsionDist(self.__targetMatrix.translation)
            desiredCollisionDist = self.__curDistRange[1]
            collisionDistDiff = desiredCollisionDist - collisionDist
            desiredPos = self.__targetMatrix.translation - self.__cameraDirection.scale(collisionDistDiff)
            sphereCollisionDist = self._aimingSystem.getSphereCollsionDist(self.__targetMatrix.translation, desiredPos, self.__collisionSphereRadius)
            if sphereCollisionDist >= 0.0:
                sphereCollisionDist -= COLLISION_EPS
                desiredCollisionDist = collisionDist + copysign(sphereCollisionDist, collisionDistDiff)
            distLerpParam = self.__getDistInterpolationParam(collisionDist, deltaTime)
            newDistance = math_utils.lerp(collisionDist, desiredCollisionDist, distLerpParam)
            if self.aimingSystem.aimPoint.distSqrTo(self.__prevAimPoint) > 0.010000000000000002:
                BigWorld.player().positionControl.moveTo(self._aimingSystem.aimPoint)
                self.__prevAimPoint = self._aimingSystem.aimPoint
            self.__targetMatrix.translation = self._aimingSystem.aimPoint - self.__cameraDirection.scale(newDistance)
            self.__sourceMatrix = math_utils.createRotationMatrix((self.__cameraDirection.yaw, -self.__cameraDirection.pitch, 0))
            self.__cam.source = self.__sourceMatrix
            self.__cam.forceUpdate()
            if not self.__autoUpdatePosition:
                self.__dxdydz = Vector3(0, 0, 0)
            self.__updateTrajectoryDrawer()
            return 0.01

    def _readConfigs(self, dataSec):
        if not dataSec:
            LOG_WARNING('Invalid section <assaultSPG/camera> in avatar_input_handler.xml')
        super(AssaultCamera, self)._readConfigs(dataSec)

    def _readBaseCfg(self, dataSec):
        bcfg = self._baseCfg
        bcfg['keySensitivity'] = readFloat(dataSec, 'keySensitivity', 0.005, 10.0, 0.025)
        bcfg['sensitivity'] = readFloat(dataSec, 'sensitivity', 0.005, 10.0, 0.025)
        bcfg['collisionSphereRadius'] = readFloat(dataSec, 'collisionSphereRadius', 1.0, 5.0, 5.0)
        bcfg['rMinInterpolationSpeed'] = readFloat(dataSec, 'rMinInterpolationSpeed', 0.005, 10.0, 7.0)
        bcfg['rDefaultInterpolationSpeed'] = readFloat(dataSec, 'rDefaultInterpolationSpeed', 0.005, 10.0, 0.005)
        bcfg['rMaxInterpolationSpeed'] = readFloat(dataSec, 'rMaxInterpolationSpeed', 0.005, 10.0, 0.005)
        bcfg['angleInterpolationSpeed'] = readFloat(dataSec, 'angleInterpolationSpeed', 0.005, 10.0, 7.0)
        self._readStatesCfg(dataSec)

    def _readStatesCfg(self, dataSec):
        bcfg = self._baseCfg
        stateSectionName = 'states/'
        bcfg['statesCount'] = readInt(dataSec, stateSectionName + 'count', 0, 100, 0)
        bcfg['initialStateIndex'] = readInt(dataSec, stateSectionName + 'initialStateIndex', 0, 100, 0)
        bcfg['states'] = {}
        for index in range(0, bcfg['statesCount']):
            subsectionStateName = 'state_' + str(index) + '/'
            bcfg['states'][index] = {}
            bcfg['states'][index]['distRange'] = readVec2(dataSec, stateSectionName + subsectionStateName + 'distRange', (0.0, 0.0), (1000.0, 1000.0), (0.0, 1000.0))
            bcfg['states'][index]['angle'] = readFloat(dataSec, stateSectionName + subsectionStateName + 'angle', 0.0, 90.0, 45.0) / 180.0 * pi

    def _readUserCfg(self):
        ucfg = self._userCfg
        dataSec = Settings.g_instance.userPrefs[Settings.KEY_CONTROL_MODE]
        if dataSec is not None:
            dataSec = dataSec['assaultSPG/camera']
        ucfg['horzInvert'] = False
        ucfg['vertInvert'] = False
        ucfg['keySensitivity'] = readFloat(dataSec, 'keySensitivity', 0.0, 10.0, 1.0)
        ucfg['sensitivity'] = readFloat(dataSec, 'sensitivity', 0.0, 10.0, 1.0)
        return

    def _makeCfg(self):
        bcfg = self._baseCfg
        ucfg = self._userCfg
        cfg = self._cfg
        cfg['keySensitivity'] = bcfg['keySensitivity']
        cfg['sensitivity'] = bcfg['sensitivity']
        cfg['statesCount'] = bcfg['statesCount']
        cfg['initialStateIndex'] = bcfg['initialStateIndex']
        cfg['states'] = bcfg['states']
        cfg['keySensitivity'] *= ucfg['keySensitivity']
        cfg['sensitivity'] *= ucfg['sensitivity']
        cfg['horzInvert'] = ucfg['horzInvert']
        cfg['vertInvert'] = ucfg['vertInvert']
        cfg['collisionSphereRadius'] = bcfg['collisionSphereRadius']
        cfg['rMinInterpolationSpeed'] = bcfg['rMinInterpolationSpeed']
        cfg['rDefaultInterpolationSpeed'] = bcfg['rDefaultInterpolationSpeed']
        cfg['rMaxInterpolationSpeed'] = bcfg['rMaxInterpolationSpeed']
        cfg['angleInterpolationSpeed'] = bcfg['angleInterpolationSpeed']
