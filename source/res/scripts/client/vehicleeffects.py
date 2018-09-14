# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VehicleEffects.py
from collections import namedtuple
from functools import partial
import BigWorld
import Math
import Pixie
from Math import Matrix
from constants import VEHICLE_HIT_EFFECT
from debug_utils import LOG_CODEPOINT_WARNING, LOG_WARNING, LOG_ERROR
from items import _xml
import material_kinds
from helpers.EffectMaterialCalculation import calcEffectMaterialIndex
from CustomEffect import RangeTable
from helpers import PixieBG
from vehicle_systems.stricted_loading import restrictBySpaceAndNode, restrictBySpace
from vehicle_systems.tankStructure import TankNodeNames, TankPartNames
from vehicle_systems.assembly_utility import Component
DUMMY_NODE_PREFIX = 'DM'

class VehicleTrailEffects(Component):
    _DRAW_ORDER_IDX = 102
    enabled = property(lambda self: self.__enabled)
    _TRAIL_E_PIXIE_ORDER = 0
    _TRAIL_E_PIXIE_NODE = 1
    _TRAIL_E_PIXIE_FILE = 2
    _TRAIL_E_PIXIE_INDEX = 3
    _TRAIL_E_PIXIE_ACTIVE = 4
    _TRAIL_E_PIXIE_EFFECTS = 5

    def __init__(self, vehicle):
        self.__vehicle = vehicle
        chassisModel = self.__vehicle.appearance.compoundModel
        topRightCarryingPoint = self.__vehicle.typeDescriptor.chassis['topRightCarryingPoint']
        self.__enabled = True
        self.__trailParticleNodes = []
        self.__trailParticles = {}
        mMidLeft = Math.Matrix()
        mMidLeft.setTranslate((-topRightCarryingPoint[0], 0, 0))
        mMidRight = Math.Matrix()
        mMidRight.setTranslate((topRightCarryingPoint[0], 0, 0))
        self.__trailParticleNodes = [chassisModel.node(TankNodeNames.TRACK_LEFT_MID, mMidLeft), chassisModel.node(TankNodeNames.TRACK_RIGHT_MID, mMidRight)]
        i = 0
        for nodeName in (TankNodeNames.TRACK_LEFT_FRONT,
         TankNodeNames.TRACK_RIGHT_FRONT,
         TankNodeNames.TRACK_LEFT_REAR,
         TankNodeNames.TRACK_RIGHT_REAR):
            identity = Math.Matrix()
            identity.setIdentity()
            node = chassisModel.node(nodeName)
            if node is None:
                raise Exception('Node %s is not found' % nodeName)
            chassisModel.node(nodeName, Math.Matrix(node.localMatrix))
            self.__trailParticleNodes.append(node)

        identity = Math.Matrix()
        identity.setIdentity()
        self.__centerNode = chassisModel.node(TankNodeNames.CHASSIS_MID_TRAIL, identity)
        self.__trailParticlesDelayBeforeShow = BigWorld.time() + 4.0
        return

    def destroy(self):
        self.stopEffects()
        self.__trailParticleNodes = None
        self.__trailParticles = None
        self.__centerNode = None
        self.__vehicle = None
        return

    def getTrackCenterNode(self, trackIdx):
        return self.__trailParticleNodes[trackIdx]

    def enable(self, isEnabled):
        if self.__enabled and not isEnabled:
            self.stopEffects()
        self.__enabled = isEnabled

    def stopEffects(self):
        for node in self.__trailParticles.iterkeys():
            for trail in self.__trailParticles[node]:
                if trail[0] is not None:
                    node.detach(trail[0])

        self.__trailParticles = {}
        return

    def update(self):
        vehicle = self.__vehicle
        vehicleAppearance = self.__vehicle.appearance
        if not self.__enabled:
            return
        elif vehicle.typeDescriptor.chassis['effects'] is None:
            self.__enabled = False
            return
        else:
            time = BigWorld.time()
            if time < self.__trailParticlesDelayBeforeShow:
                return
            movementInfo = Math.Vector4(vehicleAppearance.fashion.movementInfo.value)
            vehicleSpeedRel = vehicle.speedInfo.value[2] / vehicle.typeDescriptor.physics['speedLimits'][0]
            tooSlow = abs(vehicleSpeedRel) < 0.1
            waterHeight = None if not vehicleAppearance.isInWater else vehicleAppearance.waterHeight
            effectIndexes = self.__getEffectIndexesUnderVehicle(vehicleAppearance)
            self.__updateNodePosition(self.__centerNode, vehicle.position, waterHeight)
            centerEffectIdx = effectIndexes[2]
            if not tooSlow and not vehicleAppearance.isUnderwater:
                self.__createTrailParticlesIfNeeded(self.__centerNode, 0, 'dust', centerEffectIdx, VehicleTrailEffects._DRAW_ORDER_IDX, True)
            centerNodeEffects = self.__trailParticles.get(self.__centerNode)
            if centerNodeEffects is not None:
                for nodeEffect in centerNodeEffects:
                    stopParticles = nodeEffect[1] != centerEffectIdx or vehicleAppearance.isUnderwater or tooSlow
                    self.__updateNodeEffect(nodeEffect, self.__centerNode, centerNodeEffects, vehicleSpeedRel, stopParticles)

            for iTrack in xrange(2):
                trackSpeedRel = movementInfo[iTrack + 1]
                trackSpeedRel = 0.0 if trackSpeedRel == 0 else abs(vehicleSpeedRel) * trackSpeedRel / abs(trackSpeedRel)
                activeCornerNode = self.__trailParticleNodes[2 + iTrack + (0 if trackSpeedRel <= 0 else 2)]
                inactiveCornerNode = self.__trailParticleNodes[2 + iTrack + (0 if trackSpeedRel > 0 else 2)]
                self.__updateNodePosition(activeCornerNode, vehicle.position, waterHeight)
                self.__updateNodePosition(inactiveCornerNode, vehicle.position, waterHeight)
                currEffectIndex = effectIndexes[iTrack]
                if not tooSlow and not vehicleAppearance.isUnderwater:
                    self.__createTrailParticlesIfNeeded(activeCornerNode, iTrack, 'mud', currEffectIndex, VehicleTrailEffects._DRAW_ORDER_IDX + iTrack, True)
                    self.__createTrailParticlesIfNeeded(inactiveCornerNode, iTrack, 'mud', currEffectIndex, VehicleTrailEffects._DRAW_ORDER_IDX + iTrack, False)
                for node in (activeCornerNode, inactiveCornerNode):
                    nodeEffects = self.__trailParticles.get(node)
                    if nodeEffects is not None:
                        for nodeEffect in nodeEffects:
                            createdForActiveNode = nodeEffect[5]
                            stopParticlesOnDirChange = node == activeCornerNode and not createdForActiveNode or node == inactiveCornerNode and createdForActiveNode
                            stopParticles = nodeEffect[1] != currEffectIndex or stopParticlesOnDirChange or vehicleAppearance.isUnderwater or tooSlow
                            self.__updateNodeEffect(nodeEffect, node, nodeEffects, trackSpeedRel, stopParticles)

            return

    def __getEffectIndexesUnderVehicle(self, vehicleAppearance):
        correctedMatKinds = [ (material_kinds.WATER_MATERIAL_KIND if vehicleAppearance.isInWater else matKind) for matKind in vehicleAppearance.terrainMatKind ]
        return map(calcEffectMaterialIndex, correctedMatKinds)

    def __updateNodePosition(self, node, vehiclePos, waterHeight):
        if waterHeight is not None:
            toCenterShift = vehiclePos.y - (Math.Matrix(node).translation.y - node.local.translation.y)
            node.local.translation.y = waterHeight + toCenterShift
        else:
            node.local.translation.y = 0
        return

    def __createTrailParticlesIfNeeded(self, node, iTrack, effectGroup, effectIndex, drawOrder, isActiveNode):
        if effectIndex is None:
            return
        else:
            effectDesc = self.__vehicle.typeDescriptor.chassis['effects'].get(effectGroup)
            if effectDesc is None:
                return
            effectName = effectDesc[0].get(effectIndex)
            if effectName is None or effectName == 'none' or effectName == 'None':
                return
            if isinstance(effectName, list):
                effectIdx = iTrack
                effectIdx += 0 if isActiveNode else 2
                effectName = effectName[effectIdx]
            nodeEffects = self.__trailParticles.get(node)
            if nodeEffects is None:
                nodeEffects = []
                self.__trailParticles[node] = nodeEffects
            else:
                for nodeEffect in nodeEffects:
                    createdForActiveNode = nodeEffect[5]
                    if nodeEffect[1] == effectIndex and createdForActiveNode == isActiveNode:
                        return

            effectRecord = [None,
             effectIndex,
             0,
             0,
             0.0,
             isActiveNode]
            elemDesc = [drawOrder,
             node,
             effectName,
             effectIndex,
             isActiveNode,
             effectRecord]
            nodeEffects.append(effectRecord)
            Pixie.createBG(effectName, restrictBySpaceAndNode(node, self._callbackTrailParticleLoaded, elemDesc))
            return

    def _callbackTrailParticleLoaded(self, elemDesc, pixie):
        if self.__vehicle is None or self.__vehicle.model is None:
            LOG_WARNING("The vehicle object is 'None', can't attach pixie '%s'" % elemDesc[self._TRAIL_E_PIXIE_FILE])
            return
        elif pixie is None:
            LOG_ERROR("Can't create pixie '%s'." % elemDesc[self._TRAIL_E_PIXIE_FILE])
            return
        else:
            pixie.drawOrder = elemDesc[self._TRAIL_E_PIXIE_ORDER]
            elemDesc[self._TRAIL_E_PIXIE_NODE].attach(pixie)
            basicRates = []
            for i in xrange(pixie.nSystems()):
                try:
                    source = pixie.system(i).action(1)
                    basicRates.append(source.rate)
                    source.rate = source.rate * 0.001
                except:
                    basicRates.append(-1.0)
                    source = pixie.system(i).action(16)
                    source.MultRate(0.01)

            elemDesc[self._TRAIL_E_PIXIE_EFFECTS][0] = pixie
            elemDesc[self._TRAIL_E_PIXIE_EFFECTS][4] = basicRates
            return

    def __updateNodeEffect(self, nodeEffect, node, nodeEffects, relSpeed, stopParticles):
        relEmissionRate = 0.0 if stopParticles else abs(relSpeed)
        basicEmissionRates = nodeEffect[4]
        pixie = nodeEffect[0]
        if pixie is None:
            return
        else:
            for i in xrange(pixie.nSystems()):
                if basicEmissionRates[i] < 0:
                    source = pixie.system(i).action(16)
                    source.MultRate(relEmissionRate)
                source = pixie.system(i).action(1)
                source.rate = relEmissionRate * basicEmissionRates[i]

            effectInactive = relEmissionRate < 0.0001
            if effectInactive:
                time = BigWorld.time()
                timeOfStop = nodeEffect[3]
                if timeOfStop == 0:
                    nodeEffect[3] = time
                elif time - timeOfStop > 5.0 or material_kinds.EFFECT_MATERIALS[nodeEffect[1]] == 'water':
                    pixie = nodeEffect[0]
                    node.detach(pixie)
                    nodeEffects.remove(nodeEffect)
            else:
                nodeEffect[3] = 0
            return


