# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/commander/commands/vehicle_formation.py
from collections import namedtuple
import logging
import math
import BigWorld
import Math
import math_utils
import ResMgr
from Math import Vector3
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
_logger = logging.getLogger(__name__)
_HP_TO_WEIGHT_RATIO = 30
RTS_VEHICLE_FORMATION_CFG = 'gui/rts_vehicle_formation.xml'
_Slot = namedtuple('Slot', ('heavyTank', 'atSPG', 'heavyAtSPG', 'mediumAtSPG', 'lightAtSPG', 'SPG', 'heavySPG', 'mediumSPG', 'lightSPG', 'mediumTank', 'lightTank', 'posOffset'))

class VehicleFormationMgr(object):

    def __init__(self):
        self.__formations = []
        self.load(RTS_VEHICLE_FORMATION_CFG)

    def load(self, xmlConfigPath):
        self.__formations = []
        ResMgr.purge(xmlConfigPath)
        formationsDataSec = ResMgr.openSection(xmlConfigPath)
        if formationsDataSec:
            for dataSec in formationsDataSec.values():
                self.__formations.append(_Formation(dataSec))

    def getFormation(self, vehicleCount, formationIndex):
        found = 0
        formation = _Formation(None)
        for it in self.__formations:
            if it.isAllowedVehicleCount(vehicleCount):
                formation = it
                found += 1
                if formationIndex == found:
                    break

        return formation


class _Formation(object):

    def __init__(self, dataSec):
        self.__slots = []
        self.__vehicleCount = []
        self.load(dataSec)

    def load(self, dataSec):
        self.__slots = []
        self.__vehicleCount = []
        if dataSec is None:
            return
        else:
            self.__vehicleCount = map(int, dataSec.readString('vehicleCount', '').split())
            slotsDataSec = dataSec['slots']
            if slotsDataSec:
                for dataSecSlot in slotsDataSec.values():
                    heavyTankWeight = dataSecSlot.readFloat('heavyTank', 0)
                    atSPGWeight = dataSecSlot.readFloat('AT-SPG', 0)
                    spgWeight = dataSecSlot.readFloat('SPG', 0)
                    mediumTankWeight = dataSecSlot.readFloat('mediumTank', 0)
                    lightTankWeight = dataSecSlot.readFloat('lightTank', 0)
                    posOffset = dataSecSlot.readVector2('posOffset', Math.Vector2(0, 0))
                    heavyAtSPG = dataSecSlot.readFloat('heavyAT-SPG', -1)
                    mediumAtSPG = dataSecSlot.readFloat('mediumAT-SPG', -1)
                    lightAtSPG = dataSecSlot.readFloat('lightAT-SPG', -1)
                    heavySPG = dataSecSlot.readFloat('heavySPG', -1)
                    mediumSPG = dataSecSlot.readFloat('mediumSPG', -1)
                    lightSPG = dataSecSlot.readFloat('lightSPG', -1)
                    slot = _Slot(heavyTank=heavyTankWeight, atSPG=atSPGWeight, heavyAtSPG=heavyAtSPG, mediumAtSPG=mediumAtSPG, lightAtSPG=lightAtSPG, SPG=spgWeight, heavySPG=heavySPG, mediumSPG=mediumSPG, lightSPG=lightSPG, mediumTank=mediumTankWeight, lightTank=lightTankWeight, posOffset=posOffset)
                    self.__slots.append(slot)

            return

    def isAllowedVehicleCount(self, vehicleCount):
        return vehicleCount in self.__vehicleCount

    def sortVehicles(self, vehicleIDs):
        sortedVehicleIds = []
        currentTankWeight = 0
        currentTankName = None
        index = 0
        for slot in self.__slots:
            for vID in vehicleIDs:
                vehicle = BigWorld.entity(vID)
                if vID in sortedVehicleIds or not vehicle.id:
                    continue
                vTypeDesc = vehicle.typeDescriptor
                slotWeight = _getWeightFromSlot(slot, vTypeDesc)
                vehicleWeight = slotWeight + vehicle.health / _HP_TO_WEIGHT_RATIO
                vehicleName = vTypeDesc.type.userString
                if currentTankWeight <= vehicleWeight:
                    if 0 < currentTankWeight == vehicleWeight and vehicleName >= currentTankName:
                        continue
                    if 0 <= index < len(sortedVehicleIds):
                        sortedVehicleIds[index] = vID
                    else:
                        sortedVehicleIds.insert(index, vID)
                    currentTankWeight = vehicleWeight
                    currentTankName = vehicleName

            currentTankWeight = 0
            index += 1
            if index == len(vehicleIDs):
                break

        return sortedVehicleIds

    def getVehiclesPositions(self, vehicleIDs, position, direction, reverse):
        positions = []
        vIDs = self.sortVehicles(vehicleIDs)
        if self.__slots:
            heading = getHeading(direction, reverse)
            baseDir = Vector3(1, 0, 0)
            baseDirZ = Vector3(0, 0, 1)
            cosDiff = heading.dot(baseDir)
            radianDiff = math.acos(cosDiff)
            if heading.dot(baseDirZ) > 0:
                radianDiff = -1 * radianDiff
            rotationMatix = math_utils.createRotationMatrix(Vector3(radianDiff, 0, 0))
            for idx, vID in enumerate(vIDs):
                slot = self.__slots[idx]
                offset = slot.posOffset
                tankPos = Vector3(position.x + offset[1], position.y, position.z + offset[0]) - position
                positions.append((vID, rotationMatix.applyVector(tankPos) + position, heading))

        else:

            def _getCoefficient(rank, count):
                return rank + 0.5 - count / 2.0

            heading = getHeading(direction, reverse)
            for y, vID in enumerate(vehicleIDs):
                targetHeading = heading * 7.5 * _getCoefficient(0, 0)
                perpendicular = getPerpendicular(heading) * 7.5 * _getCoefficient(y, len(vehicleIDs))
                positions.append((vID, position - targetHeading + perpendicular, heading))

        return positions


