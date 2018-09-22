# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_cameras/hangar_camera_manager.py
import math
from functools import partial
from logging import getLogger
import BigWorld
import Math
import Keys
from AvatarInputHandler import mathUtils
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared.utils import IHangarSpace
from helpers import dependency
from gui import g_keyEventHandlers, g_mouseEventHandlers
from gui.shared import g_eventBus
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents, CameraMovementStates
from gui.hangar_cameras.hangar_camera_idle import HangarCameraIdle
from gui.hangar_cameras.hangar_camera_parallax import HangarCameraParallax
from AvatarInputHandler.cameras import FovExtended
_logger = getLogger(__name__)

class HangarCameraYawFilter(object):

    def __init__(self, start, end, camSens):
        self.__start = start
        self.__end = end
        self.__camSens = camSens
        self.__reversed = self.__start > self.__end
        self.__cycled = int(math.degrees(math.fabs(self.__end - self.__start))) >= 359.0
        self.__prevDirection = 0.0
        self.__camSens = camSens
        self.__yawLimits = None
        self.setConstraints(start, end)
        return

    def setConstraints(self, start, end):
        self.__start = start
        self.__end = end
        if int(math.fabs(math.degrees(self.__start)) + 0.5) >= 180:
            self.__start *= 179 / 180.0
        if int(math.fabs(math.degrees(self.__end)) + 0.5) >= 180:
            self.__end *= 179 / 180.0

    def setYawLimits(self, limits):
        self.__yawLimits = limits

    def toLimit(self, inAngle):
        inAngle = mathUtils.reduceToPI(inAngle)
        if self.__cycled:
            return inAngle
        if self.__reversed:
            if inAngle >= self.__start and inAngle <= self.__end:
                return inAngle
        elif self.__start <= inAngle <= self.__end:
            return inAngle
        delta1 = self.__start - inAngle
        delta2 = self.__end - inAngle
        return self.__end if math.fabs(delta1) > math.fabs(delta2) else self.__start

    def getNextYaw(self, currentYaw, targetYaw, delta):
        if delta == 0.0 or self.__prevDirection * delta < 0.0:
            targetYaw = currentYaw
        self.__prevDirection = delta
        nextYaw = targetYaw + delta * self.__camSens
        if delta > 0.0:
            if nextYaw >= currentYaw:
                deltaYaw = nextYaw - currentYaw
            else:
                deltaYaw = 2.0 * math.pi - currentYaw + nextYaw
            if deltaYaw > math.pi:
                nextYaw = currentYaw + math.pi * 0.9
        else:
            if nextYaw <= currentYaw:
                deltaYaw = currentYaw - nextYaw
            else:
                deltaYaw = 2.0 * math.pi + currentYaw - nextYaw
            if deltaYaw > math.pi:
                nextYaw = currentYaw - math.pi * 0.9
        if not self.__cycled:
            if not self.__reversed:
                if delta > 0.0 and (nextYaw > self.__end or nextYaw < currentYaw):
                    nextYaw = self.__end
                elif delta < 0.0 and (nextYaw < self.__start or nextYaw > currentYaw):
                    nextYaw = self.__start
            elif delta > 0.0 and nextYaw > self.__end and nextYaw <= self.__start:
                nextYaw = self.__end
            elif delta < 0.0 and nextYaw < self.__start and nextYaw >= self.__end:
                nextYaw = self.__start
        if self.__yawLimits is not None:
            if nextYaw < 0.0:
                nextYaw += 2.0 * math.pi
            nextYaw = mathUtils.clamp(self.__yawLimits[0], self.__yawLimits[1], nextYaw)
        return nextYaw