class ExhaustEffectsDescriptor(object):

    def __init__(self, dataSection):
        try:
            self.tables = []
            states = ('start', 'idle', 'mainLoad', 'highLoad')
            for state in states:
                effectSection = dataSection[state]
                rpm = effectSection.readString('rpm', '0')
                rpm = map(float, rpm.split())
                effects = effectSection.readString('effects', '')
                effects = effects.split()
                if not effects:
                    effects.append('')
                assert len(rpm) == len(effects), 'rpm size differs from effects'
                self.tables.append(RangeTable(rpm, effects))

        except Exception as exp:
            raise Exception('error reading exhaust effects %s, got %s' % (dataSection.name, exp))


class VehicleExhaustDescriptor(object):

    def __init__(self, dataSection, exhaustEffectsDescriptors, xmlCtx):
        self.nodes = _xml.readNonEmptyString(xmlCtx, dataSection, 'exhaust/nodes').split()
        defaultPixieName = _xml.readNonEmptyString(xmlCtx, dataSection, 'exhaust/pixie')
        dieselPixieName = defaultPixieName
        gasolinePixieName = defaultPixieName
        exhaustTagsSection = dataSection['exhaust/tags']
        if exhaustTagsSection is not None:
            dieselPixieName = exhaustTagsSection.readString('diesel', dieselPixieName)
            gasolinePixieName = exhaustTagsSection.readString('gasoline', gasolinePixieName)
        tmpDefault = exhaustEffectsDescriptors['default']
        self.diesel = exhaustEffectsDescriptors.get(dieselPixieName, tmpDefault)
        self.gasoline = exhaustEffectsDescriptors.get(gasolinePixieName, tmpDefault)
        return

    def prerequisites(self):
        prereqs = set()
        allTables = list(self.diesel.tables)
        allTables += self.gasoline.tables
        for table in allTables:
            for effectName in table.values:
                prereqs.add(effectName)

        return prereqs


