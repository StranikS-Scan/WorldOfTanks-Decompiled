# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_cameras/hangar_camera_manager.py
import math
from functools import partial
from logging import getLogger
import BigWorld
import Math
import Keys
import math_utils
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared.utils import IHangarSpace
from helpers import dependency
from gui import g_keyEventHandlers, g_mouseEventHandlers
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents, CameraMovementStates
from gui.hangar_cameras.hangar_camera_idle import HangarCameraIdle
from gui.hangar_cameras.hangar_camera_parallax import HangarCameraParallax
from AvatarInputHandler.cameras import FovExtended
from vehicle_systems.stricted_loading import makeCallbackWeak
_logger = getLogger(__name__)
IMMEDIATE_CAMERA_MOVEMENT_MODE = 0
FAST_CAMERA_MOVEMENT_MODE = 1
GRADUAL_CAMERA_MOVEMENT_MODE = 2

class HangarCameraYawFilter(object):

    def __init__(self, start, end, camSens):
        self.__start = start
        self.__end = end
        self.__camSens = camSens
        self.__reversed = self.__start > self.__end
        self.__cycled = int(math.degrees(math.fabs(self.__end - self.__start))) >= 359.0
        self.__prevDirection = 0.0
        self.__camSens = camSens
        self.setConstraints(start, end)

    def setConstraints(self, start, end):
        self.__start = start
        self.__end = end
        if int(math.fabs(math.degrees(self.__start)) + 0.5) >= 180:
            self.__start *= 179 / 180.0
        if int(math.fabs(math.degrees(self.__end)) + 0.5) >= 180:
            self.__end *= 179 / 180.0

    def toLimit(self, inAngle):
        inAngle = math_utils.reduceToPI(inAngle)
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
        return nextYaw


