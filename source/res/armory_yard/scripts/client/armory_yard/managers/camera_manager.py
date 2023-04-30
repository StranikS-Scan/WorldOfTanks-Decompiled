# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/managers/camera_manager.py
import BigWorld
import math
import math_utils
import Math
import CGF
import GenericComponents
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.account_helpers.settings_core import ISettingsCore
from gui.ClientHangarSpace import hangarCFG
from gui.shared import g_eventBus
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from CameraComponents import CameraComponent, OrbitComponent, ParallaxComponent
from gui.hangar_cameras.hangar_camera_parallax import HangarCameraParallax
from gui.hangar_cameras.hangar_camera_manager import IMMEDIATE_CAMERA_MOVEMENT_MODE

class CameraManager(object):

    def __init__(self):
        self.__cam = None
        self.__prevPosition = Math.Vector3(0, 0, 0)
        return

    def destroy(self):
        if self.__cam is not None:
            self.__cam.destroy()
        self.__cam = None
        return

    @dependency.replace_none_kwargs(hangarSpace=IHangarSpace)
    def goToPosition(self, data, hangarSpace=None):
        newTransform = data.findComponentByType(GenericComponents.TransformComponent)
        if self.__prevPosition == newTransform.worldPosition:
            return
        else:
            if self.__cam is None:
                self.__cam = ArmoryYardStageCamera()
                self.__cam.init()
            if hangarSpace is not None and hangarSpace.space is not None:
                self.__cam.setCamera(data)
                self.__prevPosition = newTransform.worldPosition
            return

    @dependency.replace_none_kwargs(hangarSpace=IHangarSpace)
    def goToHangar(self, hangarSpace=None):
        if hangarSpace is not None and hangarSpace.space is not None:
            hangarCameraManager = hangarSpace.space.getCameraManager()
            if hangarCameraManager is not None:
                cfg = hangarCFG()
                pos = cfg['cam_start_target_pos']
                hangarCameraManager.setCameraLocation(targetPos=pos, pivotPos=cfg['cam_pivot_pos'], yaw=math.radians(cfg['cam_start_angles'][0]), pitch=math.radians(cfg['cam_start_angles'][1]), dist=cfg['cam_start_dist'], camConstraints=[cfg['cam_pitch_constr'], cfg['cam_yaw_constr'], cfg['cam_dist_constr']], movementMode=IMMEDIATE_CAMERA_MOVEMENT_MODE)
                self.__prevPosition = pos
        return


class ArmoryYardCameraYawFilter(object):
    _EPS = 0.001

    def __init__(self, start, length, camSens):
        self.__offset = start
        self.__length = length
        self.__cycled = self.__length > 2.0 * math.pi - self._EPS
        self.__camSens = camSens
        self.__prevDirection = 0.0

    def toLimit(self, inAngle):
        inAngle = math_utils.reduceToPI(inAngle)
        inAngle = self.__normalize(inAngle)
        if not self.__cycled and inAngle > self.__length:
            if inAngle - self.__length < 2.0 * math.pi - inAngle:
                return self.__refresh(self.__length)
            return self.__refresh(0.0)
        return self.__refresh(inAngle)

    def getNextYaw(self, currentYaw, targetYaw, delta):
        if delta == 0.0:
            return targetYaw
        if self.__prevDirection * delta < 0.0:
            targetYaw = currentYaw
        self.__prevDirection = delta
        nextYaw = targetYaw + delta * self.__camSens
        if delta > 0.0:
            if nextYaw >= currentYaw:
                deltaYaw = nextYaw - currentYaw
            else:
                deltaYaw = 2.0 * math.pi + nextYaw - currentYaw
            if deltaYaw > math.pi:
                nextYaw = currentYaw + math.pi * 0.9
        else:
            if nextYaw <= currentYaw:
                deltaYaw = currentYaw - nextYaw
            else:
                deltaYaw = 2.0 * math.pi - nextYaw + currentYaw
            if deltaYaw > math.pi:
                nextYaw = currentYaw - math.pi * 0.9
        nextYaw = math_utils.reduceToPI(nextYaw)
        nextYaw = self.__normalize(nextYaw)
        currentYaw = self.__normalize(currentYaw)
        if not self.__cycled:
            if delta > 0.0 and (nextYaw > self.__length or nextYaw < currentYaw):
                return self.__refresh(self.__length)
            if delta < 0.0 and (nextYaw > self.__length or nextYaw > currentYaw):
                return self.__refresh(0.0)
        return self.__refresh(nextYaw)

    def __normalize(self, angle):
        angle -= self.__offset
        if angle < -self._EPS:
            angle += 2.0 * math.pi
        elif angle > 2.0 * math.pi + self._EPS:
            angle -= 2.0 * math.pi
        return angle

    def __refresh(self, angle):
        angle += self.__offset
        return math_utils.reduceToPI(angle)


