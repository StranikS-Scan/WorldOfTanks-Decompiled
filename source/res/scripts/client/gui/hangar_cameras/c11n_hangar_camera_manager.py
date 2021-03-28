# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_cameras/c11n_hangar_camera_manager.py
import math
from copy import copy
from collections import namedtuple
import BigWorld
import Math
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
from gui import g_guiResetters
from gui.hangar_cameras.hangar_camera_manager import IMMEDIATE_CAMERA_MOVEMENT_MODE
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.utils.graphics import isRendererPipelineDeferred
from items.components.c11n_constants import EASING_TRANSITION_DURATION, IMMEDIATE_TRANSITION_DURATION
from helpers import dependency
from helpers.CallbackDelayer import TimeDeltaMeter
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.customization import ICustomizationService
from vehicle_systems.tankStructure import TankPartIndexes, TankPartNames
_VERTICAL_OFFSET = 0.2
_WORLD_UP = Math.Vector3(0, 1, 0)
_STYLE_INFO_YAW = math.radians(-135)
_STYLE_INFO_PITCH = math.radians(-5)
_STYLE_INFO_MAX_CAMERA_DIST = 15
_STYLE_INFO_MAX_VEHICLE_WIDTH = 0.45
_STYLE_INFO_MAX_VEHICLE_HEIGHT = 0.3
_STYLE_INFO_VEHICLE_SCREEN_X_SHIFT = 1.0 / 3
_PROJECTION_DECALS_DIR_CLIP_COS = 0.8
DOFParams = namedtuple('DOFParams', ['nearStart',
 'nearDist',
 'farStart',
 'farDist'])

class C11nCameraModes(object):
    START_STATE = 0
    PREVIEW = 1
    EMBLEM = 2
    ANCHOR = 3
    STYLE_INFO = 4


