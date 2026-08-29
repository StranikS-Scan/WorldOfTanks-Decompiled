# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/vehicle_assembly_manager.py
from collections import namedtuple
import typing
import logging
import CGF
import GenericComponents
import GpuDecals
import Vehicular
import Compound
from cgf_components.client_worlds_helpers import ClientWorld, getClientWorld
from cgf_modules.variable_components import VariableStorageComponent
from constants import IS_UE_EDITOR
from vehicle_systems import vehicle_composition as veh_comp
from vehicle_systems.components import vehicle_variable_storage
from vehicle_systems.tankStructure import TankPartNames, TankRenderMode, ModelStates, TankNodeNames
if typing.TYPE_CHECKING:
    from GenericComponents import SlotMarkerComponent
    from vehicle_appearance.common_tank_appearance import CommonTankAppearance
    from gui.hangar_vehicle_appearance import HangarVehicleAppearance
    from vehicle_systems.components.vehicle_variable_storage import VariableType
    TAppearance = typing.Union[HangarVehicleAppearance, CommonTankAppearance]
_logger = logging.getLogger(__name__)

def _isAlive(appearance):
    if IS_UE_EDITOR:
        return appearance is not None
    else:
        vehicle = appearance.getVehicle() if appearance is not None else None
        return vehicle is not None and vehicle.isAlive()


class Assembler(object):
    NodeFollowerAccess = CGF.AccessReaction(CGF.Ro(Compound.LocalTransformNodeFollower))
    AccessReactions = tuple()

    def checkSlotMarker(self, slotMarker):
        raise NotImplementedError

    @typing.overload
    def assemble(self, gameObject, slotMarker, queue, *accessors):
        pass

    @typing.overload
    def assemble(self, gameObject, slotMarker, queue):
        pass

    def assemble(self, *args):
        raise NotImplementedError

    @staticmethod
    def _replaceWithNodeDriver(go, appearance, queue, nodeFollowerAccess):
        followerComponent = nodeFollowerAccess.find(go)
        if followerComponent:
            node = appearance.compoundModel.nodeByHandle(followerComponent.nodeHandle)
            if node is None:
                return
            queue.removeComponent(go, CGF.TransformComponent)
            queue.createComponent(go, CGF.TransformComponent, node.localMatrix)
            queue.removeComponent(go, Compound.NodeLeaderComponent)
            queue.createComponent(go, Compound.NodeLeaderComponent, node.name)
            queue.removeComponent(go, Compound.LocalTransformNodeFollower)
        return


class TurretGunRotationAssembler(Assembler):
    _SLOTS = (veh_comp.VehicleSlots.TURRET.value,
     veh_comp.VehicleSlots.GUN.value,
     veh_comp.VehicleSlots.GUN_INCLINATION.value,
     veh_comp.VehicleSlots.TURRET_COLLISION.value,
     veh_comp.VehicleSlots.GUN_COLLISION.value)
    AccessReactions = (Assembler.NodeFollowerAccess,)

    def checkSlotMarker(self, slotMarker):
        return slotMarker.slotName in self._SLOTS

    def assemble(self, gameObject, slotMarker, queue, nodeFollowerAccess):
        appearance = veh_comp.findParentVehicleAppearance(gameObject)
        if _isAlive(appearance):
            matrixProvider = self.__getMatrixProvider(slotMarker.slotName, appearance)
            if matrixProvider is not None:
                self._replaceWithNodeDriver(gameObject, appearance, queue, nodeFollowerAccess)
                queue.removeComponent(gameObject, GenericComponents.MatrixProviderFollowerComponent)
                queue.createComponent(gameObject, GenericComponents.MatrixProviderFollowerComponent, matrixProvider)
        elif appearance is not None and not appearance.isTurretDetached:
            appearance.compoundModel.node(TankPartNames.TURRET).localMatrix = appearance.turretMatrix
            appearance.compoundModel.node(TankPartNames.GUN).localMatrix = appearance.gunMatrix
        return

    def __getMatrixProvider(self, slotName, appearance):
        if IS_UE_EDITOR:
            if slotName == veh_comp.VehicleSlots.TURRET_COLLISION.value:
                return appearance.turretMatrix
            if slotName == veh_comp.VehicleSlots.GUN_COLLISION.value:
                return appearance.gunMatrix
        if slotName == veh_comp.VehicleSlots.TURRET.value:
            return appearance.turretMatrix
        else:
            if IS_UE_EDITOR:
                hasGunInclination = appearance.renderMode in (TankRenderMode.NORMAL, TankRenderMode.OVERLAY_COLLISION)
            else:
                hasGunInclination = not appearance.damageState.isCurrentModelDamaged
            if hasGunInclination and slotName == veh_comp.VehicleSlots.GUN_INCLINATION.value:
                return appearance.gunMatrix
            return appearance.gunMatrix if not hasGunInclination and slotName == veh_comp.VehicleSlots.GUN.value else None