def build(vehicleIDs, position, direction, rowCount=1, reverse=False):
    return getVehiclesPositions(vehicleIDs, position, direction, reverse, rowCount)


def getVehiclesPositions(vehicleIDs, position, direction, reverse, rowCount):
    vehicleCount = len(vehicleIDs)
    formation = g_formationMgr.getFormation(vehicleCount, rowCount)
    return formation.getVehiclesPositions(vehicleIDs, position, direction, reverse)


def getHeading(direction, reverse):
    heading = Math.Vector3(direction.x, 0, direction.z)
    heading.normalise()
    if reverse:
        heading = -heading
    return heading


def getPerpendicular(vector):
    perpendicular2D = _rotateVector2D(Math.Vector2(vector.x, vector.z), math.radians(90))
    return Math.Vector3(perpendicular2D.x, 0.0, perpendicular2D.y)


def pathsIntersect(position1, path1, position2, path2):
    maxPathLen = 100.0
    maxPathSegments = 4
    lenPath1 = min(len(path1), maxPathSegments)
    lenPath2 = min(len(path2), maxPathSegments)
    if not lenPath1 or not lenPath2:
        return False
    else:
        p1 = Math.Vector2(position1.x, position1.z)
        pathLen1 = 0.0
        for index1 in xrange(lenPath1):
            p2 = path1[index1]
            if p2 is None:
                continue
            p2 = Math.Vector2(p2.x, p2.z)
            q1 = Math.Vector2(position2.x, position2.z)
            pathLen2 = 0.0
            for index2 in xrange(lenPath2):
                q2 = path2[index2]
                if q2 is None:
                    continue
                q2 = Math.Vector2(q2.x, q2.z)
                if p2.distTo(q2) < 5:
                    return False
                if _lineSegmentsIntersect2D(p1, p2, q1, q2):
                    return True
                pathLen2 = pathLen2 + q1.distTo(q2)
                if pathLen2 > maxPathLen:
                    break
                q1 = q2

            pathLen1 = pathLen1 + p1.distTo(p2)
            if pathLen1 > maxPathLen:
                break
            p1 = p2

        return False


def getPathFinalHeading(start, path):
    if not path or start is None:
        return Math.Vector3(0.0, 0.0, 1.0)
    else:
        pathLen = len(path)
        p1 = start if pathLen == 1 else path[pathLen - 2]
        p2 = path[pathLen - 1]
        if p1 is None or p2 is None:
            return Math.Vector3(0.0, 0.0, 1.0)
        finalHeading = p2 - p1
        finalHeading.y = 0
        finalHeading = _normaliseSafe(finalHeading, Math.Vector3(0.0, 0.0, 1.0))
        return finalHeading


def getBotPathFinalHeading(bot, path):
    return Math.Vector3(0.0, 0.0, 1.0) if path is None else getPathFinalHeading(bot.position, path)


def _normaliseSafe(vector, default=None):
    if default is None:
        default = Math.Vector3(0.0, 0.0, 0.0)
    magnitude = vector.length
    return vector / magnitude if magnitude else default


def _rotateVector2D(vector, angle):
    x = vector.x
    y = vector.y
    cosTheta = math.cos(angle)
    sinTheta = math.sin(angle)
    return Math.Vector2(x * cosTheta - y * sinTheta, x * sinTheta + y * cosTheta)


def _lineSegmentsIntersect2D(p1, p2, q1, q2):
    r = p2 - p1
    s = q2 - q1
    rxs = r.cross2D(s)
    if math_utils.almostZero(rxs):
        return False
    delta = q1 - p1
    t = delta.cross2D(s) / rxs
    u = delta.cross2D(r) / rxs
    return 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0


def _getWeightFromSlot(slot, vTypeDesc):
    vClass = vTypeDesc.type.getVehicleClass()
    if vClass == VEHICLE_CLASS_NAME.HEAVY_TANK:
        return slot.heavyTank
    if vClass == VEHICLE_CLASS_NAME.MEDIUM_TANK:
        return slot.mediumTank
    if vClass == VEHICLE_CLASS_NAME.LIGHT_TANK:
        return slot.lightTank
    if vClass == VEHICLE_CLASS_NAME.AT_SPG:
        if 'heavyAT-SPG' in vTypeDesc.type.tags and slot.heavyAtSPG >= 0:
            return slot.heavyAtSPG
        if 'mediumAT-SPG' in vTypeDesc.type.tags and slot.mediumAtSPG >= 0:
            return slot.mediumAtSPG
        if 'lightAT-SPG' in vTypeDesc.type.tags and slot.lightAtSPG >= 0:
            return slot.lightAtSPG
        return slot.atSPG
    if vClass == VEHICLE_CLASS_NAME.SPG:
        if 'lightSPG' in vTypeDesc.type.tags and slot.lightSPG >= 0:
            return slot.lightSPG
        if 'mediumSPG' in vTypeDesc.type.tags and slot.mediumSPG >= 0:
            return slot.mediumSPG
        if 'heavySPG' in vTypeDesc.type.tags and slot.heavySPG >= 0:
            return slot.heavySPG
        return slot.SPG
    _logger.error('Vehicle type is missing from formation: ' + str(vClass))


g_formationMgr = VehicleFormationMgr()
