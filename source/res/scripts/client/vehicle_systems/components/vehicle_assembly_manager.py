# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/vehicle_assembly_manager.py
from collections import namedtuple
import typing
import logging
import enum
import CGF
import GenericComponents
import Vehicular
import DataLinks
import math_utils
import Compound
import BattleReplay
from cgf_script.managers_registrator import autoregister, onAddedQuery
from constants import IS_UE_EDITOR
from helpers import isPlayerAccount, isPlayerAvatar
from vehicle_systems import vehicle_composition as veh_comp
from vehicle_systems.tankStructure import TankPartNames, TankRenderMode
if typing.TYPE_CHECKING:
    from common_tank_appearance import CommonTankAppearance
    from gui.hangar_vehicle_appearance import HangarVehicleAppearance
_logger = logging.getLogger(__name__)

class AssemblyType(enum.IntEnum):
    NONE = 0
    BATTLE = 1
    HANGAR = 2
    EDITOR = 4


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
            go.createComponent(Compound.NodeLeaderComponent, node.name)
            go.removeComponent(followerComponent)
        else:
            _logger.error("Can't find LocalTransformNodeFollower for game object: %s", go.name)
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
        if gameObject.findComponentByType(GenericComponents.MatrixProviderFollowerComponent):
            return
        else:
            appearance = veh_comp.findParentVehicleAppearance(gameObject)
            if appearance is not None:
                matrixProvider = self.__getMatrixProvider(slotMarker.slotName, appearance)
                if matrixProvider is not None:
                    self._replaceWithNodeDriver(gameObject, appearance)
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
        if gameObject.findComponentByType(Vehicular.GunRecoilComponent):
            return
        else:
            appearance = veh_comp.findParentVehicleAppearance(gameObject)
            if appearance is not None:
                if self._createComponent(gameObject, appearance) is not None:
                    appearance.setGunRecoil(gameObject)
            return

    def _createComponent(self, gameObject, appearance):
        vehicleDesc = appearance.typeDescriptor
        recoilDescr = vehicleDesc.gun.recoil
        if recoilDescr is None:
            return
        else:
            self._replaceWithNodeDriver(gameObject, appearance)
            return gameObject.createComponent(Vehicular.GunRecoilComponent, recoilDescr.backoffTime, recoilDescr.returnTime, recoilDescr.amplitude, False)


class MultiGunRecoilAssembler(RecoilAssembler):
    _SLOTS = (veh_comp.VehicleSlots.GUN_RECOIL_L.value, veh_comp.VehicleSlots.GUN_RECOIL_R.value)

    def checkSlotMarker(self, slotMarker):
        return slotMarker.slotName in self._SLOTS

    def assemble(self, gameObject, slotMarker):
        appearance = veh_comp.findParentVehicleAppearance(gameObject)
        if appearance is not None and not appearance.damageState.isCurrentModelDamaged:
            if self._createComponent(gameObject, appearance) is not None:
                multiGun = appearance.typeDescriptor.turret.multiGun
                gunIndex = 0
                for i, gunInstance in enumerate(multiGun):
                    if gunInstance.node == slotMarker.slotName:
                        gunIndex = i
                        break

                appearance.gunAnimators.set(gunIndex, gameObject)
        return


class SwingingAnimationManager(Assembler):

    def checkSlotMarker(self, slotMarker):
        return slotMarker.slotName == veh_comp.VehicleSlots.HULL.value

    def assemble(self, gameObject, slotMarker):
        if gameObject.findComponentByType(Vehicular.SwingingAnimator):
            return
        else:
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


_AssemblerData = namedtuple('_AssemblerData', ('typeFlags', 'assembler'))

@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor)
class VehicleAssemblyManager(CGF.ComponentManager):
    _assemblers = (_AssemblerData(AssemblyType.BATTLE | AssemblyType.EDITOR, TurretGunRotationAssembler),
     _AssemblerData(AssemblyType.BATTLE | AssemblyType.EDITOR, RecoilAssembler),
     _AssemblerData(AssemblyType.BATTLE | AssemblyType.EDITOR, MultiGunRecoilAssembler),
     _AssemblerData(AssemblyType.BATTLE | AssemblyType.EDITOR, SwingingAnimationManager))

    def __init__(self):
        super(VehicleAssemblyManager, self).__init__()
        if IS_UE_EDITOR:
            assemblyType = AssemblyType.EDITOR
        elif isPlayerAccount():
            assemblyType = AssemblyType.HANGAR
        elif isPlayerAvatar() or BattleReplay.isServerSideReplay():
            assemblyType = AssemblyType.BATTLE
        else:
            assemblyType = AssemblyType.NONE
            _logger.warning("Can't recognize assembly type")
        if assemblyType != AssemblyType.NONE:
            self.__assemblers = [ assemblerData.assembler() for assemblerData in VehicleAssemblyManager._assemblers if assemblerData.typeFlags & assemblyType ]
        else:
            self.__assemblers = []

    @onAddedQuery(CGF.GameObject, GenericComponents.SlotMarkerComponent)
    def onAddedSlotMarker(self, gameObject, slotMarker):
        for assembler in self.__assemblers:
            if assembler.checkSlotMarker(slotMarker):
                assembler.assemble(gameObject, slotMarker)