class TurretJointRotationAssembler(Assembler):
    _SLOTS = TankNodeNames.TURRET_JOINT
    AccessReactions = tuple()

    def checkSlotMarker(self, slotMarker):
        return slotMarker.slotName in self._SLOTS

    def assemble(self, gameObject, slotMarker, queue):
        appearance = veh_comp.findParentVehicleAppearance(gameObject)
        if appearance is None:
            return
        else:
            matrixProvider = self.__getMatrixProvider(slotMarker.slotName, appearance)
            if matrixProvider is not None:
                queue.createComponent(gameObject, GenericComponents.MatrixProviderFollowerComponent, matrixProvider)
            return

    def __getMatrixProvider(self, slotName, appearance):
        return appearance.turretRotator.turretMatrix if slotName == TankNodeNames.TURRET_JOINT else None


class RecoilAssembler(Assembler):
    _SLOTS = (veh_comp.VehicleSlots.GUN_RECOIL.value,)
    AccessReactions = (Assembler.NodeFollowerAccess,)

    def checkSlotMarker(self, slotMarker):
        return slotMarker.slotName in self._SLOTS

    def assemble(self, gameObject, _, queue, nodeFollowerAccess):
        appearance = veh_comp.findParentVehicleAppearance(gameObject)
        if not _isAlive(appearance):
            return
        else:
            if self._createComponent(gameObject, appearance, queue, nodeFollowerAccess) is not None:
                appearance.setGunRecoil(gameObject)
            return

    def _createComponent(self, gameObject, appearance, queue, nodeFollowerAccess):
        recoil = appearance.typeDescriptor.gun.recoil
        if recoil is None:
            return
        else:
            self._replaceWithNodeDriver(gameObject, appearance, queue, nodeFollowerAccess)
            queue.removeComponent(gameObject, Vehicular.RecoilComponent)
            return queue.createComponent(gameObject, Vehicular.RecoilComponent, recoil.backoffTime, recoil.returnTime, recoil.amplitude, False)


class MultiGunRecoilAssembler(RecoilAssembler):
    _SLOTS = (veh_comp.VehicleSlots.GUN_RECOIL_L.value, veh_comp.VehicleSlots.GUN_RECOIL_R.value)

    def checkSlotMarker(self, slotMarker):
        return slotMarker.slotName in self._SLOTS

    def assemble(self, gameObject, slotMarker, queue, nodeFollowerAccess):
        appearance = veh_comp.findParentVehicleAppearance(gameObject)
        if not _isAlive(appearance):
            return
        else:
            gunIndex = -1
            for i, gunInstance in enumerate(appearance.typeDescriptor.gun.multiGun or ()):
                if gunInstance.node == slotMarker.slotName:
                    gunIndex = i
                    break

            if gunIndex >= 0 and self._createComponent(gameObject, appearance, queue, nodeFollowerAccess) is not None:
                appearance.gunAnimators.set(gunIndex, gameObject)
            return


