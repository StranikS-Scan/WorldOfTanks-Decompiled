# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_cameras/c11n_hangar_camera_manager.py
import math
import BigWorld
import Math
import CGF
from gui.shared.utils.graphics import isRendererPipelineDeferred
from items.components.c11n_constants import EASING_TRANSITION_DURATION
from helpers import dependency
from helpers.CallbackDelayer import TimeDeltaMeter
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.customization import ICustomizationService
from vehicle_systems.tankStructure import TankPartIndexes, TankPartNames
from cgf_components.hangar_camera_manager import HangarCameraManager, DOFParams
_VERTICAL_OFFSET = 0.2
_WORLD_UP = Math.Vector3(0, 1, 0)
_STYLE_INFO_YAW = math.radians(-135)
_STYLE_INFO_PITCH = math.radians(-5)
_STYLE_INFO_MAX_CAMERA_DIST = 15
_STYLE_INFO_MAX_VEHICLE_WIDTH = 0.45
_STYLE_INFO_MAX_VEHICLE_HEIGHT = 0.3
_STYLE_INFO_VEHICLE_SCREEN_X_SHIFT = 1.0 / 3
_PROJECTION_DECALS_DIR_CLIP_COS = 0.8

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
        self.__currentMode = C11nCameraModes.START_STATE
        self.__c11nCamera = None
        self.__screenSpaceOffset = 0.0
        self.__ctx = None
        return

    def init(self):
        self.__ctx = self._service.getCtx()
        self.__currentMode = C11nCameraModes.PREVIEW
        self.__rotateTurretAndGun()

    def fini(self):
        self.__ctx = None
        self.__currentMode = C11nCameraModes.START_STATE
        return

    @property
    def vEntity(self):
        return self._hangarSpace.getVehicleEntity()

    @property
    def currentMode(self):
        return self.__currentMode

    def resetCustomizationCamera(self):
        cameraManager = CGF.getManager(self._hangarSpace.spaceID, HangarCameraManager)
        if not cameraManager:
            return
        cameraManager.resetCameraTarget(EASING_TRANSITION_DURATION)
        self.enableMovementByMouse()
        self.__rotateTurretAndGun()
        self.__currentMode = C11nCameraModes.PREVIEW

    def locateCameraOnDecal(self, location, width, slotId, relativeSize=0.5, forceRotate=False):
        cameraManager = CGF.getManager(self._hangarSpace.spaceID, HangarCameraManager)
        if not cameraManager:
            return False
        halfF = width / (2 * relativeSize)
        dist = halfF / math.tan(BigWorld.projection().fov * 0.5)
        yaw, pitch = self.__getCameraYawPitch(location.up, location.normal)
        duration = EASING_TRANSITION_DURATION if not forceRotate else 0
        cameraManager.setDOFParams(False)
        cameraManager.moveCamera(location.position, yaw, pitch, dist, duration)
        self.__rotateTurretAndGun(slotId)
        self.__currentMode = C11nCameraModes.EMBLEM
        return True

    def locateCameraOnAnchor(self, position, normal, up, slotId, forceRotate=False):
        cameraManager = CGF.getManager(self._hangarSpace.spaceID, HangarCameraManager)
        if not cameraManager:
            return False
        else:
            if normal is not None:
                yaw, pitch = self.__getCameraYawPitch(up, normal, clipCos=_PROJECTION_DECALS_DIR_CLIP_COS)
            else:
                yaw = None
                pitch = None
            duration = EASING_TRANSITION_DURATION if not forceRotate else 0
            cameraManager.setDOFParams(False)
            cameraManager.moveCamera(position, yaw, pitch, None, duration)
            self.__rotateTurretAndGun(slotId)
            self.__currentMode = C11nCameraModes.ANCHOR
            return True

    def locateCameraToStyleInfoPreview(self):
        cameraManager = CGF.getManager(self._hangarSpace.spaceID, HangarCameraManager)
        if not cameraManager:
            return False
        elif self.vEntity is None or self.vEntity.appearance is None or self.vEntity.appearance.compoundModel is None:
            return
        else:
            appearance = self.vEntity.appearance
            position = appearance.getVehicleCentralPoint()
            m = Math.Matrix(appearance.compoundModel.node(TankPartNames.HULL))
            targetPos = m.applyPoint(position)
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
            halfHeight = dist * halfFOVTan
            halfWidth = halfHeight * aspect
            targetPos += pivotDir * halfWidth * _STYLE_INFO_VEHICLE_SCREEN_X_SHIFT
            futureCamDir = mat.applyVector(Math.Vector3(0, 0, 1))
            futureCamPos = targetPos - futureCamDir * dist
            paramsDOF = None
            if isRendererPipelineDeferred():
                paramsDOF = self.__getStyleInfoDOFParams(futureCamPos)
            cameraManager.setDOFParams(True, paramsDOF)
            cameraManager.moveCamera(targetPos, _STYLE_INFO_YAW, _STYLE_INFO_PITCH, dist, EASING_TRANSITION_DURATION)
            self.enableMovementByMouse(enableRotation=False, enableZoom=False)
            self.__currentMode = C11nCameraModes.STYLE_INFO
            return

    def enableMovementByMouse(self, enableRotation=True, enableZoom=True):
        cameraManager = CGF.getManager(self._hangarSpace.spaceID, HangarCameraManager)
        if not cameraManager:
            return False
        cameraManager.enableMovementByMouse(enableRotation, enableZoom)

    def isStyleInfo(self):
        return self.__currentMode == C11nCameraModes.STYLE_INFO

    def __rotateTurretAndGun(self, slotId=None):
        if self.vEntity is not None and self.vEntity.isVehicleLoaded:
            self.vEntity.appearance.rotateTurretForAnchor(slotId)
            self.vEntity.appearance.rotateGunToDefault()
        return

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
        return (direction.yaw, -direction.pitch)
