# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/vehicle_assembler.py
import functools
import weakref
from vehicle_systems import model_assembler
from vehicle_systems.CompoundAppearance import CompoundAppearance
from vehicle_systems.components.peripherals_controller import PeripheralsController
from vehicle_systems.components.world_connectors import GunRotatorConnector
from vehicle_systems.model_assembler import prepareCompoundAssembler, createEffects, createSwingingAnimator
from vehicle_systems.components.vehicle_audition_wwise import TrackCrashAuditionWWISE
from vehicle_systems.components.tutorial_mat_kinds_controller import TutorialMatKindsController
import BigWorld
from vehicle_systems.components.highlighter import Highlighter
from helpers import gEffectsDisabled
import Vehicular
import DataLinks
from vehicle_systems.tankStructure import TankPartNames
TANK_FRICTION_EVENT = 'collision_tank_friction_pc'
VEHICLE_PRIORITY_GROUP = 1

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

    def prerequisites(self, typeDescriptor, id, health=1, isCrewActive=True, isTurretDetached=False, outfitCD=''):
        assert 'pillbox' not in typeDescriptor.type.tags, 'Pillboxes are not supported and have never been'
        prereqs = self.__appearance.prerequisites(typeDescriptor, id, health, isCrewActive, isTurretDetached, outfitCD)
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
    def __isFlying(appearance):
        return appearance.isFlying

    @staticmethod
    def __createTrackCrashControl(appearance):
        if appearance.isAlive and appearance.customEffectManager is not None:
            trackCenterNodes = tuple((appearance.customEffectManager.getTrackCenterNode(x) for x in xrange(2)))
            appearance.trackCrashAudition = TrackCrashAuditionWWISE(trackCenterNodes)
        return

    @staticmethod
    def __postSetupFilter(appearance):
        suspensionWorking = appearance.suspension is not None and appearance.suspension.hasGroundNodes
        placingOnGround = not (suspensionWorking or appearance.leveredSuspension is not None)
        appearance.filter.placingOnGround = placingOnGround
        return

    @staticmethod
    def __assembleNonDamagedOnly(appearance, isPlayer, lodLink, lodStateLink):
        model_assembler.assembleTerrainMatKindSensor(appearance, lodStateLink)
        model_assembler.assembleRecoil(appearance, lodLink)
        model_assembler.assembleGunLinkedNodesAnimator(appearance)
        model_assembler.assembleSuspensionIfNeed(appearance, lodStateLink)
        model_assembler.assembleLeveredSuspensionIfNeed(appearance, lodStateLink)
        _assembleSwinging(appearance, lodLink)
        model_assembler.assembleSuspensionSound(appearance, lodLink, isPlayer)
        model_assembler.assembleSuspensionController(appearance)
        appearance.wheelsAnimator = model_assembler.createWheelsAnimator(appearance.compoundModel, appearance.typeDescriptor, appearance.splineTracks, appearance.filter, lodStateLink)
        appearance.trackNodesAnimator = model_assembler.createTrackNodesAnimator(appearance.compoundModel, appearance.typeDescriptor, appearance.wheelsAnimator, lodStateLink)
        model_assembler.assembleVehicleTraces(appearance, appearance.filter, lodStateLink)

    def _assembleParts(self, isPlayer, appearance):
        appearance.filter = model_assembler.createVehicleFilter(appearance.typeDescriptor)
        if appearance.isAlive:
            appearance.detailedEngineState = model_assembler.assembleDetailedEngineState(appearance.compoundModel, appearance.filter, appearance.typeDescriptor, isPlayer)
            if not gEffectsDisabled():
                model_assembler.assembleVehicleAudition(isPlayer, appearance)
                model_assembler.subscribeEngineAuditionToEngineState(appearance.engineAudition, appearance.detailedEngineState)
                createEffects(appearance)
            if isPlayer:
                gunRotatorConnector = GunRotatorConnector(appearance)
                appearance.addComponent(gunRotatorConnector)
                appearance.frictionAudition = Vehicular.FrictionAudition(TANK_FRICTION_EVENT)
                appearance.peripheralsController = PeripheralsController()
        self.__createTrackCrashControl(appearance)
        appearance.highlighter = Highlighter()
        isLodTopPriority = isPlayer
        lodCalcInst = Vehicular.LodCalculator(DataLinks.linkMatrixTranslation(appearance.compoundModel.matrix), True, VEHICLE_PRIORITY_GROUP, isLodTopPriority)
        appearance.lodCalculator = lodCalcInst
        lodLink = DataLinks.createFloatLink(lodCalcInst, 'lodDistance')
        lodStateLink = lodCalcInst.lodStateLink
        isDamaged = appearance.damageState.isCurrentModelDamaged
        if not isDamaged:
            self.__assembleNonDamagedOnly(appearance, isPlayer, lodLink, lodStateLink)
        model_assembler.setupTurretRotations(appearance)
        if appearance.fashion is not None:
            appearance.fashion.movementInfo = appearance.filter.movementInfo
        appearance.waterSensor = model_assembler.assembleWaterSensor(appearance.typeDescriptor, appearance, lodStateLink)
        if appearance.engineAudition is not None:
            appearance.engineAudition.setIsUnderwaterInfo(DataLinks.createBoolLink(appearance.waterSensor, 'isUnderWater'))
            appearance.engineAudition.setIsInWaterInfo(DataLinks.createBoolLink(appearance.waterSensor, 'isInWater'))
        if isPlayer and BigWorld.player().isInTutorial:
            tutorialMatKindsController = TutorialMatKindsController()
            tutorialMatKindsController.terrainMatKindsLink = lambda : appearance.terrainMatKind
            appearance.addComponent(tutorialMatKindsController)
        self.__postSetupFilter(appearance)
        return


def _assembleSwinging(appearance, lodLink):
    compoundModel = appearance.compoundModel
    appearance.swingingAnimator = swingingAnimator = createSwingingAnimator(appearance.typeDescriptor, compoundModel.node(TankPartNames.HULL).localMatrix, appearance.compoundModel.matrix, lodLink)
    compoundModel.node(TankPartNames.HULL, swingingAnimator)
    if hasattr(appearance.filter, 'placingCompensationMatrix'):
        swingingAnimator.placingCompensationMatrix = appearance.filter.placingCompensationMatrix
