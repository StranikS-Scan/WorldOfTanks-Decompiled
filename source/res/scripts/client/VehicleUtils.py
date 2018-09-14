# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VehicleUtils.py
from collections import namedtuple
import BigWorld
import Math
from debug_utils import *
import weakref
from VehicleEffects import VehicleTrailEffects, VehicleExhaustEffects
from constants import IS_DEVELOPMENT, ARENA_GUI_TYPE, VEHICLE_PHYSICS_MODE
import constants
from OcclusionDecal import OcclusionDecal
from ShadowForwardDecal import ShadowForwardDecal
from helpers.CallbackDelayer import CallbackDelayer
from helpers import bound_effects, DecalMap, isPlayerAvatar, newFakeModel
from helpers.EffectsList import EffectsListPlayer, SpecialKeyPointNames
import items.vehicles
import random
import math
import time
from Event import Event
from functools import partial
import material_kinds
from VehicleStickers import VehicleStickers
import AuxiliaryFx
import TriggersManager
from TriggersManager import TRIGGER_TYPE
from Vibroeffects.ControllersManager import ControllersManager as VibrationControllersManager
from LightFx.LightControllersManager import LightControllersManager as LightFxControllersManager
import LightFx.LightManager
import BattleReplay
from vehicle_systems.tankStructure import TankPartNames
from VehicleEffects import RepaintParams
from vehicle_systems.assembly_utility import ComponentSystem, ComponentDescriptor
_ENABLE_VEHICLE_VALIDATION = False
_VEHICLE_DISAPPEAR_TIME = 0.2
_VEHICLE_APPEAR_TIME = 0.2
_ROOT_NODE_NAME = 'V'
_GUN_RECOIL_NODE_NAME = 'G'
_PERIODIC_TIME = 0.25
_PERIODIC_TIME_ENGINE = 0.1
_LOD_DISTANCE_EXHAUST = 200.0
_LOD_DISTANCE_TRAIL_PARTICLES = 100.0
_MOVE_THROUGH_WATER_SOUND = '/vehicles/tanks/water'
_CAMOUFLAGE_MIN_INTENSITY = 1.0
_PITCH_SWINGING_MODIFIERS = (0.9, 1.88, 0.3, 4.0, 1.0, 1.0)
_MIN_DEPTH_FOR_HEAVY_SPLASH = 0.5
_ALLOW_LAMP_LIGHTS = False
MAX_DISTANCE = 500
_MATKIND_COUNT = 3

class StippleManager:

    def __init__(self):
        self.__stippleDescs = {}
        self.__stippleToAddDescs = {}

    def showFor(self, vehicle, model):
        if not model.stipple:
            model.stipple = True
            callbackID = BigWorld.callback(0.0, partial(self.__addStippleModel, vehicle.id))
            self.__stippleToAddDescs[vehicle.id] = (model, callbackID)

    def hideIfExistFor(self, vehicle):
        desc = self.__stippleDescs.get(vehicle.id)
        if desc is not None:
            BigWorld.cancelCallback(desc[1])
            BigWorld.player().delModel(desc[0])
            desc[0].reset()
            del self.__stippleDescs[vehicle.id]
        desc = self.__stippleToAddDescs.get(vehicle.id)
        if desc is not None:
            BigWorld.cancelCallback(desc[1])
            del self.__stippleToAddDescs[vehicle.id]
        return

    def destroy(self):
        for model, callbackID in self.__stippleDescs.itervalues():
            BigWorld.cancelCallback(callbackID)
            model.reset()
            BigWorld.player().delModel(model)

        for model, callbackID in self.__stippleToAddDescs.itervalues():
            model.reset()
            BigWorld.cancelCallback(callbackID)

        self.__stippleDescs = None
        self.__stippleToAddDescs = None
        return

    def __addStippleModel(self, vehID):
        model = self.__stippleToAddDescs[vehID][0]
        if False:
            callbackID = BigWorld.callback(0.0, partial(self.__addStippleModel, vehID))
            self.__stippleToAddDescs[vehID] = (model, callbackID)
            return
        del self.__stippleToAddDescs[vehID]
        BigWorld.player().addModel(model)
        callbackID = BigWorld.callback(_VEHICLE_DISAPPEAR_TIME, partial(self.__removeStippleModel, vehID))
        self.__stippleDescs[vehID] = (model, callbackID)

    def __removeStippleModel(self, vehID):
        model = self.__stippleDescs[vehID][0]
        BigWorld.player().delModel(model)
        model.reset()
        del self.__stippleDescs[vehID]


