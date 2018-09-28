# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_cameras/c11n_hangar_camera_manager.py
import math
import BigWorld
import Math
from gui import g_guiResetters
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer, TimeDeltaMeter
from skeletons.account_helpers.settings_core import ISettingsCore
from vehicle_systems.tankStructure import TankPartIndexes, TankPartNames
_VERTICAL_OFFSET = 0.2

class C11nHangarCameraManager(CallbackDelayer, TimeDeltaMeter):
    _settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, hangarCameraManager):
        CallbackDelayer.__init__(self)
        TimeDeltaMeter.__init__(self)
        self._prevCameraPosition = 0
        self.__hangarCameraManager = hangarCameraManager
        self.__selectedEmblemInfo = None
        self.__prevPitch = None
        return

    def init(self):
        g_guiResetters.add(self.__onProjectionChanged)
        self._settingsCore.onSettingsApplied += self.__onProjectionChanged

    def fini(self):
        g_guiResetters.remove(self.__onProjectionChanged)
        self._settingsCore.onSettingsApplied -= self.__onProjectionChanged

    def locateCameraToPreview(self):
        if self.__hangarCameraManager is None or self.__hangarCameraManager.camera is None:
            return
        else:
            from gui.ClientHangarSpace import hangarCFG
            cfg = hangarCFG()
            self._setCameraLocation(targetPos=cfg['preview_cam_start_target_pos'], pivotPos=cfg['preview_cam_pivot_pos'], yaw=math.radians(cfg['preview_cam_start_angles'][0]), pitch=math.radians(cfg['preview_cam_start_angles'][1]), dist=cfg['preview_cam_start_dist'])
            return

    def locateCameraToCustomizationPreview(self, preserveAngles=False, forceLocate=False):
        if self.__hangarCameraManager is None or self.__hangarCameraManager.camera is None:
            return
        else:
            from gui.ClientHangarSpace import customizationHangarCFG, hangarCFG
            cfg = customizationHangarCFG()
            hangarConfig = hangarCFG()
            vEntity = BigWorld.entity(self.__hangarCameraManager.getCurrentEntityId())
            from HangarVehicle import HangarVehicle
            pivotPos = cfg['cam_pivot_pos']
            if isinstance(vEntity, HangarVehicle):
                appearance = vEntity.appearance
                hullAABB = appearance.collisions.getBoundingBox(TankPartIndexes.HULL)
                position = Math.Vector3((hullAABB[1].x + hullAABB[0].x) / 2.0, hullAABB[1].y / 2.0, (hullAABB[1].z + hullAABB[0].z) / 2.0)
                m = Math.Matrix(appearance.compoundModel.node(TankPartNames.HULL))
                worldPos = m.applyPoint(position)
                pivotPos = Math.Vector3(0, 0, 0)
            else:
                worldPos = cfg['cam_start_target_pos']
            if preserveAngles:
                matrix = Math.Matrix(self.__hangarCameraManager.camera.invViewMatrix)
                previewYaw = matrix.yaw
                previewPitch = self.__prevPitch or 0.0
            else:
                previewYaw = math.radians(cfg['cam_start_angles'][0])
                previewPitch = math.radians(cfg['cam_start_angles'][1])
            self._setCameraLocation(targetPos=worldPos, pivotPos=pivotPos, yaw=previewYaw, pitch=previewPitch, dist=cfg['cam_start_dist'], camConstraints=[hangarConfig['cam_pitch_constr'], hangarConfig['cam_yaw_constr'], cfg['cam_dist_constr']], smothiedTransition=not forceLocate)
            self.__prevPitch = None
            return

    def locateCameraToStartState(self):
        if self.__hangarCameraManager is None or self.__hangarCameraManager.camera is None:
            return
        else:
            from gui.ClientHangarSpace import hangarCFG
            cfg = hangarCFG()
            self.__hangarCameraManager.setCameraLocation(targetPos=cfg['cam_start_target_pos'], pivotPos=cfg['cam_pivot_pos'], yaw=math.radians(cfg['cam_start_angles'][0]), pitch=math.radians(cfg['cam_start_angles'][1]), dist=cfg['cam_start_dist'], camConstraints=[cfg['cam_pitch_constr'], cfg['cam_yaw_constr'], cfg['cam_dist_constr']])
            return

    def locateCameraOnEmblem(self, onHull, emblemType, emblemIdx, relativeSize=0.5):
        if self.__hangarCameraManager is None or self.__hangarCameraManager.camera is None:
            return False
        else:
            currentMatrix = Math.Matrix(self.__hangarCameraManager.camera.invViewMatrix)
            self.__prevPitch = -(currentMatrix.pitch - self.__hangarCameraManager.camera.pitchOffset)
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
            cfg = hangarCFG()
            emblemSize = emblemPositionParams[3] * cfg['v_scale']
            halfF = emblemSize / (2 * relativeSize)
            dist = halfF / math.tan(BigWorld.projection().fov / 2)
            self._setCameraLocation(targetPos=position, pivotPos=Math.Vector3(0, 0, 0), yaw=direction.yaw, pitch=-direction.pitch, dist=dist, previewMode=True)
            return True

    def locateCameraOnAnchor(self, position, normal):
        if self.__hangarCameraManager is None or self.__hangarCameraManager.camera is None:
            return False
        else:
            currentMatrix = Math.Matrix(self.__hangarCameraManager.camera.invViewMatrix)
            self.__prevPitch = -(currentMatrix.pitch - self.__hangarCameraManager.camera.pitchOffset)
            if normal is not None:
                direction = -normal
                yaw = direction.yaw
                pitch = -direction.pitch
            else:
                yaw = None
                pitch = None
            self._setCameraLocation(targetPos=position, pivotPos=Math.Vector3(0, 0, 0), yaw=yaw, pitch=pitch)
            return True

    def clearSelectedEmblemInfo(self):
        if self.__hangarCameraManager is not None:
            self.__hangarCameraManager.setPreviewMode(False)
        return

    def _setCameraLocation(self, targetPos=None, pivotPos=None, yaw=None, pitch=None, dist=None, camConstraints=None, ignoreConstraints=False, smothiedTransition=True, previewMode=False):
        from gui.ClientHangarSpace import customizationHangarCFG
        customCfg = customizationHangarCFG()
        self.__hangarCameraManager.camera.maxDistHalfLife = customCfg['cam_fluency']
        self.__hangarCameraManager.camera.turningHalfLife = customCfg['cam_fluency']
        self.__hangarCameraManager.camera.movementHalfLife = customCfg['cam_fluency']
        self.__hangarCameraManager.setCameraLocation(targetPos=targetPos, pivotPos=pivotPos, yaw=yaw, pitch=pitch, dist=dist, camConstraints=camConstraints, ignoreConstraints=ignoreConstraints, smothiedTransition=smothiedTransition, previewMode=previewMode, verticalOffset=_VERTICAL_OFFSET)
        self._startCameraMovement()

    def _startCameraMovement(self):
        self.__curTime = 0.0
        self._prevCameraPosition = None
        self.measureDeltaTime()
        self.delayCallback(0.1, self.__update)
        return

    def _finishCameraMovement(self):
        self.__curTime = None
        from gui.ClientHangarSpace import hangarCFG
        cfg = hangarCFG()
        self.__hangarCameraManager.camera.maxDistHalfLife = cfg['cam_fluency']
        self.__hangarCameraManager.camera.turningHalfLife = cfg['cam_fluency']
        self.__hangarCameraManager.camera.movementHalfLife = cfg['cam_fluency']
        return

    def __update(self):
        self.__curTime += self.measureDeltaTime() / 5.0
        isCameraDone = self.__curTime >= 1.0
        if not isCameraDone:
            cameraPosition = self.__hangarCameraManager.getCameraPosition()
            cameraPosition = Math.Vector3(round(cameraPosition.x, 2), round(cameraPosition.y, 2), round(cameraPosition.z, 2))
            isCameraDone = cameraPosition == self._prevCameraPosition
            self._prevCameraPosition = cameraPosition
        if isCameraDone:
            self.stopCallback(self.__update)
            self._finishCameraMovement()
            return None
        else:
            return 0.1

    def __onProjectionChanged(self, *args, **kwargs):
        self.__hangarCameraManager.updateProjection()