class _MouseMoveParams(object):
    __slots__ = ('rotationSensitivity', 'zoomSensitivity', 'yawConstraints', 'pitchConstraints', 'distConstraints', 'distLength', 'shiftPivotLows', 'shiftPivotDistances')

    def __init__(self, rotationSensitivity=0.005, zoomSensitivity=0.003, yawConstraints=None, pitchConstraints=None, distConstraints=None):
        self.rotationSensitivity = rotationSensitivity
        self.zoomSensitivity = zoomSensitivity
        self.yawConstraints = yawConstraints
        self.pitchConstraints = pitchConstraints
        self.distConstraints = distConstraints
        self.distLength = 0
        self.shiftPivotDistances = Math.Vector3(0, 0, 0)
        self.shiftPivotLows = Math.Vector3(0, 0, 0)
        self.updateLength()

    def updateLength(self):
        self.distLength = 0 if self.distConstraints is None else self.distConstraints[1] - self.distConstraints[0]
        return

    def setPivotShifts(self, shiftPivotLows, shiftPivotDistances):
        self.shiftPivotLows = shiftPivotLows
        self.shiftPivotDistances = shiftPivotDistances


class ArmoryYardStageCamera(object):
    _settingsCore = dependency.descriptor(ISettingsCore)
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        self.__cam = None
        self.__parallaxCam = None
        self.__rotationEnabled = True
        self.__zoomEnabled = True
        self.__yawCameraFilter = None
        self.__mouseMoveParams = _MouseMoveParams()
        return

    def init(self):
        g_eventBus.addListener(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, self.__handleLobbyViewMouseEvent)

    def destroy(self):
        BigWorld.camera(self._hangarSpace.space.camera)
        self.__cam.spaceID = 0
        self.__cam = None
        self.__parallaxCam = None
        self.__mouseMoveParams = None
        self.__yawCameraFilter = None
        g_eventBus.removeListener(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, self.__handleLobbyViewMouseEvent)
        return

    def setCamera(self, gameObject):
        self.__cam = BigWorld.CursorCamera()
        self.__cam.spaceID = self._hangarSpace.spaceID
        self.__cam.isHangar = True
        hierarchy = CGF.HierarchyManager(self._hangarSpace.spaceID)
        cameraComponent = gameObject.findComponentByType(CameraComponent)
        parent = hierarchy.getParent(gameObject)
        parentTransformComponent = parent.findComponentByType(GenericComponents.TransformComponent)
        transformComponent = gameObject.findComponentByType(GenericComponents.TransformComponent)
        orbitComponent = gameObject.findComponentByType(OrbitComponent)
        if not cameraComponent or not orbitComponent or not parentTransformComponent or not transformComponent:
            return
        worldYaw = parentTransformComponent.worldTransform.yaw
        worldPitch = parentTransformComponent.worldTransform.pitch
        yawLimits = orbitComponent.yawLimits + Math.Vector2(worldYaw, worldYaw) + Math.Vector2(math.pi, math.pi)
        pitchLimits = orbitComponent.pitchLimits + Math.Vector2(worldPitch, worldPitch)
        yawConstraints = Math.Vector2(self.__normaliseAngle(yawLimits.x), self.__normaliseAngle(yawLimits.y))
        pitchConstraints = Math.Vector2(self.__normaliseAngle(pitchLimits.x), self.__normaliseAngle(pitchLimits.y))
        distConstraints = orbitComponent.distLimits
        self.__mouseMoveParams = _MouseMoveParams(cameraComponent.rotationSensitivity, cameraComponent.zoomSensitivity, yawConstraints, pitchConstraints, distConstraints)
        self.__yawCameraFilter = ArmoryYardCameraYawFilter(yawConstraints[0], orbitComponent.yawLimits.y - orbitComponent.yawLimits.x, cameraComponent.rotationSensitivity)
        targetPos = parentTransformComponent.worldTransform.translation
        yaw = self.__normaliseAngle(orbitComponent.startYaw + worldYaw + math.pi)
        pitch = self.__normaliseAngle(orbitComponent.startPitch + worldPitch)
        distance = orbitComponent.startDist
        yaw = self.__yawCameraFilter.toLimit(yaw)
        pitch = math_utils.clamp(self.__mouseMoveParams.pitchConstraints[0], self.__mouseMoveParams.pitchConstraints[1], pitch)
        targetMatrix = Math.Matrix()
        targetMatrix.setTranslate(targetPos)
        self.__cam.target = targetMatrix
        sourceMatrix = Math.Matrix()
        sourceMatrix.setRotateYPR(Math.Vector3(yaw, pitch, 0.0))
        self.__cam.source = sourceMatrix
        self.__cam.pivotPosition = Math.Vector3(0, 0, 0)
        self.__cam.pivotMaxDist = distance
        self.__cam.maxDistHalfLife = cameraComponent.fluency
        self.__cam.turningHalfLife = cameraComponent.fluency
        self.__cam.movementHalfLife = cameraComponent.fluency
        self.__cam.forceUpdate()
        parallaxComponent = gameObject.findComponentByType(ParallaxComponent)
        if parallaxComponent:
            self.__parallaxCam = HangarCameraParallax(self.__cam)
            self.__parallaxCam.setEnabled(True)
        BigWorld.camera(self.__cam)
        self.__cam.setDynamicCollisions(False)
        self.__cam.enableAdvancedCollider(False)

    def __normaliseAngle(self, angle):
        eps = 0.001
        if angle > math.pi + eps:
            return angle - 2 * math.pi
        return angle + 2 * math.pi if angle < -math.pi - eps else angle

    def __calculateDynamicFov(self):
        minDist, maxDist = self.__mouseMoveParams.distConstraints
        if self.__customFov or not self._settingsCore.getSetting('dynamicFov') or abs(maxDist - minDist) <= 0.001:
            return None
        else:
            relativeDist = (self.__cam.pivotMaxDist - minDist) / (maxDist - minDist)
            _, minFov, maxFov = self._settingsCore.getSetting('fov')
            return math_utils.lerp(minFov, maxFov, relativeDist)

    def __updateCameraByMouseMove(self, dx, dy, dz):
        sourceMat = Math.Matrix(self.__cam.source)
        yaw = sourceMat.yaw
        pitch = sourceMat.pitch
        if self.__rotationEnabled:
            currentMatrix = Math.Matrix(self.__cam.invViewMatrix)
            currentYaw = currentMatrix.yaw
            yaw = self.__yawCameraFilter.getNextYaw(currentYaw, yaw, dx)
            pitch -= dy * self.__mouseMoveParams.rotationSensitivity
            pitch = math_utils.clamp(self.__mouseMoveParams.pitchConstraints[0], self.__mouseMoveParams.pitchConstraints[1], pitch)
            mat = Math.Matrix()
            mat.setRotateYPR((yaw, pitch, 0.0))
            self.__cam.source = mat
        if self.__zoomEnabled:
            if dz < 0.0:
                dist = self.__cam.pivotMaxDist
            else:
                dist = self.__cam.targetMaxDist
            dist -= dz * self.__mouseMoveParams.zoomSensitivity
            dist = math_utils.clamp(self.__mouseMoveParams.distConstraints[0], self.__mouseMoveParams.distConstraints[1], dist)
            if self.__mouseMoveParams.distLength > 0.0:
                prc = (dist - self.__mouseMoveParams.distConstraints[0]) / self.__mouseMoveParams.distLength
                pivotPos = self.__mouseMoveParams.shiftPivotDistances * prc
            else:
                pivotPos = Math.Vector3(0.0, 0.0, 0.0)
            self.__cam.pivotPosition = pivotPos + self.__mouseMoveParams.shiftPivotLows
            self.__cam.pivotMaxDist = dist

    def __handleLobbyViewMouseEvent(self, event):
        ctx = event.ctx
        self.__updateCameraByMouseMove(ctx['dx'], ctx['dy'], ctx['dz'])
