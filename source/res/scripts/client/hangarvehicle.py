# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HangarVehicle.py
import BigWorld
import Math
import math
from ClientSelectableCameraObject import ClientSelectableCameraObject, CameraMovementStates, normalizeAngle
from AvatarInputHandler import mathUtils
from ModelHitTester import segmentMayHitVehicle, SegmentCollisionResult
from gui.shared.utils.HangarSpace import g_hangarSpace
from gui.shared import event_dispatcher as shared_events

class HangarVehicle(ClientSelectableCameraObject):
    ON_SELECT_SOUND_NAME = ''
    ON_DESELECT_SOUND_NAME = 'hangar_h15_sabaton_music_resume'

    def __init__(self):
        self.selectionId = ''
        self.clickSoundName = ''
        self.releaseSoundName = ''
        self.mouseOverSoundName = ''
        self.modelName = ''
        self.cameraPivotX = 0.0
        self.cameraPivotY = 0.0
        self.cameraPivotZ = 0.0
        self.cameraYaw = 0.0
        self.cameraPitch = 0.0
        self.cameraObjectAspect = 1.0
        self.yawLimitMin = 0.0
        self.yawLimitMax = 2.0 * math.pi
        self.pitchLimitMin = 0.0
        self.pitchLimitMax = 0.0
        self.typeDescriptor = None
        super(HangarVehicle, self).__init__()
        self.isRoot = True
        return

    def prerequisites(self):
        return []

    def onEnterWorld(self, prereqs):
        super(HangarVehicle, self).onEnterWorld(prereqs)
        self._setState(CameraMovementStates.ON_OBJECT)

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

    def setStartValues(self):
        pass

    def onKeyDown(self, key):
        pass

    def onDeselect(self):
        if self.state == CameraMovementStates.ON_OBJECT:
            space = g_hangarSpace.space
            camera = BigWorld.camera()
            self.goalPosition = camera.position
            self.cameraYaw = normalizeAngle(Math.Matrix(camera.source).yaw)
            self.cameraPitch = -1 * Math.Matrix(camera.source).pitch
            self.goalTarget = Math.Matrix(camera.target).translation
            self.goalDistance[0] = self.goalDistance[1] = camera.pivotMaxDist
            self.pitchLimits = space.getCameraLocation()['camConstraints'].pitchLimits
            self.cameraPivot = camera.pivotPosition
        super(HangarVehicle, self).onDeselect()

    def _callOnSelectEvent(self):
        shared_events.hideVehiclePreview()

    def setCursorCameraDistance(self):
        g_hangarSpace.space.setDefaultCameraDistance()

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
        if self.typeDescriptor is None:
            return res
        else:
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