class C11nHangarCameraManager(TimeDeltaMeter):
    _settingsCore = dependency.descriptor(ISettingsCore)
    _service = dependency.descriptor(ICustomizationService)
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        TimeDeltaMeter.__init__(self)
        self._prevCameraPosition = 0
        self.__hangarCameraManager = None
        self.__currentMode = C11nCameraModes.START_STATE
        self.__prevPitch = None
        self.__c11nCamera = None
        self.__tankCentralPoint = None
        self.__screenSpaceOffset = 0.0
        self.__ctx = None
        return

    def init(self):
        if self._hangarSpace.spaceInited:
            if self._hangarSpace.space.getCameraManager() is not None:
                self.__hangarCameraManager = self._hangarSpace.space.getCameraManager()
                self.__initCameras()
            g_eventBus.addListener(events.HangarCameraManagerEvent.ON_CREATE, self.__onCreateHangarCameraManager, scope=EVENT_BUS_SCOPE.LOBBY)
            g_eventBus.addListener(events.HangarCameraManagerEvent.ON_DESTROY, self.__onDestroyHangarCameraManager, scope=EVENT_BUS_SCOPE.LOBBY)
        g_guiResetters.add(self.__projectionChangeHandler)
        self._settingsCore.onSettingsApplied += self.__projectionChangeHandler
        self.__ctx = self._service.getCtx()
        return

    def fini(self):
        self.__ctx = None
        g_guiResetters.remove(self.__projectionChangeHandler)
        self._settingsCore.onSettingsApplied -= self.__projectionChangeHandler
        g_eventBus.removeListener(events.HangarCameraManagerEvent.ON_CREATE, self.__onCreateHangarCameraManager, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.HangarCameraManagerEvent.ON_DESTROY, self.__onDestroyHangarCameraManager, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__destroyCameras()
        return

    @property
    def vEntity(self):
        if self.__hangarCameraManager is not None:
            currentEntityId = self.__hangarCameraManager.getCurrentEntityId()
            if currentEntityId is not None:
                vEntity = BigWorld.entity(currentEntityId)
                if isinstance(vEntity, ClientSelectableCameraVehicle):
                    return vEntity
        return

    @property
    def currentMode(self):
        return self.__currentMode

    def locateCameraToCustomizationPreview(self, forceLocate=False, preserveAngles=False, updateTankCentralPoint=False):
        if self.__hangarCameraManager is None or self.__hangarCameraManager.camera is None:
            return
        else:
            from gui.ClientHangarSpace import customizationHangarCFG, hangarCFG
            cfg = customizationHangarCFG()
            hangarConfig = hangarCFG()
            self.__rotateTurretAndGun()
            if self.__tankCentralPoint is None or updateTankCentralPoint:
                self.__tankCentralPoint = self.__getTankCentralPoint()
            worldPos = self.__tankCentralPoint
            if worldPos:
                pivotPos = Math.Vector3(0, 0, 0)
            else:
                worldPos = cfg['cam_start_target_pos']
                pivotPos = cfg['cam_pivot_pos']
            if preserveAngles:
                matrix = Math.Matrix(self.__hangarCameraManager.camera.invViewMatrix)
                previewYaw = matrix.yaw
                previewPitch = self.__prevPitch or 0.0
            else:
                previewYaw = math.radians(cfg['cam_start_angles'][0])
                previewPitch = math.radians(cfg['cam_start_angles'][1])
            self._setCameraLocation(targetPos=worldPos, pivotPos=pivotPos, yaw=previewYaw, pitch=previewPitch, dist=cfg['cam_start_dist'], camConstraints=[hangarConfig['cam_pitch_constr'], hangarConfig['cam_yaw_constr'], cfg['cam_dist_constr']], forceLocate=forceLocate)
            self.__currentMode = C11nCameraModes.PREVIEW
            self.enableMovementByMouse()
            self.__prevPitch = None
            return

    def locateCameraToStartState(self, needToSetCameraLocation=True):
        if self.__hangarCameraManager is None or self.__hangarCameraManager.camera is None:
            return
        else:
            from gui.ClientHangarSpace import hangarCFG
            cfg = hangarCFG()
            if needToSetCameraLocation:
                dist = cfg['cam_start_dist']
                self.__hangarCameraManager.setCameraLocation(targetPos=cfg['cam_start_target_pos'], pivotPos=cfg['cam_pivot_pos'], yaw=math.radians(cfg['cam_start_angles'][0]), pitch=math.radians(cfg['cam_start_angles'][1]), dist=dist, camConstraints=[cfg['cam_pitch_constr'], cfg['cam_yaw_constr'], cfg['cam_dist_constr']])
                self.__hangarCameraManager.updateDynamicFov(dist=dist, rampTime=IMMEDIATE_TRANSITION_DURATION)
            self.__currentMode = C11nCameraModes.START_STATE
            self.enableMovementByMouse()
            return

    def locateCameraOnDecal(self, location, width, slotId, relativeSize=0.5, forceRotate=False):
        if self.__hangarCameraManager is None or self.__hangarCameraManager.camera is None:
            return False
        else:
            self.__savePitch()
            self.__rotateTurretAndGun(slotId)
            from gui.ClientHangarSpace import hangarCFG
            hangarCfg = hangarCFG()
            halfF = width / (2 * relativeSize)
            dist = halfF / math.tan(BigWorld.projection().fov * 0.5)
            distConstraints = self.__getDistConstraints(location.position)
            constraints = [hangarCfg['cam_pitch_constr'], hangarCfg['cam_yaw_constr'], distConstraints]
            yaw, pitch = self.__getCameraYawPitch(location.up, location.normal)
            self._setCameraLocation(targetPos=location.position, pivotPos=Math.Vector3(0, 0, 0), yaw=yaw, pitch=pitch, dist=dist, camConstraints=constraints, forceRotate=forceRotate)
            self.__currentMode = C11nCameraModes.EMBLEM
            return True

    def locateCameraOnAnchor(self, position, normal, up, slotId, forceRotate=False):
        if self.__hangarCameraManager is None or self.__hangarCameraManager.camera is None:
            return False
        else:
            self.__savePitch()
            self.__rotateTurretAndGun(slotId)
            if normal is not None:
                yaw, pitch = self.__getCameraYawPitch(up, normal, clipCos=_PROJECTION_DECALS_DIR_CLIP_COS)
            else:
                yaw = None
                pitch = None
            distConstraints = self.__getDistConstraints(position)
            from gui.ClientHangarSpace import hangarCFG
            hangarCfg = hangarCFG()
            constraints = (hangarCfg['cam_pitch_constr'], hangarCfg['cam_yaw_constr'], distConstraints)
            self._setCameraLocation(targetPos=position, pivotPos=Math.Vector3(0, 0, 0), yaw=yaw, pitch=pitch, camConstraints=constraints, forceRotate=forceRotate)
            self.__currentMode = C11nCameraModes.ANCHOR
            return True

    def locateCameraToStyleInfoPreview(self, forceLocate=False):
        if self.__hangarCameraManager is None or self.__hangarCameraManager.camera is None:
            return
        else:
            self.__savePitch()
            from gui.ClientHangarSpace import customizationHangarCFG, hangarCFG
            cfg = customizationHangarCFG()
            hangarConfig = hangarCFG()
            if self.__tankCentralPoint is None:
                self.__tankCentralPoint = self.__getTankCentralPoint()
            dist = cfg['cam_start_dist']
            targetPos = copy(self.__tankCentralPoint)
            distConstraints = copy(cfg['cam_dist_constr'])
            if self.vEntity is not None and self.vEntity.appearance is not None and self.vEntity.appearance.compoundModel is not None:
                appearance = self.vEntity.appearance
                mat = Math.Matrix()
                mat.setRotateYPR((_STYLE_INFO_YAW, -_STYLE_INFO_PITCH, 0.0))
                pivotDir = mat.applyVector(Math.Vector3(1, 0, 0))
                pivotDir = Math.Vector3(pivotDir.x, 0, pivotDir.z)
                pivotDir.normalise()
                hullAABB = appearance.collisions.getBoundingBox(TankPartIndexes.HULL)
                width = hullAABB[1].x - hullAABB[0].x
                length = hullAABB[1].z - hullAABB[0].z
                height = hullAABB[1].y - hullAABB[0].y
                hullViewSpaceX = width * abs(math.cos(_STYLE_INFO_YAW)) + length * abs(math.sin(_STYLE_INFO_YAW))
                hullViewSpaceZ = width * abs(math.sin(_STYLE_INFO_YAW)) + length * abs(math.cos(_STYLE_INFO_YAW))
                aspect = BigWorld.getAspectRatio()
                halfFOVTan = math.tan(BigWorld.projection().fov * 0.5)
                distW = hullViewSpaceX / (_STYLE_INFO_MAX_VEHICLE_WIDTH * 2 * halfFOVTan * aspect)
                distH = height / (_STYLE_INFO_MAX_VEHICLE_HEIGHT * 2 * halfFOVTan) + hullViewSpaceZ * 0.5
                dist = max(distH, distW)
                distConstraints.y = _STYLE_INFO_MAX_CAMERA_DIST
                halfHeight = dist * halfFOVTan
                halfWidth = halfHeight * aspect
                targetPos += pivotDir * halfWidth * _STYLE_INFO_VEHICLE_SCREEN_X_SHIFT
                futureCamDir = mat.applyVector(Math.Vector3(0, 0, 1))
                futureCamPos = targetPos - futureCamDir * dist
                paramsDOF = None
                if isRendererPipelineDeferred():
                    paramsDOF = self.__getStyleInfoDOFParams(futureCamPos)
                self.__ctx.events.onUpdateStyleInfoDOF(paramsDOF)
            self._setCameraLocation(targetPos=targetPos, pivotPos=-Math.Vector3(0, 0, 0), yaw=_STYLE_INFO_YAW, pitch=_STYLE_INFO_PITCH, dist=dist, camConstraints=[hangarConfig['cam_pitch_constr'], hangarConfig['cam_yaw_constr'], distConstraints], forceLocate=forceLocate, forceRotate=True)
            self.__currentMode = C11nCameraModes.STYLE_INFO
            self.enableMovementByMouse(enableRotation=False, enableZoom=False)
            return

    def isStyleInfo(self):
        return self.__currentMode == C11nCameraModes.STYLE_INFO

    def __rotateTurretAndGun(self, slotId=None):
        if self.vEntity is not None and self.vEntity.isVehicleLoaded:
            self.vEntity.appearance.rotateTurretForAnchor(slotId)
            self.vEntity.appearance.rotateGunToDefault()
        return

    def enableMovementByMouse(self, enableRotation=True, enableZoom=True):
        if self.__hangarCameraManager is not None:
            self.__hangarCameraManager.enableMovementByMouse(enableRotation=enableRotation, enableZoom=enableZoom)
        return

    def _setCameraLocation(self, targetPos=None, pivotPos=None, yaw=None, pitch=None, dist=None, camConstraints=None, ignoreConstraints=False, forceLocate=False, forceRotate=False):
        if self.__hangarCameraManager is None:
            return
        else:
            hangarCamera = self.__hangarCameraManager.camera
            transitionDuration = IMMEDIATE_TRANSITION_DURATION if forceLocate else EASING_TRANSITION_DURATION
            if self.__c11nCamera is not None and hangarCamera is not None:
                currentTarget = hangarCamera.target.translation
                if targetPos != currentTarget or forceRotate:
                    self.__c11nCamera.moveTo(targetPos, transitionDuration)
                else:
                    return
            self.__hangarCameraManager.setCameraLocation(targetPos=targetPos, pivotPos=pivotPos, yaw=yaw, pitch=pitch, dist=dist, camConstraints=camConstraints, ignoreConstraints=ignoreConstraints, movementMode=IMMEDIATE_CAMERA_MOVEMENT_MODE)
            if dist is not None:
                self.__hangarCameraManager.updateDynamicFov(dist=dist, rampTime=transitionDuration)
            return

    def __getDistConstraints(self, position, commonConstraints=None, startingPoint=None):
        if commonConstraints is None or startingPoint is None:
            from gui.ClientHangarSpace import customizationHangarCFG
            cfg = customizationHangarCFG()
            commonConstraints = commonConstraints or cfg['cam_dist_constr']
            startingPoint = startingPoint or cfg['cam_start_target_pos']
        return (commonConstraints[0], commonConstraints[1] - (position[1] - startingPoint[1]))

    def __getTankCentralPoint(self):
        if self.vEntity is not None and self.vEntity.appearance is not None and self.vEntity.appearance.compoundModel is not None and self.vEntity.appearance.collisions is not None:
            appearance = self.vEntity.appearance
            hullAABB = appearance.collisions.getBoundingBox(TankPartIndexes.HULL)
            position = Math.Vector3((hullAABB[1].x + hullAABB[0].x) / 2.0, hullAABB[1].y / 2.0, (hullAABB[1].z + hullAABB[0].z) / 2.0)
            m = Math.Matrix(appearance.compoundModel.node(TankPartNames.HULL))
            worldPos = m.applyPoint(position)
        else:
            worldPos = None
        return worldPos

    def __savePitch(self):
        if self.__hangarCameraManager is None or self.__hangarCameraManager.camera is None:
            return
        else:
            if self.__currentMode in (C11nCameraModes.START_STATE, C11nCameraModes.PREVIEW):
                currentMatrix = Math.Matrix(self.__hangarCameraManager.camera.invViewMatrix)
                self.__prevPitch = -currentMatrix.pitch
            return

    def __projectionChangeHandler(self, *args, **kwargs):
        BigWorld.callback(0.0, self.__onProjectionChanged)

    def __onProjectionChanged(self):
        if self.__currentMode == C11nCameraModes.STYLE_INFO:
            self.locateCameraToStyleInfoPreview(forceLocate=True)
        self.__c11nCamera.updateProjection()

    def __updateScreenSpaceOffset(self, val):
        if self.__screenSpaceOffset != val:
            self.__screenSpaceOffset = val
            self.__c11nCamera.updateScreenSpaceOffset(val)
            self.__c11nCamera.updateProjection()

    def __getStyleInfoDOFParams(self, cameraPos):
        if self.vEntity is None or self.vEntity.appearance is None:
            return
        else:
            compoundModel = self.vEntity.appearance.compoundModel
            chassisBounds = Math.Matrix(compoundModel.getBoundsForPart(TankPartIndexes.CHASSIS))
            outsidePoints = (chassisBounds.applyPoint((0, 1, 0)),
             chassisBounds.applyPoint((0, 1, 1)),
             chassisBounds.applyPoint((1, 1, 0)),
             chassisBounds.applyPoint((1, 1, 1)))
            dists = []
            for point in outsidePoints:
                dist = point - cameraPos
                dists.append(dist.length)

            dists.sort()
            return DOFParams(nearStart=0, nearDist=0, farStart=dists[2], farDist=1)

    def __initCameras(self):
        if self.__hangarCameraManager is None:
            return
        else:
            hangarCamera = self.__hangarCameraManager.camera
            if hangarCamera is None:
                return
            self.__c11nCamera = BigWorld.SphericalTransitionCamera(hangarCamera, _VERTICAL_OFFSET)
            targetPos = Math.Matrix(hangarCamera.target).translation
            self.__c11nCamera.moveTo(targetPos, 0.0)
            BigWorld.camera(self.__c11nCamera)
            from gui.ClientHangarSpace import customizationHangarCFG
            customCfg = customizationHangarCFG()
            hangarCamera.maxDistHalfLife = customCfg['cam_fluency']
            hangarCamera.turningHalfLife = customCfg['cam_fluency']
            hangarCamera.movementHalfLife = customCfg['cam_fluency']
            self.__hangarCameraManager.handleInactiveCamera = True
            self.__updateScreenSpaceOffset(_VERTICAL_OFFSET)
            return

    def __destroyCameras(self):
        if self.__c11nCamera is not None:
            self.__c11nCamera.stop()
        if self.__hangarCameraManager is not None and self.__hangarCameraManager.camera is not None:
            hangarCamera = self.__hangarCameraManager.camera
            from gui.ClientHangarSpace import hangarCFG
            cfg = hangarCFG()
            hangarCamera.maxDistHalfLife = cfg['cam_fluency']
            hangarCamera.turningHalfLife = cfg['cam_fluency']
            hangarCamera.movementHalfLife = cfg['cam_fluency']
            BigWorld.camera(hangarCamera)
        if self.__hangarCameraManager is not None:
            self.__hangarCameraManager.handleInactiveCamera = False
        self.__c11nCamera = None
        self.__hangarCameraManager = None
        return

    def __onCreateHangarCameraManager(self, event):
        if 'hangarCameraManager' in event.ctx:
            if self.__hangarCameraManager is not None:
                return
            self.__hangarCameraManager = event.ctx['hangarCameraManager']
            self.__initCameras()
        return

    def __onDestroyHangarCameraManager(self, _):
        self.__destroyCameras()

    def __getCameraYawPitch(self, up, normal, clipCos=None):
        if up.dot(_WORLD_UP) > 0.99:
            direction = -normal
        else:
            if up.dot(_WORLD_UP) <= 0.01:
                up = Math.Vector3(up.x, 0.05, up.z)
                up.normalise()
            direction = up * _WORLD_UP * up
            direction.normalise()
            if normal.dot(_WORLD_UP) > 0:
                direction = -direction
            if clipCos is not None and direction.dot(-normal) < clipCos:
                direction = -normal
        yaw = direction.yaw
        pitch = -direction.pitch
        return (yaw, pitch)