class _CrashedTrackController:

    def __init__(self, vehicle, va):
        self.__vehicle = vehicle.proxy
        self.__va = weakref.ref(va)
        self.__flags = 0
        self.__model = None
        self.__fashion = None
        self.__inited = True
        self.__forceHide = False
        self.__loadInfo = [False, False]
        return

    def isLeftTrackBroken(self):
        return self.__flags & 1

    def isRightTrackBroken(self):
        return self.__flags & 2

    def destroy(self):
        self.__vehicle = None
        return

    def setVisible(self, bool):
        self.__forceHide = not bool
        self.__setupTracksHiding(not bool)

    def addTrack(self, isLeft):
        if not self.__inited:
            return
        else:
            if self.__flags == 0 and self.__vehicle is not None and self.__vehicle.isPlayerVehicle:
                TriggersManager.g_manager.activateTrigger(TRIGGER_TYPE.PLAYER_VEHICLE_TRACKS_DAMAGED)
            if self.__vehicle.filter.placingOnGround:
                flying = self.__vehicle.filter.numLeftTrackContacts == 0
                self.__flags |= 1 if isLeft else 2
            elif isLeft:
                flying = self.__va().fashion.isFlyingLeft
                self.__flags |= 1
            else:
                flying = self.__va().fashion.isFlyingRight
                self.__flags |= 2
            if self.__model is None and not flying:
                self.__loadInfo = [True, isLeft]
                BigWorld.fetchModel(self.__va().modelsDesc['chassis']['_stateFunc'](self.__vehicle, 'destroyed'), self.__onModelLoaded)
            if self.__fashion is None:
                self.__fashion = BigWorld.WGVehicleFashion(True, 1.0, True, 'wheeledVehicle' in self.__vehicle.type.tags)
                _setupVehicleFashion(self, self.__fashion, self.__vehicle, True)
            self.__fashion.setCrashEffectCoeff(0.0)
            self.__setupTracksHiding()
            return

    def delTrack(self, isLeft):
        if not self.__inited or self.__fashion is None:
            return
        else:
            if self.__loadInfo[0] and self.__loadInfo[1] == isLeft:
                self.__loadInfo = [False, False]
            if isLeft:
                self.__flags &= -2
            else:
                self.__flags &= -3
            self.__setupTracksHiding()
            if self.__flags == 0 and self.__model is not None:
                self.__va().modelsDesc['chassis']['model'].root.detach(self.__model)
                self.__model = None
                self.__fashion = None
            if self.__flags != 0 and self.__vehicle is not None and self.__vehicle.isPlayerVehicle:
                TriggersManager.g_manager.deactivateTrigger(TRIGGER_TYPE.PLAYER_VEHICLE_TRACKS_DAMAGED)
            return

    def receiveShotImpulse(self, dir, impulse):
        if not self.__inited or self.__fashion is None:
            return
        else:
            self.__fashion.receiveShotImpulse(dir, impulse)
            return

    def reset(self):
        if not self.__inited:
            return
        else:
            if self.__fashion is not None:
                self.__fashion.setCrashEffectCoeff(-1.0)
            self.__flags = 0
            if self.__model is not None:
                self.__va().modelsDesc['chassis']['model'].root.detach(self.__model)
                self.__model = None
                self.__fashion = None
            return

    def __setupTracksHiding(self, force=False):
        if force or self.__forceHide:
            tracks = (True, True)
            invTracks = (True, True)
        else:
            tracks = (self.__flags & 1, self.__flags & 2)
            invTracks = (not tracks[0], not tracks[1])
        self.__va().fashion.hideTracks(*tracks)
        if self.__fashion is not None:
            self.__fashion.hideTracks(*invTracks)
        return

    def __onModelLoaded(self, model):
        if self.__va() is None or not self.__loadInfo[0] or not self.__inited:
            return
        else:
            va = self.__va()
            self.__loadInfo = [False, False]
            if model:
                self.__model = model
            else:
                self.__inited = False
                modelState = va.modelsDesc['chassis']['_stateFunc'](self.__vehicle, 'destroyed')
                LOG_ERROR('Model %s not loaded.' % modelState)
                return
            try:
                self.__model.wg_fashion = self.__fashion
                va.modelsDesc['chassis']['model'].root.attach(self.__model)
            except:
                va.fashion.hideTracks(False, False)
                self.__inited = False
                LOG_CURRENT_EXCEPTION()

            return


