# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VehicleEffects.py
from collections import namedtuple
import Math
from Math import Matrix
from constants import VEHICLE_HIT_EFFECT
from debug_utils import LOG_CODEPOINT_WARNING
from items import vehicles
from vehicle_systems.tankStructure import TankPartIndexes
DUMMY_NODE_PREFIX = 'DM'
MAX_FALLBACK_CHECK_DISTANCE = 10000.0
HitEffectMapping = namedtuple('HitEffectMapping', ('componentName', 'hitTester'))

class DamageFromShotDecoder(object):
    ShotPoint = namedtuple('ShotPoint', ('componentName', 'matrix', 'hitEffectCode', 'hitEffectGroup'))
    _HIT_EFFECT_CODE_TO_EFFECT_GROUP = {VEHICLE_HIT_EFFECT.INTERMEDIATE_RICOCHET: 'armorBasicRicochet',
     VEHICLE_HIT_EFFECT.FINAL_RICOCHET: 'armorRicochet',
     VEHICLE_HIT_EFFECT.ARMOR_NOT_PIERCED: 'armorResisted',
     VEHICLE_HIT_EFFECT.ARMOR_PIERCED_NO_DAMAGE: 'armorResisted',
     VEHICLE_HIT_EFFECT.ARMOR_PIERCED: 'armorHit',
     VEHICLE_HIT_EFFECT.CRITICAL_HIT: 'armorCriticalHit',
     VEHICLE_HIT_EFFECT.ARMOR_PIERCED_DEVICE_DAMAGED: 'armorCriticalHit'}

    @staticmethod
    def hasDamaged(vehicleHitEffectCode):
        return vehicleHitEffectCode >= VEHICLE_HIT_EFFECT.ARMOR_PIERCED

    @classmethod
    def decodeHitPoints(cls, encodedPoints, collisionComponent, maxComponentIdx=TankPartIndexes.ALL[-1]):
        resultPoints = []
        for encodedPoint in encodedPoints:
            compIdx, hitEffectCode, startPoint, endPoint = DamageFromShotDecoder.decodeSegment(encodedPoint, collisionComponent, maxComponentIdx)
            if startPoint == endPoint or compIdx < 0:
                continue
            convertedCompIdx = DamageFromShotDecoder.convertComponentIndex(compIdx)
            hitTestRes = collisionComponent.collideLocal(convertedCompIdx, startPoint, endPoint)
            bbox = collisionComponent.getBoundingBox(convertedCompIdx)
            if not hitTestRes or hitTestRes < 0.0:
                width, height, depth = (bbox[1] - bbox[0]) / 256.0
                directions = [Math.Vector3(0.0, -height, 0.0),
                 Math.Vector3(0.0, height, 0.0),
                 Math.Vector3(-width, 0.0, 0.0),
                 Math.Vector3(width, 0.0, 0.0),
                 Math.Vector3(0.0, 0.0, -depth),
                 Math.Vector3(0.0, 0.0, depth)]
                for direction in directions:
                    hitTestRes = collisionComponent.collideLocal(convertedCompIdx, startPoint + direction, endPoint + direction)
                    if hitTestRes >= 0.0:
                        break

            if hitTestRes is None or hitTestRes < 0.0:
                newPoint = collisionComponent.collideLocalPoint(convertedCompIdx, startPoint, MAX_FALLBACK_CHECK_DISTANCE)
                if newPoint.length > 0.0:
                    hitRay = endPoint - startPoint
                    hitTestRes = hitRay.length
                    endPoint = newPoint
                    startPoint = endPoint - hitRay
            if hitTestRes is None or hitTestRes < 0.0:
                continue
            minDist = hitTestRes
            hitDir = endPoint - startPoint
            hitDir.normalise()
            rot = Matrix()
            rot.setRotateYPR((hitDir.yaw, hitDir.pitch, 0.0))
            matrix = Matrix()
            matrix.setTranslate(startPoint + hitDir * minDist)
            matrix.preMultiply(rot)
            effectGroup = cls._HIT_EFFECT_CODE_TO_EFFECT_GROUP[hitEffectCode]
            componentName = TankPartIndexes.getName(compIdx)
            if not componentName:
                componentName = collisionComponent.getPartName(convertedCompIdx)
            resultPoints.append(DamageFromShotDecoder.ShotPoint(componentName, matrix, hitEffectCode, effectGroup))

        return resultPoints

    @staticmethod
    def convertComponentIndex(compIdx):
        idx = compIdx
        maxStructuralIndex = TankPartIndexes.ALL[-1]
        if compIdx > maxStructuralIndex:
            idx = maxStructuralIndex - compIdx
        return idx

    @staticmethod
    def decodeSegment(segment, collisionComponent, maxComponentIdx=TankPartIndexes.ALL[-1]):
        if collisionComponent is None:
            return (-1,
             int(segment & 255),
             None,
             None)
        else:
            compIdx = segment >> 8 & 255
            if compIdx > maxComponentIdx:
                LOG_CODEPOINT_WARNING(compIdx)
                return (-1,
                 int(segment & 255),
                 None,
                 None)
            bbox = collisionComponent.getBoundingBox(DamageFromShotDecoder.convertComponentIndex(compIdx))
            minimum = Math.Vector3(bbox[0])
            delta = (bbox[1] - minimum).scale(1.0 / 255.0)
            segStart = minimum + Math.Vector3(delta[0] * (segment >> 16 & 255), delta[1] * (segment >> 24 & 255), delta[2] * (segment >> 32 & 255))
            segEnd = minimum + Math.Vector3(delta[0] * (segment >> 40 & 255), delta[1] * (segment >> 48 & 255), delta[2] * (segment >> 56 & 255))
            offset = (segEnd - segStart) * 0.01
            return (compIdx,
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
