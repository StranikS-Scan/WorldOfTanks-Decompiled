# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/vehicle_assembler.py
from vehicle_systems import model_assembler
from vehicle_systems.CompoundAppearance import CompoundAppearance
from vehicle_systems.components.peripherals_controller import PeripheralsController
from vehicle_systems.components.world_connectors import GunRotatorConnector
from vehicle_systems.model_assembler import prepareCompoundAssembler, createEffects, createSwingingAnimator
from vehicle_systems.components.vehicle_audition_wwise import TrackCrashAuditionWWISE
from vehicle_systems.components.tutorial_mat_kinds_controller import TutorialMatKindsController
import BigWorld
from vehicle_systems.components.highlighter import Highlighter
from vehicle_systems.components.vehicle_shadow_manager import VehicleShadowManager
from helpers import gEffectsDisabled
import Vehicular
import DataLinks
from vehicle_systems.tankStructure import TankPartNames, TankNodeNames, TankPartIndexes
TANK_FRICTION_EVENT = 'collision_tank_friction_pc'
VEHICLE_PRIORITY_GROUP = 1

def createAssembler():
    return PanzerAssemblerWWISE()


class VehicleAssemblerAbstract(object):
    appearance = property()

    def __init__(self):
        pass

    def prerequisites(self, typeDescriptor, vID, health=1, isCrewActive=True, isTurretDetached=False):
        return None

    def constructAppearance(self, isPlayer, resourceRefs):
        return None


