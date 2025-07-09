# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VehicleEffects.py
from collections import namedtuple
import typing
import cgf_network
import Physics
from Math import Vector3, Vector4, Matrix
from constants import VEHICLE_HIT_EFFECT
from debug_utils import LOG_CODEPOINT_WARNING, LOG_DEBUG_DEV
from items import vehicles
from helpers_common import decodeSegment, getComponentIndexFromEncodedSegment
from vehicle_systems.tankStructure import TankPartIndexes, TankPartNames
if typing.TYPE_CHECKING:
    from Entity import PyFixedDictDataInstance
    from BigWorld import CollisionComponent
    from typing import Optional, Union, TypeVar, List, Tuple
    TYPE_VEH_HIT_POINT = TypeVar('TYPE_VEH_HIT_POINT', bound=PyFixedDictDataInstance)
DUMMY_NODE_PREFIX = 'DM'
MAX_FALLBACK_CHECK_DISTANCE = 10000.0
HitEffectMapping = namedtuple('HitEffectMapping', ('componentName', 'hitTester'))

class DamageFromShotDecoder(object):
    ShotPoint = namedtuple('ShotPoint', ('componentName', 'componentIdx', 'matrix', 'hitEffectCode', 'hitEffectGroup', 'isDynCollision'))
    _HIT_EFFECT_CODE_TO_EFFECT_GROUP = {VEHICLE_HIT_EFFECT.INTERMEDIATE_RICOCHET: 'armorBasicRicochet',
     VEHICLE_HIT_EFFECT.FINAL_RICOCHET: 'armorRicochet',
     VEHICLE_HIT_EFFECT.ARMOR_NOT_PIERCED: 'armorResisted',
     VEHICLE_HIT_EFFECT.ARMOR_PIERCED_NO_DAMAGE: 'armorResisted',
     VEHICLE_HIT_EFFECT.ARMOR_PIERCED: 'armorHit',
     VEHICLE_HIT_EFFECT.CRITICAL_HIT: 'armorCriticalHit',
     VEHICLE_HIT_EFFECT.ARMOR_PIERCED_DEVICE_DAMAGED: 'armorCriticalHit'}
    _PRIMARY_COLLISION_INDEX = 0
    _ENCODED_SEGMENT_BITS = 64

    @staticmethod
    def hasDamaged(vehicleHitEffectCode):
        return vehicleHitEffectCode >= VEHICLE_HIT_EFFECT.ARMOR_PIERCED

    @staticmethod
    def convertComponentIndex(compIdx, collisionComponent):
        return collisionComponent.maxStaticPartIndex - compIdx if compIdx > collisionComponent.maxStaticPartIndex else compIdx

    @staticmethod
    def getPartName(partIndex, collisionComponent):
        return collisionComponent.getPartName(partIndex) if partIndex < 0 else TankPartIndexes.getName(partIndex)

    @classmethod
    def encodeHitPoint(cls, hitPoint):
        return hitPoint['networkID'] << cls._ENCODED_SEGMENT_BITS | hitPoint['segment']

    @classmethod
    def getNetworkIDFromEncodedHitPoint(cls, code):
        return code >> cls._ENCODED_SEGMENT_BITS

    @classmethod
    def parseHitPoints(cls, hitPoints, collisionComponent):
        resultPoints = []
        for hitPoint in hitPoints:
            parsedHitPoint = DamageFromShotDecoder.parseHitPoint(hitPoint, collisionComponent)
            if parsedHitPoint is None:
                continue
            compIdx, hitEffectCode, startPoint, endPoint = parsedHitPoint
            if startPoint == endPoint:
                continue
            hitTestRes = collisionComponent.collideLocal(compIdx, startPoint, endPoint)
            bbox = collisionComponent.getBoundingBox(compIdx)
            if not hitTestRes or hitTestRes < 0.0:
                width, height, depth = (bbox[1] - bbox[0]) / 256.0
                directions = [Vector3(0.0, -height, 0.0),
                 Vector3(0.0, height, 0.0),
                 Vector3(-width, 0.0, 0.0),
                 Vector3(width, 0.0, 0.0),
                 Vector3(0.0, 0.0, -depth),
                 Vector3(0.0, 0.0, depth)]
                for direction in directions:
                    hitTestRes = collisionComponent.collideLocal(compIdx, startPoint + direction, endPoint + direction)
                    if hitTestRes >= 0.0:
                        break

            if hitTestRes is None or hitTestRes < 0.0:
                newPoint = collisionComponent.collideLocalPoint(compIdx, startPoint, MAX_FALLBACK_CHECK_DISTANCE)
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
            hitPoint = startPoint + hitDir * minDist
            componentName = cls.getPartName(compIdx, collisionComponent)
            isDynCollision = compIdx > collisionComponent.maxStaticPartIndex
            if isDynCollision:
                parentCompIdx = collisionComponent.getParentPartIndex(compIdx)
                if parentCompIdx is not None:
                    componentName = cls.getPartName(parentCompIdx, collisionComponent)
                    childTransform = collisionComponent.getPartTransform(compIdx)
                    invParentTransform = collisionComponent.getPartTransform(parentCompIdx)
                    invParentTransform.invertOrthonormal()
                    hitPoint = invParentTransform.applyPoint(childTransform.applyPoint(hitPoint))
                    hitDir = invParentTransform.applyVector(childTransform.applyVector(hitDir))
            if not componentName:
                componentName = TankPartNames.CHASSIS
            rot = Matrix()
            rot.setRotateYPR((hitDir.yaw, hitDir.pitch, 0.0))
            matrix = Matrix()
            matrix.setTranslate(hitPoint)
            matrix.preMultiply(rot)
            effectGroup = cls._HIT_EFFECT_CODE_TO_EFFECT_GROUP[hitEffectCode]
            resultPoints.append(DamageFromShotDecoder.ShotPoint(componentName, compIdx, matrix, hitEffectCode, effectGroup, isDynCollision))

        return resultPoints

    @classmethod
    def parseHitPoint(cls, hitPoint, collisionComponent):
        networkID = hitPoint['networkID']
        segment = hitPoint['segment']
        if networkID == cgf_network.C_INVALID_NETWORK_OBJECT_ID:
            compIndex = cls.convertComponentIndex(getComponentIndexFromEncodedSegment(segment), collisionComponent)
        else:
            compIndex = cls.getPartIndexByNetworkID(collisionComponent.spaceID, networkID)
            if compIndex is None:
                return
        if not collisionComponent.hasAttachment(compIndex):
            LOG_CODEPOINT_WARNING(compIndex)
            return
        else:
            _, data, start, end = decodeSegment(segment, collisionComponent.getBoundingBox(compIndex))
            return (compIndex,
             data,
             start,
             end)

    @classmethod
    def getPartIndexByNetworkID(cls, spaceID, networkID):
        gameObject = cgf_network.getGameObjectByNetworkID(spaceID, networkID)
        if not gameObject.isValid():
            LOG_DEBUG_DEV("[DamageFromShotDecoder] Can't find game object for networkID {}".format(networkID))
            return None
        else:
            linker = gameObject.findComponentByType(Physics.DynamicCollisionLinker)
            if linker and linker.collisionPartIndexes:
                return linker.collisionPartIndexes[cls._PRIMARY_COLLISION_INDEX]
            LOG_DEBUG_DEV("[DamageFromShotDecoder] Can't find collision for networkID {}".format(networkID))
            return None


class RepaintParams(object):

    @staticmethod
    def getRepaintParams(vehicleDescr):
        tintGroups = vehicles.g_cache.customization(vehicleDescr.type.customizationNationID)['tintGroups']
        for i in tintGroups.keys():
            grp = tintGroups[i]
            repaintReplaceColor = Vector4(grp.x, grp.y, grp.z, 0.0) / 255.0

        refColor = vehicleDescr.type.repaintParameters['refColor'] / 255.0
        repaintReferenceGloss = vehicleDescr.type.repaintParameters['refGloss'] / 255.0
        repaintColorRangeScale = vehicleDescr.type.repaintParameters['refColorMult']
        repaintGlossRangeScale = vehicleDescr.type.repaintParameters['refGlossMult']
        repaintReferenceColor = Vector4(refColor.x, refColor.y, refColor.z, repaintReferenceGloss)
        repaintReplaceColor.w = repaintColorRangeScale
        return (repaintReferenceColor, repaintReplaceColor, repaintGlossRangeScale)