class _SkeletonCollider:

    def __init__(self, vehicle, vehicleAppearance):
        self.__vehicle = vehicle.proxy
        self.__vAppearance = weakref.proxy(vehicleAppearance)
        self.__boxAttachments = list()
        descr = vehicle.typeDescriptor
        descList = [('Scene Root', descr.chassis['hitTester'].bbox),
         ('Scene Root', descr.hull['hitTester'].bbox),
         ('Scene Root', descr.turret['hitTester'].bbox),
         ('Scene Root', descr.gun['hitTester'].bbox)]
        self.__createBoxAttachments(descList)
        vehicle.skeletonCollider = BigWorld.SkeletonCollider()
        for boxAttach in self.__boxAttachments:
            vehicle.skeletonCollider.addCollider(boxAttach)

    def destroy(self):
        delattr(self.__vehicle, 'skeletonCollider')
        self.__vehicle = None
        self.__vAppearance = None
        self.__boxAttachments = None
        return

    def attach(self):
        va = self.__vAppearance.modelsDesc
        collider = self.__vehicle.skeletonCollider.getCollider(0)
        va['chassis']['model'].node(collider.name).attach(collider)
        collider = self.__vehicle.skeletonCollider.getCollider(1)
        va['hull']['model'].node(collider.name).attach(collider)
        collider = self.__vehicle.skeletonCollider.getCollider(2)
        va['turret']['model'].node(collider.name).attach(collider)
        collider = self.__vehicle.skeletonCollider.getCollider(3)
        va['gun']['model'].node(collider.name).attach(collider)

    def detach(self):
        va = self.__vAppearance.modelsDesc
        collider = self.__vehicle.skeletonCollider.getCollider(0)
        va['chassis']['model'].node(collider.name).detach(collider)
        collider = self.__vehicle.skeletonCollider.getCollider(1)
        va['hull']['model'].node(collider.name).detach(collider)
        collider = self.__vehicle.skeletonCollider.getCollider(2)
        va['turret']['model'].node(collider.name).detach(collider)
        collider = self.__vehicle.skeletonCollider.getCollider(3)
        va['gun']['model'].node(collider.name).detach(collider)

    def __createBoxAttachments(self, descList):
        for desc in descList:
            boxAttach = BigWorld.BoxAttachment()
            boxAttach.name = desc[0]
            boxAttach.minBounds = desc[1][0]
            boxAttach.maxBounds = desc[1][1]
            self.__boxAttachments.append(boxAttach)


def _almostZero(val, epsilon=0.0004):
    return -epsilon < val < epsilon


def _createWheelsListByTemplate(startIndex, template, count):
    return [ '%s%d' % (template, i) for i in range(startIndex, startIndex + count) ]


def _setupVehicleFashion(self, fashion, vehicle, isCrashedTrack=False):
    vDesc = vehicle.typeDescriptor
    tracesCfg = vDesc.chassis['traces']
    try:
        isTrackFashionSet = setupTracksFashion(fashion, vehicle.typeDescriptor, isCrashedTrack)
        if isinstance(vehicle.filter, BigWorld.WGVehicleFilter):
            fashion.physicsInfo = vehicle.filter.physicsInfo
            fashion.movementInfo = vehicle.filter.movementInfo
            vehicle.filter.placingOnGround = vehicle.filter.placingOnGround if isTrackFashionSet else False
        if 'wheeledVehicle' in vDesc.type.tags:
            for tr in tracesCfg:
                textures = {}
                for matKindName, texId in DecalMap.g_instance.getTextureSet(tr['textureSet']).iteritems():
                    if matKindName != 'bump':
                        for matKind in material_kinds.EFFECT_MATERIAL_IDS_BY_NAMES[matKindName]:
                            textures[matKind] = texId

                fashion.addTrackTraces(tr['bufferPrefs'], textures, tr['centerOffset'], tr['size'], tr['isLeading'])

        else:
            textures = {}
            for matKindName, texId in DecalMap.g_instance.getTextureSet(tracesCfg['textureSet']).iteritems():
                if matKindName != 'bump':
                    for matKind in material_kinds.EFFECT_MATERIAL_IDS_BY_NAMES[matKindName]:
                        textures[matKind] = texId

            fashion.addTrackTraces(tracesCfg['bufferPrefs'], textures, tracesCfg['centerOffset'], tracesCfg['size'], False)
    except:
        LOG_CURRENT_EXCEPTION()


