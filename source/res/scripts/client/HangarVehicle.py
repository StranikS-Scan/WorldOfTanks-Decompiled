# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HangarVehicle.py
import BigWorld
import Math
from AvatarInputHandler import mathUtils
from ModelHitTester import segmentMayHitVehicle, SegmentCollisionResult
from ClientSelectableCameraObject import ClientSelectableCameraObject, CameraMovementStates, normalizeAngle
from gui.shared.utils.HangarSpace import g_hangarSpace

class HangarVehicle(ClientSelectableCameraObject):
    CALLBACK_DELAY = 0.02

    def __init__(self):
        self.selectionId = ''
        self.clickSoundName = ''
        self.cameraFlyToSoundName = ''
        self.cameraFlyFromSoundName = ''
        self.releaseSoundName = ''
        self.mouseOverSoundName = ''
        self.modelName = ''
        self.camera_shift_x = 0.0
        self.camera_shift_y = 0.0
        self.camera_shift_z = 0.0
        self.camera_pivot_x = 0.0
        self.camera_pivot_y = 0.0
        self.camera_pivot_z = 0.0
        self.camera_yaw = 0.0
        self.camera_pitch = 0.0
        self.camera_object_aspect = 1.0
        self.enable_yaw_limits = False
        self.yaw_limit_min = 0.0
        self.yaw_limit_max = 0.0
        self.pitch_limit_min = 0.0
        self.pitch_limit_max = 0.0
        self.camera_object_width = 0.0
        self.hack_enabled = False
        self.hacked_ratio = 0.0
        self.hacked_pivot_x = 0.0
        self.camera_min_distance = 0.0
        self.camera_max_distance = 0.0
        self.camera_backward_duration = 10.0
        self.camera_upcoming_duration = 10.0
        super(HangarVehicle, self).__init__()
        self.__pointToSee = None
        self.__heightMultiplier = None
        self.isNewYearHangar = False
        self.typeDescriptor = None
        self.isRoot = True
        return

    def prerequisites(self):
        return []

    def onEnterWorld(self, prereqs):
        super(HangarVehicle, self).onEnterWorld(prereqs)
        self.enable(False)
        self.setState(CameraMovementStates.ON_OBJECT)

    def onLeaveWorld(self):
        self.releaseBspModels()
        super(HangarVehicle, self).onLeaveWorld()

    def canDoHitTest(self, dotest):
        self.icanDoHitTest = dotest

    def releaseBspModels(self):
        self.icanDoHitTest = False
        if self.typeDescriptor is not None:
            for compDescr, compMatrix in self.getComponents():
                hitTester = compDescr.hitTester
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
            if skipGun and compDescr.itemTypeName == 'vehicleGun':
                continue
            hitTester = compDescr.hitTester
            if not hitTester.isBspModelLoaded():
                hitTester.loadBspModel()
            collisions = hitTester.localHitTest(compMatrix.applyPoint(startPoint), compMatrix.applyPoint(endPoint))
            if collisions is None:
                continue
            for dist, _, hitAngleCos, matKind in collisions:
                if res is None or res[0] >= dist:
                    matInfo = compDescr.materials.get(matKind)
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
        hullOffset = vehicleDescr.chassis.hullPosition
        m = Math.Matrix()
        offset = -hullOffset
        m.setTranslate(offset)
        res.append((vehicleDescr.hull, m))
        m = Math.Matrix()
        offset -= vehicleDescr.hull.turretPositions[0]
        m.setTranslate(offset)
        res.append((vehicleDescr.turret, m))
        yaw = vehicleDescr.gun.staticTurretYaw
        pitch = vehicleDescr.gun.staticPitch
        offset -= vehicleDescr.turret.gunPosition
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

    def onDeselect(self, newSelectedObject=None):
        if self.state == CameraMovementStates.ON_OBJECT:
            camera = BigWorld.camera()
            self.goalPosition = camera.position
            self.cameraYaw = normalizeAngle(Math.Matrix(camera.source).yaw)
            self.cameraPitch = -1 * Math.Matrix(camera.source).pitch
            self.goalTarget = Math.Matrix(camera.target).translation
            self.goalDistance[0] = self.goalDistance[1] = camera.pivotMaxDist
            self.pitchLimits = g_hangarSpace.space.getCameraLocation()['camConstraints'][0]
            self.cameraPivot = camera.pivotPosition
        return super(HangarVehicle, self).onDeselect(newSelectedObject)

    def setCursorCameraDistance(self):
        g_hangarSpace.space.setDefaultCameraDistance()
