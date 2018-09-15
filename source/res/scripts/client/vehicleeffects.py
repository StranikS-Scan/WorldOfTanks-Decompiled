# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VehicleEffects.py
from collections import namedtuple
import BigWorld
import Math
import Pixie
from Math import Matrix
from constants import VEHICLE_HIT_EFFECT
from debug_utils import LOG_CODEPOINT_WARNING, LOG_WARNING, LOG_ERROR
from items import _xml, vehicles
import material_kinds
from helpers.EffectMaterialCalculation import calcEffectMaterialIndex
from CustomEffect import RangeTable
from helpers import PixieBG
from vehicle_systems.stricted_loading import restrictBySpaceAndNode, restrictBySpace
from vehicle_systems.tankStructure import TankNodeNames, TankPartNames
from svarog_script.py_component import Component
DUMMY_NODE_PREFIX = 'DM'

class DamageFromShotDecoder(object):
    ShotPoint = namedtuple('ShotPoint', ('componentName', 'matrix', 'hitEffectGroup'))
    __hitEffectCodeToEffectGroup = ('armorBasicRicochet', 'armorRicochet', 'armorResisted', 'armorResisted', 'armorHit', 'armorCriticalHit')

    @staticmethod
    def hasDamaged(vehicleHitEffectCode):
        return vehicleHitEffectCode >= VEHICLE_HIT_EFFECT.ARMOR_PIERCED

    @staticmethod
    def decodeHitPoints(encodedPoints, vehicleDescr):
        resultPoints = []
        maxHitEffectCode = None
        for encodedPoint in encodedPoints:
            compName, hitEffectCode, startPoint, endPoint = DamageFromShotDecoder.decodeSegment(encodedPoint, vehicleDescr)
            if startPoint == endPoint:
                continue
            maxHitEffectCode = max(hitEffectCode, maxHitEffectCode)
            hitTester = getattr(vehicleDescr, compName).hitTester
            hitTestRes = hitTester.localHitTest(startPoint, endPoint)
            if not hitTestRes:
                width, height, depth = (hitTester.bbox[1] - hitTester.bbox[0]) / 256.0
                directions = [Math.Vector3(0.0, -height, 0.0),
                 Math.Vector3(0.0, height, 0.0),
                 Math.Vector3(-width, 0.0, 0.0),
                 Math.Vector3(width, 0.0, 0.0),
                 Math.Vector3(0.0, 0.0, -depth),
                 Math.Vector3(0.0, 0.0, depth)]
                for direction in directions:
                    hitTestRes = hitTester.localHitTest(startPoint + direction, endPoint + direction)
                    if hitTestRes is not None:
                        break

                if hitTestRes is None:
                    continue
            minDist = hitTestRes[0][0]
            for i in xrange(1, len(hitTestRes)):
                dist = hitTestRes[i][0]
                if dist < minDist:
                    minDist = dist

            hitDir = endPoint - startPoint
            hitDir.normalise()
            rot = Matrix()
            rot.setRotateYPR((hitDir.yaw, hitDir.pitch, 0.0))
            matrix = Matrix()
            matrix.setTranslate(startPoint + hitDir * minDist)
            matrix.preMultiply(rot)
            effectGroup = DamageFromShotDecoder.__hitEffectCodeToEffectGroup[hitEffectCode]
            resultPoints.append(DamageFromShotDecoder.ShotPoint(compName, matrix, effectGroup))

        return (maxHitEffectCode, resultPoints)

    @staticmethod
    def decodeSegment(segment, vehicleDescr):
        compIdx = segment >> 8 & 255
        if compIdx == 0:
            componentName = TankPartNames.CHASSIS
            bbox = vehicleDescr.chassis.hitTester.bbox
        elif compIdx == 1:
            componentName = TankPartNames.HULL
            bbox = vehicleDescr.hull.hitTester.bbox
        elif compIdx == 2:
            componentName = TankPartNames.TURRET
            bbox = vehicleDescr.turret.hitTester.bbox
        elif compIdx == 3:
            componentName = TankPartNames.GUN
            bbox = vehicleDescr.gun.hitTester.bbox
        else:
            LOG_CODEPOINT_WARNING(compIdx)
            return ('',
             int(segment & 255),
             None,
             None)
        min = Math.Vector3(bbox[0])
        delta = (bbox[1] - min).scale(1.0 / 255.0)
        segStart = min + Math.Vector3(delta[0] * (segment >> 16 & 255), delta[1] * (segment >> 24 & 255), delta[2] * (segment >> 32 & 255))
        segEnd = min + Math.Vector3(delta[0] * (segment >> 40 & 255), delta[1] * (segment >> 48 & 255), delta[2] * (segment >> 56 & 255))
        offset = (segEnd - segStart) * 0.01
        return (componentName,
         int(segment & 255),
         segStart - offset,
         segEnd + offset)


class RepaintParams(object):

    @staticmethod
    def getRepaintParams(vehicleDescr):
        tintGroups = vehicles.g_cache.customization(vehicleDescr.type.customizationNationID)['tintGroups']
        for i in tintGroups.keys():
            grp = tintGroups[i]
            repaintReplaceColor = Math.Vector4(grp.x, grp.y, grp.z, 0.0) / 255.0

        refColor = vehicleDescr.type.repaintParameters['refColor'] / 255.0
        repaintReferenceGloss = vehicleDescr.type.repaintParameters['refGloss'] / 255.0
        repaintColorRangeScale = vehicleDescr.type.repaintParameters['refColorMult']
        repaintGlossRangeScale = vehicleDescr.type.repaintParameters['refGlossMult']
        repaintReferenceColor = Math.Vector4(refColor.x, refColor.y, refColor.z, repaintReferenceGloss)
        repaintReplaceColor.w = repaintColorRangeScale
        return (repaintReferenceColor, repaintReplaceColor, repaintGlossRangeScale)