class ExhaustEffectsCache():
    activeEffect = property(lambda self: self.__activeEffect)
    maxDrawOrder = property(lambda self: self.__maxDrawOrder)
    uniqueEffects = property(lambda self: self.__uniqueEffects)
    node = property(lambda self: self.__node)
    _EXHAUST_E_PIXE_NAME = 0
    _EXHAUST_E_PIXE_LIST = 1

    def __init__(self, exhaustEffectsDescriptor, drawOrder, uniqueEffects=None):
        if uniqueEffects is None:
            self.__uniqueEffects = {}
        else:
            self.__uniqueEffects = {name:effect.clone() for name, effect in uniqueEffects.iteritems()}
        self.__tables = []
        self.__maxDrawOrder = drawOrder - 1
        self.__node = None
        for rangeTable in exhaustEffectsDescriptor.tables:
            effectsValues = []
            for name in rangeTable.values:
                effect = self.__uniqueEffects.get(name)
                if effect is None:
                    elemDesc = [name, effectsValues]
                    Pixie.createBG(name, restrictBySpace(self._callbackExhaustPixieLoaded, elemDesc))
                effectsValues.append(effect)

            self.__tables.append(RangeTable(rangeTable.keys, effectsValues))

        if self.__maxDrawOrder < drawOrder:
            self.__maxDrawOrder = drawOrder
        self.__activeEffect = None
        return

    def attachNode(self, node):
        self.detach()
        self.__node = node
        for effect in self.__uniqueEffects.itervalues():
            self.__node.attach(effect)

    def detach(self):
        if self.__node is not None:
            for effect in self.__uniqueEffects.itervalues():
                self.__node.detach(effect)

            self.__node = None
        return

    def destroy(self):
        self.detach()

    def clone(self, exhaustEffectsDescriptor, drawOrder):
        return ExhaustEffectsCache(exhaustEffectsDescriptor, drawOrder, self.__uniqueEffects)

    def changeActiveEffect(self, engineLoad, engineRPM):
        prevEffect = self.__activeEffect
        self.__activeEffect = self.__tables[engineLoad].lookup(engineRPM, prevEffect)
        return prevEffect != self.__activeEffect

    def _callbackExhaustPixieLoaded(self, elemDesc, pixie):
        effectName = elemDesc[self._EXHAUST_E_PIXE_NAME]
        if pixie is None:
            LOG_ERROR("Can't create pixie '%s'." % effectName)
            return
        else:
            self.__maxDrawOrder += 1
            pixie.drawOrder = self.__maxDrawOrder
            self.__uniqueEffects[effectName] = pixie
            elemDesc[self._EXHAUST_E_PIXE_LIST].append(pixie)
            if self.__node is not None:
                self.__node.attach(pixie)
            PixieBG.enablePixie(pixie, False)
            return