class SwingingAnimationManager(Assembler):
    LodCalculatorAccess = CGF.AccessReaction(CGF.Ro(Vehicular.LodCalculator))
    TransformAccess = CGF.AccessReaction(CGF.Rw(CGF.TransformComponent))
    AccessReactions = (LodCalculatorAccess, TransformAccess, Assembler.NodeFollowerAccess)

    def checkSlotMarker(self, slotMarker):
        return slotMarker.slotName == veh_comp.VehicleSlots.HULL.value

    def assemble(self, gameObject, slotMarker, queue, lodCalculatorAccess, transformAccess, nodeFollowerAccess):
        appearance = veh_comp.findParentVehicleAppearance(gameObject)
        if _isAlive(appearance):
            self.__assembleSwinging(gameObject, appearance, queue, lodCalculatorAccess, transformAccess, nodeFollowerAccess)

    def __assembleSwinging(self, gameObject, appearance, queue, lodCalculatorAccess, transformAccess, nodeFollowerAccess):
        hullNode = appearance.compoundModel.node(TankPartNames.HULL)
        if hullNode is None:
            _logger.error('Could not create SwingingAnimator: failed to find hull node')
            return
        else:
            lodCalculator = lodCalculatorAccess.find(appearance.gameObject)
            if not lodCalculator:
                _logger.error('Could not create SwingingAnimator: failed to find Vehicular.LodCalculator')
                return
            lodLink = CGF.createFloatLink(lodCalculator, 'lodDistance')
            self._replaceWithNodeDriver(gameObject, appearance, queue, nodeFollowerAccess)
            swingingAnimator = self.__createSwingingAnimator(queue, gameObject, transformAccess, appearance.typeDescriptor, hullNode.localMatrix, appearance.gameObject, lodLink)
            if hasattr(appearance.filter, 'placingCompensationMatrix'):
                swingingAnimator.placingCompensationMatrix = appearance.filter.placingCompensationMatrix
                swingingAnimator.worldMatrixGo = appearance.gameObject
            appearance.setSwingingAnimator(gameObject)
            return swingingAnimator

    def __createSwingingAnimator(self, queue, gameObject, transformAccess, vehicleDesc, basisMatrix, appearanceGo, lodLink=None):
        queue.removeComponent(gameObject, Vehicular.SwingingAnimator)
        swingingAnimator = queue.createComponent(gameObject, Vehicular.SwingingAnimator)
        transformComponent = transformAccess.find(gameObject)
        if transformComponent:
            transformComponent.transform = basisMatrix
        else:
            _logger.error("Can't find TransformComponent to create SwingingAnimator")
        swingingCfg = vehicleDesc.hull.swinging
        pp = tuple((p * m for p, m in zip(swingingCfg.pitchParams, (0.9, 1.88, 0.3, 4.0, 1.0, 1.0))))
        swingingAnimator.setupPitchSwinging(*pp)
        swingingAnimator.setupRollSwinging(*swingingCfg.rollParams)
        swingingAnimator.setupShotSwinging(swingingCfg.sensitivityToImpulse)
        swingingAnimator.maxMovementSpeed = vehicleDesc.physics['speedLimits'][0]
        swingingAnimator.lodSetting = swingingCfg.lodDist
        swingingAnimator.worldMatrixGo = appearanceGo
        swingingAnimator.lodLink = lodLink
        return swingingAnimator


class DecalsAssembler(Assembler):
    _SLOTS = (veh_comp.VehicleSlots.HULL.value, veh_comp.VehicleSlots.TURRET.value, veh_comp.VehicleSlots.GUN.value)

    def checkSlotMarker(self, slotMarker):
        return slotMarker.slotName in self._SLOTS

    def assemble(self, gameObject, slotMarker, queue):
        appearance = veh_comp.findParentVehicleAppearance(gameObject)
        if appearance is not None:
            if hasattr(appearance, 'damageState') and appearance.damageState.isCurrentModelDamaged:
                return
            partIdx = TankPartNames.getIdx(slotMarker.slotName)
            if partIdx is None:
                return _logger.error('Failed to setup GPU Decals receiver for game object: %s. Unknown tanks part: %s', gameObject.name, slotMarker.slotName)
            fashion = getattr(appearance.fashions, slotMarker.slotName, None)
            if fashion is None:
                return _logger.error('Failed to setup GPU Decals receiver for game object: %s. Missing fashion for part: %s', gameObject.name, slotMarker.slotName)
            queue.removeComponent(gameObject, GenericComponents.FashionComponent)
            queue.createComponent(gameObject, GenericComponents.FashionComponent, fashion, partIdx)
            queue.removeComponent(gameObject, GpuDecals.GpuDecalsReceiverComponent)
            queue.createComponent(gameObject, GpuDecals.GpuDecalsReceiverComponent)
        return


