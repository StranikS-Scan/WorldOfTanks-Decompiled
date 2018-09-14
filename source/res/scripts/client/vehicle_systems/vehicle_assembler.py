# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/vehicle_assembler.py
from CustomEffectManager import CustomEffectManager
from VehicleEffects import VehicleExhaustEffects, VehicleTrailEffects
from vehicle_systems import model_assembler
from vehicle_systems.CompoundAppearance import CompoundAppearance
from vehicle_systems.components.mark_turret import MarkTurret
from vehicle_systems.components.world_connectors import GunRotatorConnector
from vehicle_systems.model_assembler import prepareCompoundAssembler
import functools
from constants import VEHICLE_PHYSICS_MODE
from vehicle_systems.components.vehicle_audition_wwise import EngineAuditionWWISE, TrackCrashAuditionWWISE
import weakref
import BigWorld
import WoT
from vehicle_systems.components.engine_state import DetailedEngineStateWWISE
from vehicle_systems.components.highlighter import Highlighter
from helpers import gEffectsDisabled
import DataLinks
from vehicle_systems.tankStructure import TankNodeNames, TankPartNames

def createAssembler(vehicle):
    return PanzerAssemblerWWISE(vehicle)


class VehicleAssemblerAbstract(object):
    appearance = property()

    def __init__(self):
        pass

    def prerequisites(self):
        return None

    def constructAppearance(self, prereqs):
        return None


class _CompoundAssembler(VehicleAssemblerAbstract):
    appearance = property(lambda self: self.__appearance)

    def __init__(self, vehicle):
        VehicleAssemblerAbstract.__init__(self)
        self.__appearance = CompoundAppearance()
        self.__vehicleRef = weakref.ref(vehicle)

    def prerequisites(self):
        vehicle = self.__vehicleRef()
        prereqs = self.__appearance.prerequisites(vehicle)
        compoundAssembler = prepareCompoundAssembler(vehicle.typeDescriptor, self.__appearance.damageState.modelState, BigWorld.player().spaceID, vehicle.isTurretDetached)
        return prereqs + [compoundAssembler]

    def _assembleParts(self, vehicle, appearance):
        pass

    def constructAppearance(self, prereqs):
        self._assembleParts(self.__vehicleRef(), self.__appearance)
        return self.__appearance


class PanzerAssemblerWWISE(_CompoundAssembler):

    @staticmethod
    def __assembleEngineState(vehicle):
        detailedEngineState = DetailedEngineStateWWISE()
        isPlayerVehicle = vehicle.isPlayerVehicle
        if isPlayerVehicle:
            detailedEngineState.physicRPMLink = lambda : WoT.unpackAuxVehiclePhysicsData(BigWorld.player().ownVehicleAuxPhysicsData)[5]
            detailedEngineState.physicGearLink = lambda : BigWorld.player().ownVehicleGear
        else:
            detailedEngineState.physicRPMLink = lambda : 0.0
            detailedEngineState.physicGearLink = lambda : 0
        return detailedEngineState

    @staticmethod
    def __assembleEngineAudition(vehicle, appearance):
        vehicle = weakref.proxy(vehicle)
        appearance = weakref.proxy(appearance)
        engineAudition = EngineAuditionWWISE(vehicle.physicsMode, vehicle.isPlayerVehicle, appearance.compoundModel, vehicle.typeDescriptor, vehicle.id)
        e = engineAudition
        e.isUnderwaterLink = lambda : appearance.isUnderwater
        e.isInWaterLink = lambda : appearance.isInWater
        e.isFlyingLink = functools.partial(PanzerAssemblerWWISE.__isFlying, vehicle, appearance)
        e.curTerrainMatKindLink = lambda : appearance.terrainMatKind
        e.leftTrackScrollLink = lambda : appearance.leftTrackScroll
        e.leftTrackScrollRelativeLink = lambda : appearance.customEffectManager.getParameter('deltaL')
        e.rightTrackScrollLink = lambda : appearance.rightTrackScroll
        e.rightTrackScrollRelativeLink = lambda : appearance.customEffectManager.getParameter('deltaR')
        e.detailedEngineState = appearance.detailedEngineState
        e.vehicleFilter = vehicle.filter
        return e

    @staticmethod
    def __isFlying(vehicle, appearance):
        filter = vehicle.filter
        if filter.placingOnGround:
            contactsWithGround = filter.numLeftTrackContacts + filter.numRightTrackContacts
            return contactsWithGround == 0
        else:
            return appearance.fashion.isFlying

    @staticmethod
    def __createTrackCrashControl(vehicle, appearance):
        if vehicle.physicsMode == VEHICLE_PHYSICS_MODE.DETAILED:
            if vehicle.isAlive() and appearance.customEffectManager is not None:
                trackCenterNodes = tuple((appearance.customEffectManager.getTrackCenterNode(x) for x in xrange(2)))
                appearance.trackCrashAudition = TrackCrashAuditionWWISE(trackCenterNodes)
        else:
            trackCenterNodes = tuple((appearance.trailEffects.getTrackCenterNode(x) for x in xrange(2)))
            appearance.trackCrashAudition = TrackCrashAuditionWWISE(trackCenterNodes)
        return

    def _assembleParts(self, vehicle, appearance):
        appearance.detailedEngineState = self.__assembleEngineState(vehicle)
        _createEffects(vehicle, appearance)
        if vehicle.isAlive():
            if not appearance.isPillbox and not gEffectsDisabled():
                appearance.engineAudition = self.__assembleEngineAudition(vehicle, appearance)
                appearance.detailedEngineState.onEngineStart += appearance.engineAudition.onEngineStart
            if vehicle.isPlayerVehicle:
                gunRotatorConnector = GunRotatorConnector(appearance.compoundModel)
                appearance.addComponent(gunRotatorConnector)
        self.__createTrackCrashControl(vehicle, appearance)
        appearance.highlighter = Highlighter(vehicle)
        if appearance.fashion is not None:
            lodLink = DataLinks.createFloatLink(appearance.fashion, 'lastLod')
        else:
            lodLink = None
        typeDesc = vehicle.typeDescriptor
        if not appearance.damageState.isCurrentModelDamaged:
            _assembleSwinging(typeDesc, vehicle, lodLink)
        if 'markI' in typeDesc.type.tags:
            _setupMarkTurrets(appearance, typeDesc, lodLink)
        else:
            setupUsualTurret(appearance, typeDesc, lodLink)
        return


