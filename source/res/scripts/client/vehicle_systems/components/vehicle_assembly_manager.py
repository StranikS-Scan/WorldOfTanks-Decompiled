# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/vehicle_assembly_manager.py
from collections import namedtuple
import typing
import logging
import CGF
import GenericComponents
import GpuDecals
import Vehicular
import DataLinks
import math_utils
import Compound
from cgf_components.client_worlds_helpers import ClientWorld, clientWorldsManager, getClientWorld
from cgf_script.managers_registrator import autoregister, onAddedQuery
from constants import IS_UE_EDITOR
from vehicle_systems import vehicle_composition as veh_comp
from vehicle_systems.components import vehicle_variable_storage, gun_info
from vehicle_systems.tankStructure import TankPartNames, TankRenderMode, ModelStates
if typing.TYPE_CHECKING:
    from common_tank_appearance import CommonTankAppearance
    from gui.hangar_vehicle_appearance import HangarVehicleAppearance
_logger = logging.getLogger(__name__)

class Assembler(object):

    def checkSlotMarker(self, slotMarker):
        raise NotImplementedError()

    def assemble(self, gameObject, slotMarker):
        raise NotImplementedError()

    @staticmethod
    def _replaceWithNodeDriver(go, appearance):
        followerComponent = go.findComponentByType(Compound.LocalTransformNodeFollower)
        if followerComponent is not None:
            node = appearance.compoundModel.nodeByHandle(followerComponent.nodeHandle)
            if node is None:
                return
            go.removeComponentByType(GenericComponents.TransformComponent)
            go.createComponent(GenericComponents.TransformComponent, node.localMatrix)
            go.removeComponentByType(Compound.NodeLeaderComponent)
            go.createComponent(Compound.NodeLeaderComponent, node.name)
            go.removeComponentByType(Compound.LocalTransformNodeFollower)
        return


class TurretGunRotationAssembler(Assembler):
    _SLOTS = (veh_comp.VehicleSlots.TURRET.value,
     veh_comp.VehicleSlots.GUN.value,
     veh_comp.VehicleSlots.GUN_INCLINATION.value,
     veh_comp.VehicleSlots.TURRET_COLLISION.value,
     veh_comp.VehicleSlots.GUN_COLLISION.value)

    def checkSlotMarker(self, slotMarker):
        return slotMarker.slotName in self._SLOTS

    def assemble(self, gameObject, slotMarker):
        appearance = veh_comp.findParentVehicleAppearance(gameObject)
        if appearance is not None:
            matrixProvider = self.__getMatrixProvider(slotMarker.slotName, appearance)
            if matrixProvider is not None:
                self._replaceWithNodeDriver(gameObject, appearance)
                gameObject.removeComponentByType(GenericComponents.MatrixProviderFollowerComponent)
                gameObject.createComponent(GenericComponents.MatrixProviderFollowerComponent, matrixProvider)
        return

    def __getMatrixProvider(self, slotName, appearance):
        if slotName == veh_comp.VehicleSlots.TURRET.value:
            return appearance.turretMatrix
        else:
            if IS_UE_EDITOR:
                hasGunInclination = appearance.renderMode in (TankRenderMode.NORMAL, TankRenderMode.OVERLAY_COLLISION)
            else:
                hasGunInclination = not appearance.damageState.isCurrentModelDamaged
            if hasGunInclination and slotName == veh_comp.VehicleSlots.GUN_INCLINATION.value:
                return appearance.gunMatrix
            if not hasGunInclination and slotName == veh_comp.VehicleSlots.GUN.value:
                return appearance.gunMatrix
            if appearance.renderMode == TankRenderMode.OVERLAY_COLLISION:
                if slotName == veh_comp.VehicleSlots.TURRET_COLLISION.value:
                    return appearance.turretMatrix
                if slotName == veh_comp.VehicleSlots.GUN_COLLISION.value:
                    return appearance.gunMatrix
            return None


