# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HangarVehicle.py
import BigWorld
import Math
from AvatarInputHandler import mathUtils
from ModelHitTester import segmentMayHitVehicle, SegmentCollisionResult
import math
from gui.shared.utils import HangarSpace
from ClientSelectableCameraObject import ClientSelectableCameraObject, CameraMovementStates
import ResMgr
from vehicle_systems.tankStructure import TankPartIndexes, TankPartNames

class HangarVehicle(ClientSelectableCameraObject):
    CALLBACK_DELAY = 0.02

    def __init__(self):
        self.selectionId = ''
        self.clickSoundName = ''
        self.releaseSoundName = ''
        self.mouseOverSoundName = ''
        self.modelName = ''
        self.camera_shift_x = 0
        self.camera_shift_y = 0
        self.camera_shift_z = 0
        self.camera_pivot_x = 0
        self.camera_pivot_y = 0
        self.camera_pivot_z = 0
        self.camera_yaw = 0
        self.camera_pitch = 0
        self.camera_object_aspect = 1
        self.enable_yaw_limits = False
        self.yaw_limits = None
        self.pitch_limit_min = 0
        self.pitch_limit_max = 0
        self.camera_object_width = 0
        self.hack_enabled = False
        self.hacked_ratio = 0
        self.hacked_pivot_x = 0
        super(HangarVehicle, self).__init__()
        self.__pointToSee = None
        self.__heightMultiplier = None
        self.readCameraSettings()
        self.isNewYearHangar = False
        self.typeDescriptor = None
        self.isRoot = True
        return

    def readCameraSettings(self):
        from ChristmassTree import _CHRISTMASS_CONFIG_FILE
        settingsSection = ResMgr.openSection(_CHRISTMASS_CONFIG_FILE)
        if settingsSection is not None:
            cameraSettings = settingsSection['hangarVehicle/camera']
            if cameraSettings is not None:
                pointToSeeSection = cameraSettings['pointToSee']
                if pointToSeeSection is not None:
                    self.__pointToSee = pointToSeeSection.asVector3
                heightMultiplierSection = cameraSettings['heightMultiplier']
                if heightMultiplierSection is not None:
                    self.__heightMultiplier = heightMultiplierSection.asFloat
        return

    def prerequisites(self):
        return []

    def onEnterWorld(self, prereqs):
        super(HangarVehicle, self).onEnterWorld(prereqs)
        self.enable(False)
        self.state = CameraMovementStates.ON_OBJECT

    def onLeaveWorld(self):
        self.releaseBspModels()
        super(HangarVehicle, self).onLeaveWorld()

    def canDoHitTest(self, dotest):
        self.icanDoHitTest = dotest

    def releaseBspModels(self):
        self.icanDoHitTest = False
        if self.typeDescriptor is not None:
            for compDescr, compMatrix in self.getComponents():
                hitTester = compDescr['hitTester']
                if hitTester.isBspModelLoaded():
                    hitTester.releaseBspModel()

        return

    def collideSegment(self, startPoint, endPoint, skipGun=False):
        worldToVehMatrix = Math.Matrix(self.model.matrix)
        worldToVehMatrix.invert()
        startPoint = worldToVehMatrix.applyPoint(startPoint)
        endPoint = worldToVehMatrix.applyPoint(endPoint)
        res = None
        for compDescr, compMatrix in self.getComponents():
            if skipGun and compDescr.get('itemTypeName') == 'vehicleGun':
                continue
            hitTester = compDescr['hitTester']
            if not hitTester.isBspModelLoaded():
                hitTester.loadBspModel()
            collisions = hitTester.localHitTest(compMatrix.applyPoint(startPoint), compMatrix.applyPoint(endPoint))
            if collisions is None:
                continue
            for dist, _, hitAngleCos, matKind in collisions:
                if res is None or res[0] >= dist:
                    matInfo = compDescr['materials'].get(matKind)
                    res = SegmentCollisionResult(dist, hitAngleCos, matInfo.armor if matInfo is not None else 0)

        return res

    def segmentMayHitVehicle(self, startPoint, endPoint):
        return segmentMayHitVehicle(self.typeDescriptor, startPoint, endPoint, self.position)

    def getComponents(self):
        res = []
        vehicleDescr = self.typeDescriptor
        m = Math.Matrix()
        m.setIdentity()
        res.append((vehicleDescr.chassis, m))
        hullOffset = vehicleDescr.chassis['hullPosition']
        m = Math.Matrix()
        offset = -hullOffset
        m.setTranslate(offset)
        res.append((vehicleDescr.hull, m))
        m = Math.Matrix()
        offset -= vehicleDescr.hull['turretPositions'][0]
        m.setTranslate(offset)
        res.append((vehicleDescr.turret, m))
        yaw = vehicleDescr.gun.get('staticTurretYaw', 0.0)
        pitch = vehicleDescr.gun.get('staticPitch', 0.0)
        offset -= vehicleDescr.turret['gunPosition']
        if yaw is None:
            yaw = 0.0
        if pitch is None:
            pitch = 0.0
        m = Math.Matrix()
        gunMatrix = mathUtils.createRTMatrix(Math.Vector3(yaw, pitch, 0.0), offset)
        gunMatrix.postMultiply(m)
        res.append((vehicleDescr.gun, gunMatrix))
        return res

    def setStartValues(self):
        pass

    def _teleportHangarSpaceCamera(self, useCurrentAngles=False):
        oldPos = self.goalPosition
        super(HangarVehicle, self)._teleportHangarSpaceCamera()
        self.goalPosition = oldPos

    CONST_WALL_FLAG = 2147483648L

    def onDeselect(self):
        space = HangarSpace.g_hangarSpace.space
        space.setVisibilityMask(0)
        if self.state == CameraMovementStates.ON_OBJECT:
            camera = BigWorld.camera()
            self.goalPosition = camera.position
            self.goalYaw = Math.Matrix(camera.source).yaw
            self.goalPitch = -1 * Math.Matrix(camera.source).pitch
            self.goalPivot = camera.pivotPosition
            self.goalTarget = Math.Matrix(camera.target).translation
            self.goalDistance[0] = self.goalDistance[1] = camera.pivotMaxDist
            self.pitchLimits = space.getCameraLocation()['camConstraints'][0]
        super(HangarVehicle, self).onDeselect()

    def onSelect(self, callback=None):
        super(HangarVehicle, self).onSelect(callback)
        HangarSpace.g_hangarSpace.space.setVisibilityMask(self.CONST_WALL_FLAG)

    def setCursorCameraDistance(self):
        HangarSpace.g_hangarSpace.space.setDefaultCameraDistance()

    def __checkPosibilityToLocateCamera(self):
        return self.isNewYearHangar and self.__pointToSee is not None and self.__heightMultiplier is not None

    def __checkWaitToLocateCamera(self):
        clientSpace = HangarSpace.g_hangarSpace.space
        return clientSpace is None

    def __addCameraColliders(self):
        colliders = [(self.model.node(TankPartNames.TURRET), self.model.getBoundsForPart(TankPartIndexes.TURRET), self.model.getPartGeometryLink(TankPartIndexes.TURRET)), (self.model.node(TankPartNames.HULL), self.model.getBoundsForPart(TankPartIndexes.HULL), self.model.getPartGeometryLink(TankPartIndexes.HULL))]
        HangarSpace.g_hangarSpace.space.getCamera().setDynamicColliders(colliders)

    def __calculateCameraParams(self):
        boundsProvider = self.model.getBoundsForRoot()
        bounds = Math.Matrix(boundsProvider)
        height = bounds.get(1, 1)
        maxTankWidth = math.sqrt(bounds.get(0, 0) * bounds.get(0, 0) + bounds.get(2, 2) * bounds.get(2, 2))
        B = self.__pointToSee
        Tb = Math.Vector3(self.position)
        Tt = Tb + Math.Vector3(0, height * self.__heightMultiplier, 0)
        Tm = Tb + Math.Vector3(0, height, 0) * 0.5
        Cc = Math.Vector3(BigWorld.camera().position)
        Cb = Cc
        Cb.y = Tb.y
        B_Tb = B - Tb
        Tt_Tb = Tt - Tb
        Cb_B = Cb - B
        Ct_Cb_length = Tt_Tb.length * Cb_B.length / (B_Tb.length - maxTankWidth * 0.5)
        Ct = Cb + Math.Vector3(0, Ct_Cb_length, 0)
        Tc = Tb + Math.Vector3(0, Ct_Cb_length, 0)
        Tc_Tm = Tc - Tm
        Ct_Tm = Ct - Tm
        Tc_Ct_Tm_sin = Tc_Tm.length / Ct_Tm.length
        Tc_Ct_Tm = math.asin(Tc_Ct_Tm_sin)
        pitch = -Tc_Ct_Tm
        distance = Ct_Tm.length
        return (pitch, distance)

    def locateCameraAccordingToVehicle(self):
        if not self.__checkPosibilityToLocateCamera():
            return
        elif self.__checkWaitToLocateCamera():
            self.delayCallback(HangarVehicle.CALLBACK_DELAY, self.locateCameraAccordingToVehicle)
            return
        else:
            self.__addCameraColliders()
            pitch, distance = self.__calculateCameraParams()
            clientSpace = HangarSpace.g_hangarSpace.space
            defaultCameraDistance = clientSpace.getCameraDistance(False)
            previewCameraDistance = clientSpace.getCameraDistance(True)
            clientSpace.setCameraDistance(defaultCameraDistance[0], max(distance, defaultCameraDistance[1]), previewCameraDistance[1], max(distance, previewCameraDistance[1]))
            constr = clientSpace.getCameraLocation()['camConstraints']
            currentPitchLimits = constr[0]
            newPitchLimits = Math.Vector2()
            newPitchLimits[0] = min(currentPitchLimits[0], math.degrees(pitch))
            newPitchLimits[1] = max(currentPitchLimits[1], math.degrees(pitch))
            constr[0] = newPitchLimits
            clientSpace.setCameraLocation(None, None, None, pitch, distance, constr, False)
            hangarCamera = clientSpace.getCamera()
            hangarCamera.forceUpdate()
            return

    def onSettingChanged(self):
        pass
