# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/vehicle_assembler.py
from CustomEffectManager import CustomEffectManager
from vehicle_systems import model_assembler
from vehicle_systems.CompoundAppearance import CompoundAppearance
from vehicle_systems.components.world_connectors import GunRotatorConnector
from vehicle_systems.model_assembler import prepareCompoundAssembler
from vehicle_systems.tankStructure import getPartModelsFromDesc
import functools
from vehicle_systems.components.vehicle_audition_wwise import EngineAuditionWWISE, TrackCrashAuditionWWISE
import weakref
import BigWorld
import WoT
from vehicle_systems.components.engine_state import DetailedEngineStateWWISE
from vehicle_systems.components.highlighter import Highlighter
from helpers import gEffectsDisabled
import Vehicular
import DataLinks
from vehicle_systems.tankStructure import TankNodeNames, TankPartNames

def createAssembler():
    return PanzerAssemblerWWISE()


class VehicleAssemblerAbstract(object):
    appearance = property()

    def __init__(self):
        pass

    def prerequisites(self, typeDescriptor, id, health=1, isCrewActive=True, isTurretDetached=False):
        return None

    def constructAppearance(self, isPlayer):
        return None


class _CompoundAssembler(VehicleAssemblerAbstract):
    appearance = property(lambda self: self.__appearance)

    def __init__(self):
        VehicleAssemblerAbstract.__init__(self)
        self.__appearance = CompoundAppearance()

    def prerequisites(self, typeDescriptor, id, health=1, isCrewActive=True, isTurretDetached=False):
        prereqs = self.__appearance.prerequisites(typeDescriptor, id, health, isCrewActive, isTurretDetached)
        compoundAssembler = prepareCompoundAssembler(typeDescriptor, self.__appearance.damageState.modelState, BigWorld.player().spaceID, isTurretDetached)
        prereqs += [compoundAssembler]
        return (compoundAssembler, prereqs)

    def _assembleParts(self, vehicle, appearance):
        pass

    def constructAppearance(self, isPlayer):
        self._assembleParts(isPlayer, self.__appearance)
        return self.__appearance


class PanzerAssemblerWWISE(_CompoundAssembler):

    @staticmethod
    def __assembleEngineState(isPlayerVehicle):
        detailedEngineState = DetailedEngineStateWWISE()
        if isPlayerVehicle:
            detailedEngineState.physicRPMLink = lambda : WoT.unpackAuxVehiclePhysicsData(BigWorld.player().ownVehicleAuxPhysicsData)[5]
            detailedEngineState.physicGearLink = lambda : BigWorld.player().ownVehicleGear
        else:
            detailedEngineState.physicRPMLink = lambda : 0.0
            detailedEngineState.physicGearLink = lambda : 0
        return detailedEngineState

    @staticmethod
    def __assembleEngineAudition(isPlayer, appearance):
        appearance = weakref.proxy(appearance)
        engineAudition = EngineAuditionWWISE(isPlayer, appearance.typeDescriptor, appearance.id)
        e = engineAudition
        e.isUnderwaterLink = lambda : appearance.isUnderwater
        e.isInWaterLink = lambda : appearance.isInWater
        e.isFlyingLink = functools.partial(PanzerAssemblerWWISE.__isFlying, appearance)
        e.curTerrainMatKindLink = lambda : appearance.terrainMatKind
        e.leftTrackScrollLink = lambda : appearance.leftTrackScroll
        e.leftTrackScrollRelativeLink = lambda : appearance.customEffectManager.getParameter('deltaL')
        e.rightTrackScrollLink = lambda : appearance.rightTrackScroll
        e.rightTrackScrollRelativeLink = lambda : appearance.customEffectManager.getParameter('deltaR')
        e.detailedEngineState = appearance.detailedEngineState
        return e

    @staticmethod
    def __isFlying(appearance):
        filter = appearance.filter
        if filter.placingOnGround:
            contactsWithGround = filter.numLeftTrackContacts + filter.numRightTrackContacts
            return contactsWithGround == 0
        else:
            return appearance.fashion.isFlying

    @staticmethod
    def __createTrackCrashControl(appearance):
        if appearance.isAlive and appearance.customEffectManager is not None:
            trackCenterNodes = tuple((appearance.customEffectManager.getTrackCenterNode(x) for x in xrange(2)))
            appearance.trackCrashAudition = TrackCrashAuditionWWISE(trackCenterNodes)
        return

    def _assembleParts(self, isPlayer, appearance):
        if appearance.isAlive:
            appearance.detailedEngineState = self.__assembleEngineState(isPlayer)
            if not appearance.isPillbox and not gEffectsDisabled():
                appearance.engineAudition = self.__assembleEngineAudition(isPlayer, appearance)
                appearance.detailedEngineState.onEngineStart += appearance.engineAudition.onEngineStart
                appearance.detailedEngineState.onStateChanged += appearance.engineAudition.onStateChanged
                _createEffects(appearance)
            if isPlayer:
                gunRotatorConnector = GunRotatorConnector(appearance)
                appearance.addComponent(gunRotatorConnector)
        self.__createTrackCrashControl(appearance)
        appearance.highlighter = Highlighter()
        lodCalcInst = Vehicular.LodCalculator(DataLinks.linkMatrixTranslation(appearance.compoundModel.matrix), True)
        appearance.lodCalculator = lodCalcInst
        lodLink = DataLinks.createFloatLink(lodCalcInst, 'lodDistance')
        if not appearance.damageState.isCurrentModelDamaged:
            _assembleRecoil(appearance, lodLink)
            _assembleSwinging(appearance, lodLink)
        _setupTurretRotations(appearance)


def _createEffects(appearance):
    if gEffectsDisabled():
        appearance.customEffectManager = None
        return
    else:
        appearance.customEffectManager = CustomEffectManager(appearance)
        return


def _assembleRecoil(appearance, lodLink):
    gunAnimatorNode = appearance.compoundModel.node(TankNodeNames.GUN_RECOIL)
    localGunMatrix = gunAnimatorNode.localMatrix
    appearance.gunRecoil = gunRecoil = model_assembler.createGunAnimator(appearance.typeDescriptor, localGunMatrix, lodLink)
    gunRecoilMProv = gunRecoil.animatedMProv
    appearance.compoundModel.node(TankNodeNames.GUN_RECOIL, gunRecoilMProv)
    appearance.fashions.gun.inclinationMatrix = appearance.gunMatrix
    appearance.fashions.gun.gunLocalMatrix = gunRecoilMProv


def _assembleSwinging(appearance, lodLink):
    compoundModel = appearance.compoundModel
    appearance.swingingAnimator = swingingAnimator = model_assembler.createSwingingAnimator(appearance.typeDescriptor, compoundModel.node(TankPartNames.HULL).localMatrix, appearance.compoundModel.matrix, lodLink)
    compoundModel.node(TankPartNames.HULL, swingingAnimator)
    appearance.fashions.chassis.setupSwinging(swingingAnimator, 'V')
    if hasattr(appearance.filter, 'placingCompensationMatrix'):
        swingingAnimator.placingCompensationMatrix = appearance.filter.placingCompensationMatrix


def _setupTurretRotations(appearance):
    compoundModel = appearance.compoundModel
    compoundModel.node(TankPartNames.TURRET, appearance.turretMatrix)
    if not appearance.damageState.isCurrentModelDamaged:
        compoundModel.node(TankNodeNames.GUN_INCLINATION, appearance.gunMatrix)
    else:
        compoundModel.node(TankPartNames.GUN, appearance.gunMatrix)