def setupUsualTurret(appearance, typeDesc, lodLink):
    if not appearance.damageState.isCurrentModelDamaged:
        appearance.gunRecoil = _assembleRecoil(typeDesc, appearance, lodLink, 'G', appearance.fashions.gun)
    _setupTurretRotations(appearance)


def _setupMarkTurrets(appearance, typeDesc, lodLink):
    appearance.markTurret = markTurret = MarkTurret()
    if not appearance.damageState.isCurrentModelDamaged:
        appearance.gunRecoil = _assembleRecoil(typeDesc, appearance, lodLink, 'G', appearance.fashions.gun2)
        markTurret.gunRecoil = _assembleRecoil(typeDesc, appearance, lodLink, 'G_02', appearance.fashions.gun)
        appearance.fashions.gun.inclinationMatrix = markTurret.gunMatrix
    _setupTurretRotations(appearance)
    _setupMarkTurretRotations(appearance)


def _createEffects(vehicle, appearance):
    if not vehicle.isAlive():
        return
    elif gEffectsDisabled():
        appearance.customEffectManager = None
        return
    else:
        if vehicle.physicsMode == VEHICLE_PHYSICS_MODE.DETAILED:
            appearance.customEffectManager = CustomEffectManager(vehicle, appearance.detailedEngineState)
        else:
            appearance.exhaustEffects = VehicleExhaustEffects(vehicle.typeDescriptor)
            appearance.trailEffects = VehicleTrailEffects(vehicle)
        return


def _assembleRecoil(typeDesc, appearance, lodLink, nodeName, gunFashion):
    gunAnimatorNode = appearance.compoundModel.node(nodeName)
    localGunMatrix = gunAnimatorNode.localMatrix
    gunRecoil = model_assembler.createGunAnimator(typeDesc, localGunMatrix, lodLink)
    gunRecoilMProv = gunRecoil
    appearance.compoundModel.node(nodeName, gunRecoilMProv)
    gunFashion.inclinationMatrix = appearance.gunMatrix
    gunFashion.gunLocalMatrix = gunRecoilMProv
    return gunRecoil


def _assembleSwinging(typeDesc, vehicle, lodLink):
    appearance = vehicle.appearance
    compoundModel = appearance.compoundModel
    appearance.swingingAnimator = swingingAnimator = model_assembler.createSwingingAnimator(typeDesc, compoundModel.node(TankPartNames.HULL).localMatrix, vehicle.matrix, lodLink)
    compoundModel.node(TankPartNames.HULL, swingingAnimator)
    appearance.fashions.chassis.setupSwinging(swingingAnimator, 'V')
    if hasattr(vehicle.filter, 'placingCompensationMatrix'):
        swingingAnimator.placingCompensationMatrix = vehicle.filter.placingCompensationMatrix


def _setupTurretRotations(appearance):
    compoundModel = appearance.compoundModel
    compoundModel.node(TankPartNames.TURRET, appearance.turretMatrix)
    if not appearance.damageState.isCurrentModelDamaged:
        compoundModel.node(TankNodeNames.GUN_INCLINATION, appearance.gunMatrix)
    else:
        compoundModel.node(TankPartNames.GUN, appearance.gunMatrix)


def _setupMarkTurretRotations(appearance):
    compoundModel = appearance.compoundModel
    markTurret = appearance.markTurret
    compoundModel.node(TankPartNames.TURRET + model_assembler.MARK_NODES_POSTFIX, markTurret.turretMatrix)
    if not appearance.damageState.isCurrentModelDamaged:
        compoundModel.node(TankNodeNames.GUN_INCLINATION + model_assembler.MARK_NODES_POSTFIX, markTurret.gunMatrix)
    else:
        compoundModel.node(TankPartNames.GUN + model_assembler.MARK_NODES_POSTFIX, markTurret.gunMatrix)