class GunInfoAssembler(Assembler):
    _SLOTS = (veh_comp.VehicleSlots.GUN.value,)
    VariableStorageAccess = CGF.AccessReaction(CGF.Rw(VariableStorageComponent))
    AccessReactions = (VariableStorageAccess,)

    def checkSlotMarker(self, slotMarker):
        return slotMarker.slotName in self._SLOTS

    def assemble(self, gameObject, slotMarker, queue, varStorageAccess):
        appearance = veh_comp.findParentVehicleAppearance(gameObject)
        if appearance is not None:
            if appearance.compoundModel.node(TankPartNames.GUN) is None:
                return
            typeDescr = appearance.typeDescriptor
            if typeDescr is None:
                _logger.error('GunInfoAssembler: typeDescriptor of appearance is None')
                return
            if self._isStorageRequired(typeDescr):
                varStorage = varStorageAccess.find(gameObject)
                if not varStorage:
                    _logger.error("GunInfoAssembler: Can't find variable storage for: %s", gameObject.name)
                    return
                for varName, varValue in vehicle_variable_storage.getVariableValuesForGun(appearance):
                    varStorage.modify(gameObject, varName, varValue)

        return

    @staticmethod
    def update(appearance, varName, value):
        typeDescr = appearance.typeDescriptor
        if typeDescr is not None and not GunInfoAssembler._isStorageRequired(typeDescr):
            return
        else:
            gunGo = GenericComponents.findSlot(appearance.gameObject, veh_comp.VehicleSlots.GUN.value)
            if gunGo.valid:
                vehicle_variable_storage.update(gunGo, varName, value)
            return

    @staticmethod
    def _isStorageRequired(typeDescriptor):
        return not typeDescriptor.gun.prefabBased


class CompositionReadinessNotifier(Assembler):

    def checkSlotMarker(self, slotMarker):
        return slotMarker.slotName == GenericComponents.COMPOSITION_ROOT_SLOT_NAME

    def assemble(self, gameObject, slotMarker, queue):
        appearance = veh_comp.findParentVehicleAppearance(gameObject)
        if appearance is not None:
            appearance.setCompositionReady(True)
        return


_AssemblerData = namedtuple('_AssemblerData', ('worldFlags', 'assembler'))

class VehicleAssemblySystem(CGF.System):
    MarkerActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRo(GenericComponents.SlotMarkerComponent))
    _assemblers = (_AssemblerData(ClientWorld.BATTLE | ClientWorld.EDITOR, TurretGunRotationAssembler),
     _AssemblerData(ClientWorld.HANGAR, TurretJointRotationAssembler),
     _AssemblerData(ClientWorld.BATTLE | ClientWorld.EDITOR, RecoilAssembler),
     _AssemblerData(ClientWorld.BATTLE | ClientWorld.EDITOR, MultiGunRecoilAssembler),
     _AssemblerData(ClientWorld.AllWorlds, DecalsAssembler),
     _AssemblerData(ClientWorld.BATTLE | ClientWorld.EDITOR, GunInfoAssembler),
     _AssemblerData(ClientWorld.BATTLE | ClientWorld.EDITOR, SwingingAnimationManager),
     _AssemblerData(ClientWorld.AllWorlds, CompositionReadinessNotifier))
    _assemblerReactions = tuple((accessReact for assemblerData in _assemblers for accessReact in assemblerData.assembler.AccessReactions))
    Reactions = CGF.Reactions(MarkerActivated, *_assemblerReactions)

    def __init__(self):
        super(VehicleAssemblySystem, self).__init__()
        clientWorld = getClientWorld()
        if clientWorld != ClientWorld.NONE:
            self.__assemblers = [ assemblerData.assembler() for assemblerData in VehicleAssemblySystem._assemblers if assemblerData.worldFlags & clientWorld ]
        else:
            _logger.warning("Can't recognize client world")
            self.__assemblers = []

    def update(self):
        queue = CGF.CommandQueue(self.gom)
        for go, slot in self.reaction(self.MarkerActivated):
            for assembler in self.__assemblers:
                if assembler.checkSlotMarker(slot):
                    accessors = tuple((self.reaction(r) for r in assembler.AccessReactions))
                    assembler.assemble(go, slot, queue, *accessors)


class HangarVehicleStateSwitcherSystem(CGF.System):
    SwitcherActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRo(GenericComponents.StateSwitcherComponent))
    Reactions = CGF.Reactions(SwitcherActivated)

    def update(self):
        for go, switcher in self.reaction(self.SwitcherActivated):
            appearance = veh_comp.findParentVehicleAppearance(go)
            if not appearance:
                return
            if IS_UE_EDITOR:
                state = appearance.damageState.modelState
            else:
                state = appearance.vehicleState
            if state == ModelStates.UNDAMAGED:
                switcher.requestState(GenericComponents.StateSwitcherComponent.NORMAL_STATE)
            if state in (ModelStates.DESTROYED, ModelStates.EXPLODED):
                switcher.requestState(GenericComponents.StateSwitcherComponent.DAMAGED_STATE)