class HangarCameraManager(object):
    settingsCore = dependency.descriptor(ISettingsCore)
    hangarSpace = dependency.descriptor(IHangarSpace)

    @property
    def handleInactiveCamera(self):
        return self.__handleInactiveCamera

    @property
    def rotationEnabled(self):
        return self.__rotationEnabled

    @property
    def zoomEnabled(self):
        return self.__zoomEnabled

    @handleInactiveCamera.setter
    def handleInactiveCamera(self, value):
        self.__handleInactiveCamera = value

    def __init__(self, spaceId):
        self.__spaceId = spaceId
        self.__cam = None
        self.__cameraIdle = None
        self.__cameraParallax = None
        self.__yawCameraFilter = None
        self.__camConstraints = [ None for _ in range(3) ]
        self.__isMouseDown = False
        self.__currentEntityId = None
        self.__rotationEnabled = True
        self.__zoomEnabled = True
        self.__handleInactiveCamera = False
        self.__isInPlatoon = False
        self.__allowCustomCamDistance = True
        return

    def init(self):
        self.__setupCamera()
        self.hangarSpace.onSpaceCreate += self.__onSpaceCreated
        self.hangarSpace.onSpaceDestroy += self.__onSpaceDestroy
        self.settingsCore.onSettingsChanged += self.__handleSettingsChange
        g_eventBus.addListener(CameraRelatedEvents.IDLE_CAMERA, self.__handleIdleCameraActivation)
        g_eventBus.addListener(CameraRelatedEvents.VEHICLE_LOADING, self.__handleVehicleLoading)
        g_eventBus.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleEntityUpdated)
        g_eventBus.addListener(CameraRelatedEvents.FORCE_DISABLE_CAMERA_MOVEMENT, self.__handleDisableMovement)
        g_eventBus.handleEvent(events.HangarCameraManagerEvent(events.HangarCameraManagerEvent.ON_CREATE, ctx={'hangarCameraManager': self}), scope=EVENT_BUS_SCOPE.LOBBY)

    def destroy(self):
        g_eventBus.handleEvent(events.HangarCameraManagerEvent(events.HangarCameraManagerEvent.ON_DESTROY, ctx={'hangarCameraManager': self}), scope=EVENT_BUS_SCOPE.LOBBY)
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
        self.__cam.isMovementEnabled = True
        self.__cameraParallax.activate()
        g_mouseEventHandlers.add(self.__handleMouseEvent)
        g_keyEventHandlers.add(self.__handleKeyEvent)
        g_eventBus.addListener(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, self.__handleLobbyViewMouseEvent)

    def __onSpaceDestroy(self, inited):
        if inited:
            self.__cameraParallax.deactivate()
            g_mouseEventHandlers.remove(self.__handleMouseEvent)
            g_keyEventHandlers.remove(self.__handleKeyEvent)
            g_eventBus.removeListener(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, self.__handleLobbyViewMouseEvent)

    def setCameraLocation(self, targetPos=None, pivotPos=None, yaw=None, pitch=None, dist=None, camConstraints=None, ignoreConstraints=False, movementMode=FAST_CAMERA_MOVEMENT_MODE):
        if self.__cam is None:
            _logger.error('Unable to set camera location, because camera reference is None.')
            return
        else:
            from gui.ClientHangarSpace import hangarCFG
            cfg = hangarCFG()
            sourceMat = Math.Matrix(self.__cam.source)
            yawS = sourceMat.yaw if yaw is None else yaw
            pitchS = sourceMat.pitch if pitch is None else pitch
            if dist is None:
                dist = self.__cam.pivotMaxDist
            if movementMode != IMMEDIATE_CAMERA_MOVEMENT_MODE:
                self.__cam.movementMode = movementMode
            if camConstraints is None or camConstraints[0] is None:
                self.__camConstraints[0] = cfg['cam_pitch_constr']
            else:
                self.__camConstraints[0] = camConstraints[0]
            if camConstraints is None or camConstraints[1] is None:
                self.__camConstraints[1] = cfg['cam_yaw_constr']
            else:
                self.__camConstraints[1] = camConstraints[1]
            if camConstraints is None or camConstraints[2] is None:
                self.__updateCameraLimits()
            else:
                self.__camConstraints[2] = camConstraints[2]
            if not ignoreConstraints:
                if yaw is not None:
                    camYawConstr = self.__camConstraints[1]
                    startYaw, endYaw = camYawConstr
                    self.__yawCameraFilter.setConstraints(math.radians(startYaw), math.radians(endYaw))
                    yawS = self.__yawCameraFilter.toLimit(yawS)
                if pitch is not None:
                    camPitchConstr = self.__camConstraints[0]
                    startPitch, endPitch = (math.radians(pc) for pc in camPitchConstr)
                    pitchS = math_utils.clamp(startPitch, endPitch, pitchS)
                minDist, maxDist = self.__camConstraints[2]
                dist = math_utils.clamp(minDist, maxDist, dist)
            if yaw is not None or pitch is not None:
                mat = Math.Matrix()
                pitchS = math_utils.clamp(-math.pi / 2 * 0.99, math.pi / 2 * 0.99, pitchS)
                mat.setRotateYPR((yawS, pitchS, 0.0))
                self.__cam.source = mat
            if targetPos is not None:
                targetMat = self.__cam.target
                targetMat.setTranslate(targetPos)
                self.__cam.target = targetMat
                self.__cam.target.setTranslate(targetPos)
            if pivotPos is not None:
                self.__cam.pivotPosition = pivotPos
            self.__cam.pivotMaxDist = dist
            if movementMode == IMMEDIATE_CAMERA_MOVEMENT_MODE:
                self.__cam.pivotMinDist = 0.0
                self.__cam.forceUpdate()
            return

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

    def getCameraIdle(self):
        return self.__cameraIdle

    def updateProjection(self):
        BigWorld.callback(0.0, makeCallbackWeak(self.__updateProjection))

    def enableMovementByMouse(self, enableRotation=True, enableZoom=True):
        self.__rotationEnabled = enableRotation
        self.__zoomEnabled = enableZoom

    def updateDynamicFov(self, dist, rampTime):
        self.__updateDynamicFov(dist, rampTime)

    def __updateProjection(self):
        self.__cam.updateProjection()

    def __updateCameraByMouseMove(self, dx, dy, dz):
        if self.__cam is None:
            return
        elif self.__cam != BigWorld.camera() and not self.__handleInactiveCamera:
            return
        else:
            from gui.ClientHangarSpace import hangarCFG
            cfg = hangarCFG()
            self.__cam.movementMode = FAST_CAMERA_MOVEMENT_MODE
            if self.__rotationEnabled:
                sourceMat = Math.Matrix(self.__cam.source)
                yaw = sourceMat.yaw
                pitch = sourceMat.pitch
                currentMatrix = Math.Matrix(self.__cam.invViewMatrix)
                currentYaw = currentMatrix.yaw
                yaw = self.__yawCameraFilter.getNextYaw(currentYaw, yaw, dx)
                pitch -= dy * cfg['cam_sens']
                camPitchConstr = self.__camConstraints[0]
                startPitch, endPitch = camPitchConstr
                pitch = math_utils.clamp(math.radians(startPitch), math.radians(endPitch), pitch)
                mat = Math.Matrix()
                mat.setRotateYPR((yaw, pitch, 0.0))
                self.__cam.source = mat
            if self.__zoomEnabled:
                if dz < 0.0:
                    dist = self.__cam.pivotMaxDist
                else:
                    dist = self.__cam.targetMaxDist
                dist -= dz * cfg['cam_dist_sens']
                minDist, maxDist = self.__camConstraints[2]
                dist = math_utils.clamp(minDist, maxDist, dist)
                self.__cam.pivotMaxDist = dist
                self.__updateDynamicFov(dist=dist, rampTime=0.1)
            return

    def __updateDynamicFov(self, dist, rampTime):
        minDist, maxDist = self.__camConstraints[2]
        if not self.settingsCore.getSetting('dynamicFov') or abs(maxDist - minDist) <= 0.001:
            return
        relativeDist = (dist - minDist) / (maxDist - minDist)
        _, minFov, maxFov = self.settingsCore.getSetting('fov')
        fov = math_utils.lerp(minFov, maxFov, relativeDist)
        BigWorld.callback(0.0, partial(FovExtended.instance().setFovByAbsoluteValue, horizontalFov=fov, rampTime=rampTime))

    def __setupCamera(self):
        from gui.ClientHangarSpace import hangarCFG
        cfg = hangarCFG()
        self.__cam = BigWorld.CursorCamera()
        self.__cam.isHangar = True
        self.__cam.spaceID = self.__spaceId
        camDistConstr = cfg['cam_dist_constr']
        minDist, maxDist = camDistConstr
        self.__cam.pivotMaxDist = math_utils.clamp(minDist, maxDist, cfg['cam_start_dist'])
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
        mat = Math.Matrix()
        yaw = self.__yawCameraFilter.toLimit(math.radians(cfg['cam_start_angles'][0]))
        mat.setRotateYPR((yaw, math.radians(cfg['cam_start_angles'][1]), 0.0))
        self.__cam.source = mat
        mat = Math.Matrix()
        mat.setTranslate(cfg['cam_start_target_pos'])
        self.__cam.target = mat
        self.__cam.forceUpdate()
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
        if event.ctx['started'] and not self.__isInPlatoon:
            self.__cam.pivotMaxDist = self.__getCameraPivotDistance()

    def __handleVehicleLoading(self, event):
        ctx = event.ctx
        if self.__currentEntityId != ctx['vEntityId']:
            return
        isDone = not ctx['started']
        self.__cam.isMovementEnabled = isDone
        if isDone:
            self.__updateCameraLimits()
            self.__cam.pivotMaxDist = self.__getCameraPivotDistance()
            self.__cam.forceUpdate()

    def __handleSettingsChange(self, diff):
        if 'fov' in diff:
            _, _, dynamicFOVTop = diff['fov']
            horizontalFov = dynamicFOVTop

            def resetFov(value):
                FovExtended.instance().horizontalFov = value

            BigWorld.callback(0.0, partial(resetFov, horizontalFov))
            self.__updateCameraByMouseMove(0.0, 0.0, 0.0)

    def __handleEntityUpdated(self, event):
        ctx = event.ctx
        if ctx['state'] != CameraMovementStates.FROM_OBJECT:
            self.__currentEntityId = ctx['entityId']
            self.__updateCameraLimits()

    def __handleDisableMovement(self, event):
        enabled = not event.ctx['disable']
        self.enableMovementByMouse(enableRotation=enabled, enableZoom=enabled)

    def __updateCameraDistanceLimits(self):
        from gui.ClientHangarSpace import hangarCFG
        cfg = hangarCFG()
        if self.__allowCustomCamDistance and self.__isInPlatoon and cfg.camDistConstrPlatoon:
            minDist, maxDist = cfg.camDistConstrPlatoon
        else:
            entity = BigWorld.entities.get(self.__currentEntityId)
            modelLength = entity.getModelLength() if entity is not None and hasattr(entity, 'getModelLength') else 0.0
            minDist = max(modelLength * cfg['cam_min_dist_vehicle_hull_length_k'], cfg['cam_dist_constr'][0])
            maxDist = entity.cameraMaxDistance if entity is not None and hasattr(entity, 'cameraMaxDistance') else cfg['cam_dist_constr'][1]
        if maxDist < minDist:
            _logger.warning('incorrect values - camera MAX distance < camera MIN distance, use min distance as max')
            maxDist = minDist
        self.__camConstraints[2] = (minDist, maxDist)
        return

    def __updateCameraPitchLimits(self):
        from gui.ClientHangarSpace import hangarCFG
        cfg = hangarCFG()
        if self.__allowCustomCamDistance and self.__isInPlatoon and cfg.camPitchConstrPlatoon:
            minDist, maxDist = cfg.camPitchConstrPlatoon
            if maxDist < minDist:
                _logger.warning('incorrect values - camera MAX pitch < camera MIN pitch, use min distance as max')
                maxDist = minDist
            self.__camConstraints[0] = (minDist, maxDist)

    def __updateCameraLimits(self):
        self.__updateCameraDistanceLimits()
        self.__updateCameraPitchLimits()

    def __getCameraPivotDistance(self):
        from gui.ClientHangarSpace import hangarCFG
        cfg = hangarCFG()
        point1 = self.__cam.target.translation + cfg['cam_pivot_pos']
        point2 = self.__cam.position
        d2 = (point2 - point1).length
        d3 = max(self.__cam.targetMaxDist, d2)
        minDist, maxDist = self.__camConstraints[2]
        return math_utils.clamp(minDist, maxDist, d3)

    @property
    def camera(self):
        return self.__cam

    def setPlatoonCameraDistance(self, enable):
        self.__isInPlatoon = enable
        self.__updateCameraLimits()

    def setAllowCustomCamDistance(self, enable):
        self.__allowCustomCamDistance = enable
        self.__updateCameraLimits()

    def setPlatoonStartingCameraPosition(self):
        from gui.ClientHangarSpace import hangarCFG
        cfg = hangarCFG()
        startYaw, startPitch = cfg.camStartAnglesPlatoon
        mat = Math.Matrix()
        yaw = self.__yawCameraFilter.toLimit(math.radians(startYaw))
        mat.setRotateYPR((yaw, math.radians(startPitch), 0.0))
        self.__cam.source = mat
        cameraDist = cfg.camStartDistPlatoon
        minDist, maxDist = cfg.camDistConstrPlatoon
        self.setPlatoonCameraDistance(enable=True)
        self.__cam.pivotMaxDist = math_utils.clamp(minDist, maxDist, cameraDist)
        self.__cam.forceUpdate()
