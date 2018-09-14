# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HangarVehicle.py
import BigWorld
import Math
from ModelHitTester import segmentMayHitVehicle, SegmentCollisionResult
from gui.shared.utils import HangarSpace
from ClientSelectableCameraObject import ClientSelectableCameraObject, CameraMovementStates
import SoundGroups

class HangarVehicle(ClientSelectableCameraObject):

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
        super(HangarVehicle, self).__init__()
        self.typeDescriptor = None
        self.isRoot = True
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
        m = Math.Matrix()
        offset -= vehicleDescr.turret['gunPosition']
        m.setTranslate(offset)
        res.append((vehicleDescr.gun, m))
        return res

    def playSelectedSound(self):
        SoundGroups.g_instance.playSound2D('hangar_activeview_tank')

    def setStartValues(self):
        pass

    def onDeselect(self):
        if self.state == CameraMovementStates.ON_OBJECT:
            camera = BigWorld.camera()
            self.goalPosition = camera.position
            self.goalYaw = Math.Matrix(camera.source).yaw
            self.goalPitch = self.getPitchMultiplier() * Math.Matrix(camera.source).pitch
            self.goalPivot = camera.pivotPosition
            self.goalTarget = Math.Matrix(camera.target).translation
            self.goalDistance = camera.pivotMaxDist
        super(HangarVehicle, self).onDeselect()

    def setCursorCameraDistance(self):
        HangarSpace.g_hangarSpace.space.setDefaultCameraDistance()

    def getPitchMultiplier(self):
        pass
