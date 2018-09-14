# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HangarVehicle.py
import BigWorld
import Math
from AvatarInputHandler import mathUtils
from ModelHitTester import segmentMayHitVehicle, SegmentCollisionResult

class HangarVehicle(BigWorld.Entity):

    def __init__(self):
        self.typeDescriptor = None
        return

    def prerequisites(self):
        return []

    def onEnterWorld(self, prereqs):
        pass

    def onLeaveWorld(self):
        self.releaseBspModels()

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