def setupTracksFashion(fashion, vDesc, isCrashedTrack=False):
    retValue = True
    tracesCfg = vDesc.chassis['traces']
    tracksCfg = vDesc.chassis['tracks']
    wheelsCfg = vDesc.chassis['wheels']
    groundNodesCfg = vDesc.chassis['groundNodes']
    suspensionArmsCfg = vDesc.chassis['suspensionArms']
    trackNodesCfg = vDesc.chassis['trackNodes']
    trackParams = vDesc.chassis['trackParams']
    swingingCfg = vDesc.hull['swinging']
    splineDesc = vDesc.chassis['splineDesc']
    pp = tuple((p * m for p, m in zip(swingingCfg['pitchParams'], _PITCH_SWINGING_MODIFIERS)))
    splineLod = 9999
    tracesLodDist = tracesCfg['lodDist'] if 'lodDist' in tracesCfg else tracesCfg[0]['lodDist']
    if splineDesc is not None:
        splineLod = splineDesc['lodDist']
    fashion.setLods(tracesLodDist, wheelsCfg['lodDist'], tracksCfg['lodDist'], splineLod)
    fashion.setTracks(tracksCfg['leftMaterial'], tracksCfg['rightMaterial'], tracksCfg['textureScale'])
    if isCrashedTrack:
        return retValue
    else:
        for group in wheelsCfg['groups']:
            nodes = _createWheelsListByTemplate(group[3], group[1], group[2])
            fashion.addWheelGroup(group[0], group[4], nodes)

        for wheel in wheelsCfg['wheels']:
            fashion.addWheel(wheel[0], wheel[2], wheel[1], wheel[3], wheel[4])

        for groundGroup in groundNodesCfg['groups']:
            nodes = _createWheelsListByTemplate(groundGroup[3], groundGroup[1], groundGroup[2])
            retValue = not fashion.addGroundNodesGroup(nodes, groundGroup[0], groundGroup[4], groundGroup[5])

        for groundNode in groundNodesCfg['nodes']:
            retValue = not fashion.addGroundNode(groundNode[0], groundNode[1], groundNode[2], groundNode[3])

        for suspensionArm in suspensionArmsCfg:
            if suspensionArm[3] is not None and suspensionArm[4] is not None:
                retValue = not fashion.addSuspensionArm(suspensionArm[0], suspensionArm[1], suspensionArm[2], suspensionArm[3], suspensionArm[4])
            if suspensionArm[5] is not None and suspensionArm[6] is not None:
                retValue = not fashion.addSuspensionArmWheels(suspensionArm[0], suspensionArm[1], suspensionArm[2], suspensionArm[5], suspensionArm[6])

        if trackParams is not None:
            fashion.setTrackParams(trackParams['thickness'], trackParams['gravity'], trackParams['maxAmplitude'], trackParams['maxOffset'])
        for trackNode in trackNodesCfg['nodes']:
            leftSibling = trackNode[5]
            if leftSibling is None:
                leftSibling = ''
            rightSibling = trackNode[6]
            if rightSibling is None:
                rightSibling = ''
            fashion.addTrackNode(trackNode[0], trackNode[1], trackNode[2], trackNode[3], trackNode[4], leftSibling, rightSibling, trackNode[7], trackNode[8])

        fashion.initialUpdateTracks(1.0, 10.0)
        return retValue


SplineTracks = namedtuple('SplineTracks', ('left', 'right'))

def setupSplineTracks(fashion, vDesc, chassisModel, prereqs):
    splineDesc = vDesc.chassis['splineDesc']
    resultTracks = None
    if splineDesc is not None:
        leftSpline = None
        rightSpline = None
        segmentModelLeft = segmentModelRight = segment2ModelLeft = segment2ModelRight = None
        modelName = splineDesc['segmentModelLeft']
        try:
            segmentModelLeft = prereqs[modelName]
        except Exception:
            LOG_ERROR("can't load track segment model <%s>" % modelName)

        modelName = splineDesc['segmentModelRight']
        try:
            segmentModelRight = prereqs[modelName]
        except Exception:
            LOG_ERROR("can't load track segment model <%s>" % modelName)

        modelName = splineDesc['segment2ModelLeft']
        if modelName is not None:
            try:
                segment2ModelLeft = prereqs[modelName]
            except Exception:
                LOG_ERROR("can't load track segment 2 model <%s>" % modelName)

        modelName = splineDesc['segment2ModelRight']
        if modelName is not None:
            try:
                segment2ModelRight = prereqs[modelName]
            except Exception:
                LOG_ERROR("can't load track segment 2 model <%s>" % modelName)

        if segmentModelLeft is not None and segmentModelRight is not None:
            identityMatrix = Math.Matrix()
            identityMatrix.setIdentity()
            if splineDesc['leftDesc'] is not None:
                leftSpline = BigWorld.wg_createSplineTrack(fashion, chassisModel, splineDesc['leftDesc'], splineDesc['segmentLength'], segmentModelLeft, splineDesc['segmentOffset'], segment2ModelLeft, splineDesc['segment2Offset'], _ROOT_NODE_NAME, splineDesc['atlasUTiles'], splineDesc['atlasVTiles'])
                if leftSpline is not None:
                    chassisModel.root.attach(leftSpline, identityMatrix, True)
            if splineDesc['rightDesc'] is not None:
                rightSpline = BigWorld.wg_createSplineTrack(fashion, chassisModel, splineDesc['rightDesc'], splineDesc['segmentLength'], segmentModelRight, splineDesc['segmentOffset'], segment2ModelRight, splineDesc['segment2Offset'], _ROOT_NODE_NAME, splineDesc['atlasUTiles'], splineDesc['atlasVTiles'])
                if rightSpline is not None:
                    chassisModel.root.attach(rightSpline, identityMatrix, True)
            fashion.setSplineTrack(leftSpline, rightSpline)
        resultTracks = SplineTracks(leftSpline, rightSpline)
    return resultTracks