class HangarCameraManager(object):
    settingsCore = dependency.descriptor(ISettingsCore)
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, spaceId):
        self.__spaceId = spaceId
        self.__cam = None
        self.__cameraIdle = None
        self.__cameraParallax = None
        self.__yawCameraFilter = None
        self.__camConstraints = [ None for _ in range(3) ]
        self.__isMouseDown = False
        self.__currentEntityId = None
        self.__movementDisabled = False
        self.__isPreviewMode = False
        return

    def init(self):
        self.__setupCamera()
        self.__isPreviewMode = False
        self.hangarSpace.onSpaceCreate += self.__onSpaceCreated
        self.hangarSpace.onSpaceDestroy += self.__onSpaceDestroy
        self.settingsCore.onSettingsChanged += self.__handleSettingsChange
        g_eventBus.addListener(CameraRelatedEvents.IDLE_CAMERA, self.__handleIdleCameraActivation)
        g_eventBus.addListener(CameraRelatedEvents.VEHICLE_LOADING, self.__handleVehicleLoading)
        g_eventBus.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleEntityUpdated)
        g_eventBus.addListener(CameraRelatedEvents.FORCE_DISABLE_CAMERA_MOVEMENT, self.__handleDisableMovement)

    def destroy(self):
        self.hangarSpace.onSpaceCreate -= self.__onSpaceCreated
        self.hangarSpace.onSpaceDestroy -= self.__onSpaceDestroy
        self.settingsCore.onSettingsChanged -= self.__handleSettingsChange
        g_eventBus.removeListener(CameraRelatedEvents.IDLE_CAMERA, self.__handleIdleCameraActivation)
        g_eventBus.removeListener(CameraRelatedEvents.VEHICLE_LOADING, self.__handleVehicleLoading)
        g_eventBus.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleEntityUpdated)
        g_eventBus.removeListener(CameraRelatedEvents.FORCE_DISABLE_CAMERA_MOVEMENT, self.__handleDisableMovement)
        if self.__cameraIdle:
            self.__cameraIdle.destroy()
            self.__cameraIdle = None
        if self.__cameraParallax:
            self.__cameraParallax.destroy()
            self.__cameraParallax = None
        if self.__cam is BigWorld.camera():
            self.__cam.spaceID = 0
            BigWorld.worldDrawEnabled(False)
        self.__cam = None
        FovExtended.instance().resetFov()
        return

    def __onSpaceCreated(self):
        g_mouseEventHandlers.add(self.__handleMouseEvent)
        g_keyEventHandlers.add(self.__handleKeyEvent)
        g_eventBus.addListener(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, self.__handleLobbyViewMouseEvent)

    def __onSpaceDestroy(self, inited):
        if inited:
            g_mouseEventHandlers.remove(self.__handleMouseEvent)
            g_keyEventHandlers.remove(self.__handleKeyEvent)
            g_eventBus.removeListener(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, self.__handleLobbyViewMouseEvent)

    def setCameraLocation(self, targetPos=None, pivotPos=None, yaw=None, pitch=None, dist=None, camConstraints=None, ignoreConstraints=False, smothiedTransition=True, previewMode=False):
        from gui.ClientHangarSpace import hangarCFG
        cfg = hangarCFG()
        sourceMat = Math.Matrix(self.__cam.source)
        if yaw is None:
            yaw = sourceMat.yaw
        if pitch is None:
            pitch = sourceMat.pitch
        if dist is None:
            dist = self.__cam.pivotMaxDist
        if camConstraints is not None:
            self.__camConstraints = camConstraints
        else:
            self.__camConstraints[0] = cfg['cam_pitch_constr']
            self.__camConstraints[1] = cfg['cam_yaw_constr']
        camYawConstr = self.__camConstraints[1]
        startYaw, endYaw = camYawConstr
        self.__yawCameraFilter.setConstraints(math.radians(startYaw), math.radians(endYaw))
        self.__yawCameraFilter.setYawLimits(camYawConstr)
        if not ignoreConstraints:
            yaw = self.__yawCameraFilter.toLimit(yaw)
            camPitchConstr = self.__camConstraints[0]
            startPitch, endPitch = camPitchConstr
            pitch = mathUtils.clamp(math.radians(startPitch), math.radians(endPitch), pitch)
            distConstr = cfg['preview_cam_dist_constr'] if self.__isPreviewMode else self.__camConstraints[2]
            minDist, maxDist = distConstr
            dist = mathUtils.clamp(minDist, maxDist, dist)
        mat = Math.Matrix()
        pitch = mathUtils.clamp(-math.pi / 2 * 0.99, math.pi / 2 * 0.99, pitch)
        mat.setRotateYPR((yaw, pitch, 0.0))
        self.__cam.source = mat
        self.__cam.pivotMaxDist = dist
        if targetPos is not None:
            self.__cam.target.setTranslate(targetPos)
        if pivotPos is not None:
            self.__cam.pivotPosition = pivotPos
        if not smothiedTransition:
            self.__cam.forceUpdate()
        self.setPreviewMode(previewMode)
        return

    def setPreviewMode(self, previewMode):
        self.__isPreviewMode = previewMode

    def isPreviewMode(self):
        return self.__isPreviewMode

    def getCurrentEntityId(self):
        return self.__currentEntityId

    def getCameraLocation(self):
        sourceMat = Math.Matrix(self.__cam.source)
        targetMat = Math.Matrix(self.__cam.target)
        return {'targetPos': targetMat.translation,
         'pivotPos': self.__cam.pivotPosition,
         'yaw': sourceMat.yaw,
         'pitch': sourceMat.pitch,
         'dist': self.__cam.pivotMaxDist,
         'camConstraints': self.__camConstraints,
         'pivotDist': self.__getCameraPivotDistance()}

    def getCameraPosition(self):
        return self.__cam.position

    def __updateCameraByMouseMove(self, dx, dy, dz):
        if self.__cam is not BigWorld.camera() or self.__movementDisabled:
            return
        sourceMat = Math.Matrix(self.__cam.source)
        yaw = sourceMat.yaw
        pitch = sourceMat.pitch
        dist = self.__cam.pivotMaxDist
        currentMatrix = Math.Matrix(self.__cam.invViewMatrix)
        currentYaw = currentMatrix.yaw
        yaw = self.__yawCameraFilter.getNextYaw(currentYaw, yaw, dx)
        from gui.ClientHangarSpace import hangarCFG
        cfg = hangarCFG()
        pitch -= dy * cfg['cam_sens']
        dist -= dz * cfg['cam_dist_sens']
        camPitchConstr = self.__camConstraints[0]
        startPitch, endPitch = camPitchConstr
        pitch = mathUtils.clamp(math.radians(startPitch), math.radians(endPitch), pitch)
        distConstr = cfg['preview_cam_dist_constr'] if self.__isPreviewMode else self.__camConstraints[2]
        minDist, maxDist = distConstr
        dist = mathUtils.clamp(minDist, maxDist, dist)
        mat = Math.Matrix()
        mat.setRotateYPR((yaw, pitch, 0.0))
        self.__cam.source = mat
        self.__cam.pivotMaxDist = dist
        if self.settingsCore.getSetting('dynamicFov') and abs(distConstr[1] - distConstr[0]) > 0.001:
            relativeDist = (dist - distConstr[0]) / (distConstr[1] - distConstr[0])
            _, minFov, maxFov = self.settingsCore.getSetting('fov')
            fov = mathUtils.lerp(minFov, maxFov, relativeDist)
            BigWorld.callback(0, partial(FovExtended.instance().setFovByAbsoluteValue, math.radians(fov), 0.1))

    def __setupCamera(self):
        from gui.ClientHangarSpace import hangarCFG
        cfg = hangarCFG()
        self.__cam = BigWorld.CursorCamera()
        self.__cam.isHangar = True
        self.__cam.spaceID = self.__spaceId
        camDistConstr = cfg['cam_dist_constr']
        minDist, maxDist = camDistConstr
        self.__cam.pivotMaxDist = mathUtils.clamp(minDist, maxDist, cfg['cam_start_dist'])
        self.__cam.pivotMinDist = 0.0
        self.__cam.maxDistHalfLife = cfg['cam_fluency']
        self.__cam.turningHalfLife = cfg['cam_fluency']
        self.__cam.movementHalfLife = cfg['cam_fluency']
        self.__cam.pivotPosition = cfg['cam_pivot_pos']
        self.__camConstraints[0] = cfg['cam_pitch_constr']
        self.__camConstraints[1] = cfg['cam_yaw_constr']
        self.__camConstraints[2] = (0.0, 0.0)
        camYawConstr = self.__camConstraints[1]
        startYaw, endYaw = camYawConstr
        self.__yawCameraFilter = HangarCameraYawFilter(math.radians(startYaw), math.radians(endYaw), cfg['cam_sens'])
        self.__yawCameraFilter.setYawLimits(camYawConstr)
        mat = Math.Matrix()
        yaw = self.__yawCameraFilter.toLimit(math.radians(cfg['cam_start_angles'][0]))
        mat.setRotateYPR((yaw, math.radians(cfg['cam_start_angles'][1]), 0.0))
        self.__cam.source = mat
        mat = Math.Matrix()
        mat.setTranslate(cfg['cam_start_target_pos'])
        self.__cam.target = mat
        self.__cam.wg_applyParams()
        BigWorld.camera(self.__cam)
        self.__cameraIdle = HangarCameraIdle(self.__cam)
        self.__cameraParallax = HangarCameraParallax(self.__cam)
        self.__cam.setDynamicCollisions(True)

    def __handleMouseEvent(self, event):
        if self.__isMouseDown:
            isGuiVisible = BigWorld.getWatcher('Visibility/GUI')
            if isGuiVisible is not None and isGuiVisible.lower() == 'false':
                self.__updateCameraByMouseMove(event.dx, event.dy, event.dz)
                return True
        return False

    def __handleKeyEvent(self, event):
        if event.key == Keys.KEY_LEFTMOUSE:
            self.__isMouseDown = event.isKeyDown()

    def __handleLobbyViewMouseEvent(self, event):
        ctx = event.ctx
        self.__updateCameraByMouseMove(ctx['dx'], ctx['dy'], ctx['dz'])

    def __handleIdleCameraActivation(self, event):
        if event.ctx['started']:
            self.__cam.pivotMaxDist = self.__getCameraPivotDistance()

    def __handleVehicleLoading(self, event):
        ctx = event.ctx
        if self.__currentEntityId != ctx['vEntityId']:
            return
        isDone = not ctx['started']
        self.__cam.isMovementEnabled = isDone
        if isDone:
            self.__updateCameraDistanceLimits()
            self.__cam.pivotMaxDist = self.__getCameraPivotDistance()
            self.__cam.forceUpdate()

    def __handleSettingsChange(self, diff):
        if 'fov' in diff:
            _, _, dynamicFOVTop = diff['fov']
            defaultHorizontalFov = math.radians(dynamicFOVTop)

            def resetFov(value):
                FovExtended.instance().defaultHorizontalFov = value

            BigWorld.callback(0.0, partial(resetFov, defaultHorizontalFov))
            self.__updateCameraByMouseMove(0.0, 0.0, 0.0)

    def __handleEntityUpdated(self, event):
        ctx = event.ctx
        if ctx['state'] != CameraMovementStates.FROM_OBJECT:
            self.__currentEntityId = ctx['entityId']
            self.__updateCameraDistanceLimits()

    def __handleDisableMovement(self, event):
        self.__movementDisabled = event.ctx['disable']

    def __updateCameraDistanceLimits(self):
        from gui.ClientHangarSpace import hangarCFG
        cfg = hangarCFG()
        entity = BigWorld.entities.get(self.__currentEntityId)
        modelLength = entity.getModelLength() if entity is not None and hasattr(entity, 'getModelLength') else 0.0
        minDist = max(modelLength * cfg['cam_min_dist_vehicle_hull_length_k'], cfg['cam_dist_constr'][0])
        maxDist = entity.cameraMaxDistance if entity is not None and hasattr(entity, 'cameraMaxDistance') else cfg['cam_dist_constr'][1]
        if maxDist < minDist:
            _logger.warning('incorrect values - camera MAX distance < camera MIN distance, use min distance as max')
            maxDist = minDist
        self.__camConstraints[2] = (minDist, maxDist)
        return

    def __getCameraPivotDistance(self):
        from gui.ClientHangarSpace import hangarCFG
        cfg = hangarCFG()
        point1 = self.__cam.target.translation + cfg['cam_pivot_pos']
        point2 = self.__cam.position
        d2 = (point2 - point1).length
        d3 = max(self.__cam.targetMaxDist, d2)
        minDist, maxDist = self.__camConstraints[2]
        return mathUtils.clamp(minDist, maxDist, d3)

    @property
    def camera(self):
        return self.__cam