class VehicleExhaustEffects(Component):
    enabled = property(lambda self: self.__enabled)

    def __init__(self, vehicleTypeDescriptor):
        self.__enabled = True
        self.__exhaust = []
        isObserver = 'observer' in vehicleTypeDescriptor.type.tags
        if isObserver:
            self.__enabled = False
            return
        else:
            vehicleExhaustDescriptor = vehicleTypeDescriptor.hull['exhaust']
            engineTags = vehicleTypeDescriptor.engine['tags']
            exhaustDesc = vehicleExhaustDescriptor.diesel if 'diesel' in engineTags else vehicleExhaustDescriptor.gasoline
            effectsCache = None
            for idx, nodeName in enumerate(vehicleExhaustDescriptor.nodes):
                if effectsCache is None:
                    effectsCache = ExhaustEffectsCache(exhaustDesc, 50 + idx)
                else:
                    effectsCache = effectsCache.clone(exhaustDesc, effectsCache.maxDrawOrder + 1)
                self.__exhaust.append(effectsCache)

            return

    def destroy(self):
        for pixieCache in self.__exhaust:
            if pixieCache.activeEffect is not None:
                PixieBG.enablePixie(pixieCache.activeEffect, False)
                pixieCache.activeEffect.clear()

        for effectsCache in self.__exhaust:
            effectsCache.destroy()

        self.__exhaust = []
        return

    def enable(self, isEnabled):
        for pixieCache in self.__exhaust:
            activeEffect = pixieCache.activeEffect
            if activeEffect is not None:
                PixieBG.enablePixie(activeEffect, isEnabled)

        self.__enabled = isEnabled
        return

    def attach(self, hullModel, vehicleExhaustDescriptor):
        for nodeName, nodeAndCache in zip(vehicleExhaustDescriptor.nodes, self.__exhaust):
            node = hullModel.node(nodeName)
            nodeAndCache.attachNode(node)

    def detach(self):
        for pixieCache in self.__exhaust:
            pixieCache.detach()

    def changeExhaust(self, engineMode, rpm):
        if not self.__enabled:
            return
        else:
            for pixieCache in self.__exhaust:
                prevEffect = pixieCache.activeEffect
                shouldReattach = pixieCache.changeActiveEffect(engineMode, rpm)
                if shouldReattach and pixieCache.node is not None:
                    if prevEffect is not None:
                        PixieBG.enablePixie(prevEffect, False)
                    if pixieCache.activeEffect is not None:
                        PixieBG.enablePixie(pixieCache.activeEffect, True)

            return


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
            hitTester = getattr(vehicleDescr, compName)['hitTester']
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
            bbox = vehicleDescr.chassis['hitTester'].bbox
        elif compIdx == 1:
            componentName = TankPartNames.HULL
            bbox = vehicleDescr.hull['hitTester'].bbox
        elif compIdx == 2:
            componentName = TankPartNames.TURRET
            bbox = vehicleDescr.turret['hitTester'].bbox
        elif compIdx == 3:
            componentName = TankPartNames.GUN
            bbox = vehicleDescr.gun['hitTester'].bbox
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
        tintGroups = items.vehicles.g_cache.customization(vehicleDescr.type.customizationNationID)['tintGroups']
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