class RecoilAssembler(Assembler):
    _SLOTS = (veh_comp.VehicleSlots.GUN_RECOIL.value,)

    def checkSlotMarker(self, slotMarker):
        return slotMarker.slotName in self._SLOTS

    def assemble(self, gameObject, _):
        appearance = veh_comp.findParentVehicleAppearance(gameObject)
        if appearance is None:
            return
        else:
            if self._createComponent(gameObject, appearance) is not None:
                appearance.setGunRecoil(gameObject)
            return

    def _createComponent(self, gameObject, appearance):
        recoil = appearance.typeDescriptor.gun.recoil
        if recoil is None:
            return
        else:
            self._replaceWithNodeDriver(gameObject, appearance)
            gameObject.removeComponentByType(Vehicular.GunRecoilComponent)
            return gameObject.createComponent(Vehicular.GunRecoilComponent, recoil.backoffTime, recoil.returnTime, recoil.amplitude, False)


class MultiGunRecoilAssembler(RecoilAssembler):
    _SLOTS = (veh_comp.VehicleSlots.GUN_RECOIL_L.value, veh_comp.VehicleSlots.GUN_RECOIL_R.value)

    def checkSlotMarker(self, slotMarker):
        return slotMarker.slotName in self._SLOTS

    def assemble(self, gameObject, slotMarker):
        appearance = veh_comp.findParentVehicleAppearance(gameObject)
        if appearance is None or appearance.damageState.isCurrentModelDamaged:
            return
        else:
            gunIndex = -1
            for i, gunInstance in enumerate(appearance.typeDescriptor.gun.multiGun or ()):
                if gunInstance.node == slotMarker.slotName:
                    gunIndex = i
                    break

            if gunIndex >= 0 and self._createComponent(gameObject, appearance) is not None:
                appearance.gunAnimators.set(gunIndex, gameObject)
            return


class SwingingAnimationManager(Assembler):

    def checkSlotMarker(self, slotMarker):
        return slotMarker.slotName == veh_comp.VehicleSlots.HULL.value

    def assemble(self, gameObject, slotMarker):
        appearance = veh_comp.findParentVehicleAppearance(gameObject)
        if appearance is not None:
            self.__assembleSwinging(gameObject, appearance)
        return

    def __assembleSwinging(self, gameObject, appearance):
        hullNode = appearance.compoundModel.node(TankPartNames.HULL)
        if hullNode is None:
            _logger.error('Could not create SwingingAnimator: failed to find hull node')
            return
        else:
            lodLink = DataLinks.createFloatLink(appearance.lodCalculator, 'lodDistance')
            self._replaceWithNodeDriver(gameObject, appearance)
            swingingAnimator = self.__createSwingingAnimator(gameObject, appearance.typeDescriptor, hullNode.localMatrix, appearance.compoundModel.matrix, lodLink)
            if hasattr(appearance.filter, 'placingCompensationMatrix'):
                swingingAnimator.placingCompensationMatrix = appearance.filter.placingCompensationMatrix
                swingingAnimator.worldMatrix = appearance.compoundModel.matrix
            appearance.setSwingingAnimator(gameObject)
            if appearance.burnoutProcessor is not None:
                appearance.burnoutProcessor.setSwingingAnimator(gameObject)
            return swingingAnimator

    def __createSwingingAnimator(self, gameObject, vehicleDesc, basisMatrix, worldMProv=None, lodLink=None):
        gameObject.removeComponentByType(Vehicular.SwingingAnimator)
        swingingAnimator = gameObject.createComponent(Vehicular.SwingingAnimator)
        transformComponent = gameObject.findComponentByType(GenericComponents.TransformComponent)
        if transformComponent is not None:
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
        swingingAnimator.worldMatrix = worldMProv if worldMProv is not None else math_utils.createIdentityMatrix()
        swingingAnimator.lodLink = lodLink
        return swingingAnimator