class _CompoundAssembler(VehicleAssemblerAbstract):
    appearance = property(lambda self: self.__appearance)

    def __init__(self):
        VehicleAssemblerAbstract.__init__(self)
        self.__appearance = CompoundAppearance()

    def prerequisites(self, typeDescriptor, vID, health=1, isCrewActive=True, isTurretDetached=False, outfitCD=''):
        prereqs = self.__appearance.prerequisites(typeDescriptor, vID, health, isCrewActive, isTurretDetached, outfitCD)
        modelsSetParams = self.__appearance.modelsSetParams
        compoundAssembler = prepareCompoundAssembler(typeDescriptor, modelsSetParams, BigWorld.player().spaceID, isTurretDetached)
        if not isTurretDetached:
            bspModels = ((TankPartNames.getIdx(TankPartNames.CHASSIS), typeDescriptor.chassis.hitTester.bspModelName),
             (TankPartNames.getIdx(TankPartNames.HULL), typeDescriptor.hull.hitTester.bspModelName),
             (TankPartNames.getIdx(TankPartNames.TURRET), typeDescriptor.turret.hitTester.bspModelName),
             (TankPartNames.getIdx(TankPartNames.GUN), typeDescriptor.gun.hitTester.bspModelName))
        else:
            bspModels = ((TankPartNames.getIdx(TankPartNames.CHASSIS), typeDescriptor.chassis.hitTester.bspModelName), (TankPartNames.getIdx(TankPartNames.HULL), typeDescriptor.hull.hitTester.bspModelName))
        collisionAssembler = BigWorld.CollisionAssembler(bspModels, BigWorld.player().spaceID)
        prereqs += [compoundAssembler, collisionAssembler]
        physicalTracksBuilders = typeDescriptor.chassis.physicalTracks
        for name, builder in physicalTracksBuilders.iteritems():
            prereqs.append(builder.createLoader('{0}PhysicalTrack'.format(name), modelsSetParams.skin))

        return (compoundAssembler, prereqs)

    def _assembleParts(self, vehicle, appearance, resourceRefs):
        pass

    def constructAppearance(self, isPlayer, resourceRefs):
        self._assembleParts(isPlayer, self.__appearance, resourceRefs)
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
    def __assembleNonDamagedOnly(resourceRefs, appearance, isPlayer, lodLink, lodStateLink):
        model_assembler.assembleTerrainMatKindSensor(appearance, lodStateLink)
        model_assembler.assembleRecoil(appearance, lodLink)
        model_assembler.assembleGunLinkedNodesAnimator(appearance)
        model_assembler.assembleCollisionObstaclesCollector(appearance, lodStateLink)
        model_assembler.assembleTessellationCollisionSensor(appearance, lodStateLink)
        model_assembler.assembleSuspensionIfNeed(appearance, lodStateLink)
        model_assembler.assembleLeveredSuspensionIfNeed(appearance, lodStateLink)
        _assembleSwinging(appearance, lodLink)
        model_assembler.assembleSuspensionSound(appearance, lodLink, isPlayer)
        model_assembler.assembleSuspensionController(appearance)
        appearance.wheelsAnimator = model_assembler.createWheelsAnimator(appearance.compoundModel, appearance.typeDescriptor, appearance.splineTracks, appearance.filter, lodStateLink)
        appearance.trackNodesAnimator = model_assembler.createTrackNodesAnimator(appearance.compoundModel, appearance.typeDescriptor, appearance.wheelsAnimator, lodStateLink)
        model_assembler.assembleVehicleTraces(appearance, appearance.filter, lodStateLink)
        model_assembler.assembleTracks(resourceRefs, appearance.typeDescriptor, appearance, appearance.splineTracks, False, lodStateLink)

    def _assembleParts(self, isPlayer, appearance, resourceRefs):
        appearance.filter = model_assembler.createVehicleFilter(appearance.typeDescriptor)
        if appearance.isAlive:
            appearance.detailedEngineState = model_assembler.assembleDetailedEngineState(appearance.compoundModel, appearance.filter, appearance.typeDescriptor, isPlayer)
            if not gEffectsDisabled():
                model_assembler.assembleVehicleAudition(isPlayer, appearance)
                model_assembler.subscribeEngineAuditionToEngineState(appearance.engineAudition, appearance.detailedEngineState)
                createEffects(appearance, isPlayer)
            if isPlayer:
                gunRotatorConnector = GunRotatorConnector(appearance)
                appearance.addComponent(gunRotatorConnector)
                appearance.frictionAudition = Vehicular.FrictionAudition(TANK_FRICTION_EVENT)
                appearance.peripheralsController = PeripheralsController()
        self.__createTrackCrashControl(appearance)
        appearance.highlighter = Highlighter()
        compoundModel = appearance.compoundModel
        isLodTopPriority = isPlayer
        lodCalcInst = Vehicular.LodCalculator(DataLinks.linkMatrixTranslation(appearance.compoundModel.matrix), True, VEHICLE_PRIORITY_GROUP, isLodTopPriority)
        appearance.lodCalculator = lodCalcInst
        lodLink = DataLinks.createFloatLink(lodCalcInst, 'lodDistance')
        lodStateLink = lodCalcInst.lodStateLink
        matrixBinding = BigWorld.player().consistentMatrices.onVehicleMatrixBindingChanged
        changeCamera = BigWorld.player().inputHandler.onCameraChanged
        appearance.shadowManager = VehicleShadowManager(compoundModel, matrixBinding, changeCamera)
        isDamaged = appearance.damageState.isCurrentModelDamaged
        if not isDamaged:
            self.__assembleNonDamagedOnly(resourceRefs, appearance, isPlayer, lodLink, lodStateLink)
            dirtEnabled = BigWorld.WG_dirtEnabled() and 'HD' in appearance.typeDescriptor.type.tags
            fashions = appearance.fashions
            if dirtEnabled and fashions is not None:
                dirtHandlers = [BigWorld.PyDirtHandler(True, compoundModel.node(TankPartNames.CHASSIS).position.y),
                 BigWorld.PyDirtHandler(False, compoundModel.node(TankPartNames.HULL).position.y),
                 BigWorld.PyDirtHandler(False, compoundModel.node(TankPartNames.TURRET).position.y),
                 BigWorld.PyDirtHandler(False, compoundModel.node(TankPartNames.GUN).position.y)]
                modelHeight, _ = appearance.computeVehicleHeight()
                appearance.dirtComponent = Vehicular.DirtComponent(dirtHandlers, modelHeight)
                for fashionIdx, _ in enumerate(TankPartNames.ALL):
                    fashions[fashionIdx].addMaterialHandler(dirtHandlers[fashionIdx])

        model_assembler.setupTurretRotations(appearance)
        appearance.waterSensor = model_assembler.assembleWaterSensor(appearance.typeDescriptor, appearance, lodStateLink)
        if appearance.engineAudition is not None:
            appearance.engineAudition.setIsUnderwaterInfo(DataLinks.createBoolLink(appearance.waterSensor, 'isUnderWater'))
            appearance.engineAudition.setIsInWaterInfo(DataLinks.createBoolLink(appearance.waterSensor, 'isInWater'))
        if isPlayer and BigWorld.player().isInTutorial:
            tutorialMatKindsController = TutorialMatKindsController()
            tutorialMatKindsController.terrainMatKindsLink = lambda : appearance.terrainMatKind
            appearance.addComponent(tutorialMatKindsController)
        self.__postSetupFilter(appearance)
        compoundModel.setPartBoundingBoxAttachNode(TankPartIndexes.GUN, TankNodeNames.GUN_INCLINATION)
        return


def _assembleSwinging(appearance, lodLink):
    compoundModel = appearance.compoundModel
    appearance.swingingAnimator = swingingAnimator = createSwingingAnimator(appearance.typeDescriptor, compoundModel.node(TankPartNames.HULL).localMatrix, appearance.compoundModel.matrix, lodLink)
    compoundModel.node(TankPartNames.HULL, swingingAnimator)
    if hasattr(appearance.filter, 'placingCompensationMatrix'):
        swingingAnimator.placingCompensationMatrix = appearance.filter.placingCompensationMatrix
