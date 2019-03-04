# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_cameras/c11n_hangar_camera_manager.py
import math
import BigWorld
import Math
import Event
from AvatarInputHandler.cameras import FovExtended
from gui import g_guiResetters
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer, TimeDeltaMeter
from skeletons.account_helpers.settings_core import ISettingsCore
from vehicle_systems.tankStructure import TankPartIndexes, TankPartNames
from gui.hangar_cameras.hangar_camera_manager import IMMEDIATE_CAMERA_MOVEMENT_MODE
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
_VERTICAL_OFFSET = 0.2
_TRANSITION_DURATION = 0.8
_WORLD_UP = Math.Vector3(0, 1, 0)
_STYLE_INFO_HORIZONTAL_ANGLE_SHIFT = 45
_STYLE_INFO_VERTICAL_ANGLE_SHIFT = 5

class C11nCameraModes(object):
    START_STATE = 0
    PREVIEW = 1
    EMBLEM = 2
    ANCHOR = 3


class C11nHangarCameraManager(CallbackDelayer, TimeDeltaMeter):
    _settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, hangarCameraManager):
        CallbackDelayer.__init__(self)
        TimeDeltaMeter.__init__(self)
        self._prevCameraPosition = 0
        self.__hangarCameraManager = hangarCameraManager
        self.__currentMode = C11nCameraModes.START_STATE
        self.__prevPitch = None
        self.__hangarCamera = None
        self.__c11nCamera = None
        self.__tankCentralPoint = None
        self.__screenSpaceOffset = 0.0
        self._eventsManager = Event.EventManager()
        self.onTurretRotated = Event.Event(self._eventsManager)
        return

    def init(self):
        g_guiResetters.add(self.__onProjectionChanged)
        self._settingsCore.onSettingsApplied += self.__onProjectionChanged
        self.__hangarCamera = self.__hangarCameraManager.camera
        self.__c11nCamera = BigWorld.SphericalTransitionCamera(self.__hangarCamera, _VERTICAL_OFFSET)
        self.__screenSpaceOffset = _VERTICAL_OFFSET
        targetPos = Math.Matrix(self.__hangarCamera.target).translation
        self.__c11nCamera.moveTo(targetPos, 0.0)
        BigWorld.camera(self.__c11nCamera)
        self.__hangarCameraManager.handleInactiveCamera = True
        from gui.ClientHangarSpace import customizationHangarCFG
        customCfg = customizationHangarCFG()
        self.__hangarCamera.maxDistHalfLife = customCfg['cam_fluency']
        self.__hangarCamera.turningHalfLife = customCfg['cam_fluency']
        self.__hangarCamera.movementHalfLife = customCfg['cam_fluency']

    def fini(self):
        g_guiResetters.remove(self.__onProjectionChanged)
        self._settingsCore.onSettingsApplied -= self.__onProjectionChanged
        self._eventsManager.clear()
        if self.__c11nCamera is not None:
            self.__c11nCamera.stop()
        if self.__hangarCamera is not None:
            from gui.ClientHangarSpace import hangarCFG
            cfg = hangarCFG()
            self.__hangarCamera.maxDistHalfLife = cfg['cam_fluency']
            self.__hangarCamera.turningHalfLife = cfg['cam_fluency']
            self.__hangarCamera.movementHalfLife = cfg['cam_fluency']
            BigWorld.camera(self.__hangarCamera)
        self.__hangarCameraManager.handleInactiveCamera = False
        self.__hangarCamera = None
        self.__c11nCamera = None
        return

    @property
    def vEntity(self):
        vEntity = BigWorld.entity(self.__hangarCameraManager.getCurrentEntityId())
        return vEntity if isinstance(vEntity, ClientSelectableCameraVehicle) else None

    def locateCameraToCustomizationPreview(self, forceLocate=False, preserveAngles=False, disableMovementByMouse=False, updateTankCentralPoint=False):
        if self.__hangarCamera is None or self.__hangarCameraManager is None:
            return
        else:
            from gui.ClientHangarSpace import customizationHangarCFG, hangarCFG
            cfg = customizationHangarCFG()
            hangarConfig = hangarCFG()
            self.__rotateTurret()
            if self.__tankCentralPoint is None or updateTankCentralPoint:
                self.__tankCentralPoint = self.__getTankCentralPoint()
            worldPos = self.__tankCentralPoint
            if worldPos:
                pivotPos = Math.Vector3(0, 0, 0)
            else:
                worldPos = cfg['cam_start_target_pos']
                pivotPos = cfg['cam_pivot_pos']
            if preserveAngles:
                matrix = Math.Matrix(self.__hangarCamera.invViewMatrix)
                previewYaw = matrix.yaw
                previewPitch = self.__prevPitch or 0.0
            else:
                previewYaw = math.radians(cfg['cam_start_angles'][0])
                previewPitch = math.radians(cfg['cam_start_angles'][1])
            self.__updateScreenSpaceOffset(_VERTICAL_OFFSET)
            self._setCameraLocation(targetPos=worldPos, pivotPos=pivotPos, yaw=previewYaw, pitch=previewPitch, dist=cfg['cam_start_dist'], camConstraints=[hangarConfig['cam_pitch_constr'], hangarConfig['cam_yaw_constr'], cfg['cam_dist_constr']], forceLocate=forceLocate)
            self.__currentMode = C11nCameraModes.PREVIEW
            self.disableMovementByMouse(disableMovementByMouse)
            self.__prevPitch = None
            return

    def locateCameraToStartState(self):
        if self.__hangarCameraManager is None or self.__hangarCameraManager.camera is None:
            return
        else:
            from gui.ClientHangarSpace import hangarCFG
            cfg = hangarCFG()
            self.__updateScreenSpaceOffset(_VERTICAL_OFFSET)
            self.__hangarCameraManager.setCameraLocation(targetPos=cfg['cam_start_target_pos'], pivotPos=cfg['cam_pivot_pos'], yaw=math.radians(cfg['cam_start_angles'][0]), pitch=math.radians(cfg['cam_start_angles'][1]), dist=cfg['cam_start_dist'], camConstraints=[cfg['cam_pitch_constr'], cfg['cam_yaw_constr'], cfg['cam_dist_constr']])
            self.__currentMode = C11nCameraModes.START_STATE
            self.disableMovementByMouse(False)
            return

    def locateCameraOnEmblem(self, onHull, emblemType, emblemIdx, relativeSize=0.5, disableMovementByMouse=False, turretYaw=None, forceRotate=False):
        if self.__hangarCamera is None:
            return False
        else:
            self.__savePitch()
            if self.vEntity is None:
                return False
            emblemPositionParams = self.vEntity.appearance.getEmblemPos(onHull, emblemType, emblemIdx)
            if emblemPositionParams is None:
                return False
            self.__rotateTurret(turretYaw)
            position = emblemPositionParams.position
            direction = emblemPositionParams.direction
            emblemPositionParams = emblemPositionParams.emblemDescription
            from gui.ClientHangarSpace import hangarCFG
            hangarCfg = hangarCFG()
            emblemSize = emblemPositionParams.size * hangarCfg['v_scale']
            halfF = emblemSize / (2 * relativeSize)
            dist = halfF / math.tan(BigWorld.projection().fov / 2)
            distConstraints = self.__getDistConstraints(position)
            constraints = [hangarCfg['cam_pitch_constr'], hangarCfg['cam_yaw_constr'], distConstraints]
            transformMatrix = Math.Matrix()
            transformMatrix.lookAt(position, direction, emblemPositionParams.rayUp)
            transformMatrix.invert()
            emblemUp = transformMatrix.applyVector(_WORLD_UP)
            if not emblemUp.dot(_WORLD_UP) > 0.99:
                direction = emblemUp * (emblemUp * _WORLD_UP)
                direction.normalise()
            self._setCameraLocation(targetPos=position, pivotPos=Math.Vector3(0, 0, 0), yaw=direction.yaw, pitch=-direction.pitch, dist=dist, camConstraints=constraints, previewMode=False, forceRotate=forceRotate)
            self.__currentMode = C11nCameraModes.EMBLEM
            self.disableMovementByMouse(disableMovementByMouse)
            return True

    def locateCameraOnAnchor(self, position, normal, disableMovementByMouse=False, turretYaw=None):
        if self.__hangarCamera is None:
            return False
        else:
            self.__savePitch()
            self.__rotateTurret(turretYaw)
            if normal is not None:
                direction = -normal
                yaw = direction.yaw
                pitch = -direction.pitch
            else:
                yaw = None
                pitch = None
            distConstraints = self.__getDistConstraints(position)
            from gui.ClientHangarSpace import hangarCFG
            hangarCfg = hangarCFG()
            constraints = (hangarCfg['cam_pitch_constr'], hangarCfg['cam_yaw_constr'], distConstraints)
            self._setCameraLocation(targetPos=position, pivotPos=Math.Vector3(0, 0, 0), yaw=yaw, pitch=pitch, camConstraints=constraints)
            self.__currentMode = C11nCameraModes.ANCHOR
            self.disableMovementByMouse(disableMovementByMouse)
            return True

    def locateCameraToStyleInfoPreview(self):
        if self.__hangarCameraManager is None or self.__hangarCameraManager.camera is None:
            return
        elif self.__hangarCamera is None:
            return False
        else:
            self.__updateScreenSpaceOffset(0.0)
            self.__savePitch()
            from gui.ClientHangarSpace import customizationHangarCFG, hangarCFG
            cfg = customizationHangarCFG()
            hangarConfig = hangarCFG()
            if self.__tankCentralPoint is None:
                self.__tankCentralPoint = self.__getTankCentralPoint()
            previewYaw = math.radians(_STYLE_INFO_HORIZONTAL_ANGLE_SHIFT - 180)
            if self.vEntity is not None and self.vEntity.appearance is not None and self.vEntity.appearance.compoundModel is not None:
                appearance = self.vEntity.appearance
                hullAABB = appearance.collisions.getBoundingBox(TankPartIndexes.HULL)
                width = hullAABB[1].x - hullAABB[0].x
                length = hullAABB[1].z - hullAABB[0].z
                diag = math.sqrt(pow(width, 2) + pow(length, 2))
                diagProjectionAngle = math.acos(length / diag) + math.radians(_STYLE_INFO_HORIZONTAL_ANGLE_SHIFT)
                diagProjectionLength = diag * abs(math.sin(diagProjectionAngle))
            else:
                diagProjectionLength = 0
            shiftZ = -(0.2 * diagProjectionLength) / math.sin(math.radians(_STYLE_INFO_HORIZONTAL_ANGLE_SHIFT))
            shiftX = 0.2 * diagProjectionLength / math.cos(math.radians(_STYLE_INFO_HORIZONTAL_ANGLE_SHIFT))
            dist = 1.25 * diagProjectionLength / math.tan(FovExtended.calcHorizontalFov(BigWorld.projection().fov) / 2)
            worldPos = self.__tankCentralPoint - Math.Vector3(shiftX, 0, shiftZ)
            pivotPos = Math.Vector3(0, 0, 0)
            self._setCameraLocation(targetPos=worldPos, pivotPos=pivotPos, yaw=previewYaw, pitch=math.radians(_STYLE_INFO_VERTICAL_ANGLE_SHIFT), dist=dist, camConstraints=[hangarConfig['cam_pitch_constr'], hangarConfig['cam_yaw_constr'], cfg['cam_dist_constr']], forceLocate=False, ignoreConstraints=True)
            self.__currentMode = C11nCameraModes.PREVIEW
            self.disableMovementByMouse(True)
            return

    def clearSelectedEmblemInfo(self):
        if self.__hangarCameraManager is not None:
            self.__hangarCameraManager.setPreviewMode(False)
        return

    def __rotateTurret(self, turretYaw=None):
        if self.vEntity is not None:
            rotated = self.vEntity.appearance.rotateTurret(turretYaw)
            if rotated:
                BigWorld.callback(0.0, lambda : BigWorld.callback(0.0, self.__onTurretRotated))
        return

    def __onTurretRotated(self):
        if self.vEntity is not None:
            self.vEntity.appearance.updateSlotPositions(checkDecalsAgainstGun=False)
            self.onTurretRotated()
        return

    def disableMovementByMouse(self, disable):
        if self.__hangarCameraManager is not None:
            self.__hangarCameraManager.disableMovementByMouse(disable)
        return

    def _setCameraLocation(self, targetPos=None, pivotPos=None, yaw=None, pitch=None, dist=None, camConstraints=None, ignoreConstraints=False, previewMode=False, forceLocate=False, forceRotate=False):
        if self.__c11nCamera is not None and self.__hangarCamera is not None:
            currentTarget = self.__hangarCamera.target.translation
            if targetPos != currentTarget or forceRotate:
                self.__c11nCamera.moveTo(targetPos, 0.0 if forceLocate else _TRANSITION_DURATION)
            else:
                return
        self.__hangarCameraManager.setCameraLocation(targetPos=targetPos, pivotPos=pivotPos, yaw=yaw, pitch=pitch, dist=dist, camConstraints=camConstraints, ignoreConstraints=ignoreConstraints, previewMode=previewMode, movementMode=IMMEDIATE_CAMERA_MOVEMENT_MODE)
        return

    def __getDistConstraints(self, position, commonConstraints=None, startingPoint=None):
        if commonConstraints is None or startingPoint is None:
            from gui.ClientHangarSpace import customizationHangarCFG
            cfg = customizationHangarCFG()
            commonConstraints = commonConstraints or cfg['cam_dist_constr']
            startingPoint = startingPoint or cfg['cam_start_target_pos']
        return (commonConstraints[0], commonConstraints[1] - (position[1] - startingPoint[1]))

    def __getTankCentralPoint(self):
        if self.vEntity is not None and self.vEntity.appearance is not None and self.vEntity.appearance.compoundModel is not None:
            appearance = self.vEntity.appearance
            hullAABB = appearance.collisions.getBoundingBox(TankPartIndexes.HULL)
            position = Math.Vector3((hullAABB[1].x + hullAABB[0].x) / 2.0, hullAABB[1].y / 2.0, (hullAABB[1].z + hullAABB[0].z) / 2.0)
            m = Math.Matrix(appearance.compoundModel.node(TankPartNames.HULL))
            worldPos = m.applyPoint(position)
        else:
            worldPos = None
        return worldPos

    def __savePitch(self):
        if self.__currentMode in (C11nCameraModes.START_STATE, C11nCameraModes.PREVIEW):
            currentMatrix = Math.Matrix(self.__hangarCamera.invViewMatrix)
            self.__prevPitch = -currentMatrix.pitch

    def __onProjectionChanged(self, *args, **kwargs):
        self.__c11nCamera.updateProjection()

    def __updateScreenSpaceOffset(self, val):
        if self.__screenSpaceOffset != val:
            self.__screenSpaceOffset = val
            self.__c11nCamera.updateScreenSpaceOffset(val)
            self.__c11nCamera.updateProjection()