class DecalsAssembler(Assembler):
    _SLOTS = (veh_comp.VehicleSlots.CHASSIS.value,
     veh_comp.VehicleSlots.HULL.value,
     veh_comp.VehicleSlots.TURRET.value,
     veh_comp.VehicleSlots.GUN.value)

    def checkSlotMarker(self, slotMarker):
        return slotMarker.slotName in self._SLOTS

    def assemble(self, gameObject, slotMarker):
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
            gameObject.removeComponentByType(GenericComponents.FashionComponent)
            gameObject.createComponent(GenericComponents.FashionComponent, fashion, partIdx)
            gameObject.removeComponentByType(GpuDecals.GpuDecalsReceiverComponent)
            gameObject.createComponent(GpuDecals.GpuDecalsReceiverComponent)
        return


class GunInfoAssembler(Assembler):
    _SLOTS = (veh_comp.VehicleSlots.GUN.value,)

    def checkSlotMarker(self, slotMarker):
        return slotMarker.slotName in self._SLOTS

    def assemble(self, gameObject, slotMarker):
        appearance = veh_comp.findParentVehicleAppearance(gameObject)
        if appearance is not None:
            if appearance.compoundModel.node(TankPartNames.GUN) is None:
                return
            typeDescr = appearance.typeDescriptor
            if typeDescr is None:
                _logger.error('typeDescriptor of appearance is None')
                return
            if not typeDescr.gun.prefabBased:
                vehicle_variable_storage.createForGun(appearance, gameObject)
                gun_info.createGunInfo(gameObject, typeDescr.turret, typeDescr.gun)
        return


_AssemblerData = namedtuple('_AssemblerData', ('worldFlags', 'assembler'))

@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor)
class VehicleAssemblyManager(CGF.ComponentManager):
    _assemblers = (_AssemblerData(ClientWorld.BATTLE | ClientWorld.EDITOR, TurretGunRotationAssembler),
     _AssemblerData(ClientWorld.BATTLE | ClientWorld.EDITOR, RecoilAssembler),
     _AssemblerData(ClientWorld.BATTLE | ClientWorld.EDITOR, MultiGunRecoilAssembler),
     _AssemblerData(ClientWorld.BATTLE | ClientWorld.EDITOR, SwingingAnimationManager),
     _AssemblerData(ClientWorld.BATTLE | ClientWorld.HANGAR | ClientWorld.EDITOR, DecalsAssembler),
     _AssemblerData(ClientWorld.BATTLE | ClientWorld.EDITOR, GunInfoAssembler))

    def __init__(self):
        super(VehicleAssemblyManager, self).__init__()
        clientWorld = getClientWorld()
        if clientWorld != ClientWorld.NONE:
            self.__assemblers = [ assemblerData.assembler() for assemblerData in VehicleAssemblyManager._assemblers if assemblerData.worldFlags & clientWorld ]
        else:
            _logger.warning("Can't recognize client world")
            self.__assemblers = []

    @onAddedQuery(CGF.GameObject, GenericComponents.SlotMarkerComponent)
    def onAddedSlotMarker(self, gameObject, slotMarker):
        for assembler in self.__assemblers:
            if assembler.checkSlotMarker(slotMarker):
                assembler.assemble(gameObject, slotMarker)


@clientWorldsManager(ClientWorld.HANGAR | ClientWorld.EDITOR)
class HangarVehicleStateSwitcherManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, GenericComponents.StateSwitcherComponent)
    def onAddedVehicleStateSwitcher(self, go, switcher):
        appearance = veh_comp.findParentVehicleAppearance(go)
        if not appearance:
            return
        if IS_UE_EDITOR:
            state = appearance.damageState.modelState
        else:
            state = appearance.vehicleState
        if state == ModelStates.UNDAMAGED:
            switcher.requestState(GenericComponents.StateSwitcherComponent.NORMAL_STATE)
        elif state in (ModelStates.DESTROYED, ModelStates.EXPLODED):
            switcher.requestState(GenericComponents.StateSwitcherComponent.DAMAGED_STATE)