def _validateCfgPos(srcModelDesc, dstModelDesc, cfgPos, paramName, vehicle, state):
    invMat = Math.Matrix(srcModelDesc['model'].root)
    invMat.invert()
    invMat.preMultiply(Math.Matrix(dstModelDesc['_node']))
    realOffset = invMat.applyToOrigin()
    length = (realOffset - cfgPos).length
    if length > 0.01 and not _almostZero(realOffset.length):
        modelState = srcModelDesc['_stateFunc'](vehicle, state)
        from debug_utils import LOG_WARNING
        LOG_WARNING('%s parameter is incorrect. \n Note: it must be <%s>.\nPlayer: %s; Model: %s' % (paramName,
         realOffset,
         vehicle.publicInfo['name'],
         modelState))
        dstModelDesc['model'].visibleAttachments = True
        dstModelDesc['model'].visible = False


class VehicleDamageState(object):
    MODEL_STATE_NAMES = ('undamaged', 'destroyed', 'exploded')
    __healthToStateMap = {0: 'destruction',
     constants.SPECIAL_VEHICLE_HEALTH.AMMO_BAY_DESTROYED: 'ammoBayBurnOff',
     constants.SPECIAL_VEHICLE_HEALTH.TURRET_DETACHED: 'ammoBayExplosion',
     constants.SPECIAL_VEHICLE_HEALTH.FUEL_EXPLODED: 'fuelExplosion',
     constants.SPECIAL_VEHICLE_HEALTH.DESTR_BY_FALL_RAMMING: 'rammingDestruction'}

    @staticmethod
    def getState(health, isCrewActive, isUnderWater):
        if health > 0:
            if not isCrewActive:
                if isUnderWater:
                    return 'submersionDeath'
                else:
                    return 'crewDeath'
            else:
                return 'alive'
        else:
            return VehicleDamageState.__healthToStateMap[health]

    __stateToModelEffectsMap = {'ammoBayExplosion': ('exploded', None),
     'ammoBayBurnOff': ('destroyed', None),
     'fuelExplosion': ('destroyed', 'fuelExplosion'),
     'destruction': ('destroyed', 'destruction'),
     'crewDeath': ('undamaged', 'crewDeath'),
     'rammingDestruction': ('destroyed', 'rammingDestruction'),
     'submersionDeath': ('undamaged', 'submersionDeath'),
     'alive': ('undamaged', 'empty')}

    @staticmethod
    def getStateParams(state):
        return VehicleDamageState.__stateToModelEffectsMap[state]

    state = property(lambda self: self.__state)
    modelState = property(lambda self: self.__model)
    isCurrentModelDamaged = property(lambda self: VehicleDamageState.isDamagedModel(self.modelState))
    isCurrentModelExploded = property(lambda self: VehicleDamageState.isExplodedModel(self.modelState))
    effect = property(lambda self: self.__effect)

    @staticmethod
    def isDamagedModel(model):
        return model != 'undamaged'

    @staticmethod
    def isExplodedModel(model):
        return model == 'exploded'

    def __init__(self):
        self.__state = None
        self.__model = None
        self.__effect = None
        return

    def update(self, health, isCrewActive, isUnderWater):
        self.__state = VehicleDamageState.getState(health, isCrewActive, isUnderWater)
        params = VehicleDamageState.getStateParams(self.__state)
        self.__model, self.__effect = params
