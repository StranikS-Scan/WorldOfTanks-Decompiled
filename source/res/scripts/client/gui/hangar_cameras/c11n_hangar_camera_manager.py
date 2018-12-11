# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_cameras/c11n_hangar_camera_manager.py
import math
import BigWorld
import Math
from gui import g_guiResetters
from gui.hangar_cameras.hangar_camera_manager import IMMEDIATE_CAMERA_MOVEMENT_MODE
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer, TimeDeltaMeter
from skeletons.account_helpers.settings_core import ISettingsCore
from vehicle_systems.tankStructure import TankPartIndexes, TankPartNames
_VERTICAL_OFFSET = 0.2
_TRANSITION_DURATION = 0.8

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
        return

    def init(self):
        g_guiResetters.add(self.__onProjectionChanged)
        self._settingsCore.onSettingsApplied += self.__onProjectionChanged
        self.__hangarCamera = self.__hangarCameraManager.camera
        self.__c11nCamera = BigWorld.SphericalTransitionCamera(self.__hangarCamera, _VERTICAL_OFFSET)
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

    def locateCameraToCustomizationPreview(self, forceLocate=False, preserveAngles=False):
        if self.__hangarCamera is None or self.__hangarCameraManager is None:
            return
        else:
            from gui.ClientHangarSpace import customizationHangarCFG, hangarCFG
            cfg = customizationHangarCFG()
            hangarConfig = hangarCFG()
            worldPos = self.__getTankCentralPoint()
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
            self._setCameraLocation(targetPos=worldPos, pivotPos=pivotPos, yaw=previewYaw, pitch=previewPitch, dist=cfg['cam_start_dist'], camConstraints=[hangarConfig['cam_pitch_constr'], hangarConfig['cam_yaw_constr'], cfg['cam_dist_constr']], forceLocate=forceLocate)
            self.__currentMode = C11nCameraModes.PREVIEW
            self.__prevPitch = None
            return

    def locateCameraToStartState(self):
        if self.__hangarCameraManager is None or self.__hangarCameraManager.camera is None:
            return
        else:
            from gui.ClientHangarSpace import hangarCFG
            cfg = hangarCFG()
            self.__hangarCameraManager.setCameraLocation(targetPos=cfg['cam_start_target_pos'], pivotPos=cfg['cam_pivot_pos'], yaw=math.radians(cfg['cam_start_angles'][0]), pitch=math.radians(cfg['cam_start_angles'][1]), dist=cfg['cam_start_dist'], camConstraints=[cfg['cam_pitch_constr'], cfg['cam_yaw_constr'], cfg['cam_dist_constr']])
            self.__currentMode = C11nCameraModes.START_STATE
            return

    def locateCameraOnEmblem(self, onHull, emblemType, emblemIdx, relativeSize=0.5):
        if self.__hangarCamera is None:
            return False
        else:
            self.__savePitch()
            vEntity = BigWorld.entity(self.__hangarCameraManager.getCurrentEntityId())
            from HangarVehicle import HangarVehicle
            if not isinstance(vEntity, HangarVehicle):
                return False
            emblemPositionParams = vEntity.appearance.getEmblemPos(onHull, emblemType, emblemIdx)
            if emblemPositionParams is None:
                return False
            position = emblemPositionParams.position
            direction = emblemPositionParams.direction
            emblemPositionParams = emblemPositionParams.emblemDescription
            from gui.ClientHangarSpace import hangarCFG
            hangarCfg = hangarCFG()
            emblemSize = emblemPositionParams[3] * hangarCfg['v_scale']
            halfF = emblemSize / (2 * relativeSize)
            dist = halfF / math.tan(BigWorld.projection().fov / 2)
            distConstraints = self.__getDistConstraints(position)
            constraints = (hangarCfg['cam_pitch_constr'], hangarCfg['cam_yaw_constr'], distConstraints)
            self._setCameraLocation(targetPos=position, pivotPos=Math.Vector3(0, 0, 0), yaw=direction.yaw, pitch=-direction.pitch, dist=dist, camConstraints=constraints, previewMode=False)
            self.__currentMode = C11nCameraModes.EMBLEM
            return True

    def locateCameraOnAnchor(self, position, normal):
        if self.__hangarCamera is None:
            return False
        else:
            self.__savePitch()
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
            return True

    def clearSelectedEmblemInfo(self):
        if self.__hangarCameraManager is not None:
            self.__hangarCameraManager.setPreviewMode(False)
        return

    def _setCameraLocation(self, targetPos=None, pivotPos=None, yaw=None, pitch=None, dist=None, camConstraints=None, ignoreConstraints=False, previewMode=False, forceLocate=False):
        if self.__c11nCamera is not None and self.__hangarCamera is not None:
            currentTarget = self.__hangarCamera.target.translation
            if targetPos != currentTarget:
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
        vEntity = BigWorld.entity(self.__hangarCameraManager.getCurrentEntityId())
        from HangarVehicle import HangarVehicle
        if isinstance(vEntity, HangarVehicle) and vEntity.appearance is not None and vEntity.appearance.compoundModel is not None:
            appearance = vEntity.appearance
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
