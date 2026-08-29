# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/abilities/corroding_shot_preparing.py
from __future__ import absolute_import
import CGF
from typing import List
import math_utils
from cgf_script.registration import ComponentProperty, registerComponent
from constants import IS_CLIENT
from helpers import dependency
import GenericComponents
from items import vehicles
from battle_royale.abilities.common import getEffectSuffixForGunLength
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicle_systems.model_assembler import loadAppearancePrefab
if IS_CLIENT:
    from VehicleCorrodingShotPreparingComponent import VehicleCorrodingShotPreparingComponent
    from InBattleUpgrades import UpgradeInProgressComponent
else:

    class VehicleCorrodingShotPreparingComponent(object):
        pass


    class UpgradeInProgressComponent(object):
        pass


_GUN_LENGTH_RANGES = {'short': (0.0, 2.2),
 'med': (2.2, 4.0),
 'med_02': (4.0, 5.0),
 'long': (5.0, float('inf'))}
_GUN_EFFECT_OFFSET = {'_105mm_F34M_G1_SH': 0.07646,
 '_85mm_56_85TG_FT_G3_SH': 0.03535,
 '_76mm_54-76T_G2_SH': 0.03767}

@registerComponent
class CorrodingShotPreparingComponent(object):
    editorTitle = 'Corroding Shot Preparing Component'
    group = 'Abilities'
    domain = CGF.Domain.Client
    gunNode = ComponentProperty(type=CGF.PropertyType.Link, value=CGF.GameObject, editorName='Gun Node')


@registerComponent
class CorrodingShotPreparingNodeComponent(object):
    editorTitle = 'Corroding Shot Preparing Node Component'
    group = 'Abilities'
    domain = CGF.Domain.Client
    effectPathTemplate = ComponentProperty(type=CGF.PropertyType.String, value='', editorName='Effect Path Template')


class CorrodingShotPreparingSystem(CGF.System):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    VehicleShotActivated = CGF.ActivateReaction(CGF.ReactRw(VehicleCorrodingShotPreparingComponent))
    BattleUpgradeDeactivated = CGF.DeactivateReaction(CGF.ReactRo(UpgradeInProgressComponent), CGF.Rw(VehicleCorrodingShotPreparingComponent))
    VehicleShotDeactivated = CGF.DeactivateReaction(CGF.GameObject, CGF.ReactRo(VehicleCorrodingShotPreparingComponent))
    Reactions = CGF.Reactions(VehicleShotActivated, BattleUpgradeDeactivated, VehicleShotDeactivated)

    def update(self):
        for _, vehicleAbilityComponent in self.reaction(self.BattleUpgradeDeactivated):
            self.inBattleUpgradeCompleted(vehicleAbilityComponent)

        q = CGF.CommandQueue(self.gom)
        for gameObject, _ in self.reaction(self.VehicleShotDeactivated):
            self.stopVisualizeAbility(gameObject, q)

        for vehicleAbilityComponent in self.reaction(self.VehicleShotActivated):
            self.visualizeAbility(vehicleAbilityComponent)

    def visualizeAbility(self, vehicleAbilityComponent):
        self.__launch(vehicleAbilityComponent)

    def __launch(self, vehicleAbilityComponent):
        abilityEntity = vehicleAbilityComponent.entity
        if abilityEntity.isDestroyed:
            return

        def postloadSetup(root, objects, queue):
            corrodingShotPreparingComponent = queue.component(root, CorrodingShotPreparingComponent)
            node = queue.pendingGameObject(corrodingShotPreparingComponent.gunNode)
            self.__setupVFX(node, abilityEntity, queue)

        equipmentID = vehicles.g_cache.equipmentIDs().get(VehicleCorrodingShotPreparingComponent.EQUIPMENT_NAME)
        equipment = vehicles.g_cache.equipments()[equipmentID]
        loadAppearancePrefab(equipment.usagePrefab, abilityEntity.appearance, postloadSetup, False)

    def __setupVFX(self, nodeGO, vehicle, queue):
        appearance = vehicle.appearance
        nodeComponent = queue.component(nodeGO, CorrodingShotPreparingNodeComponent)
        transformComponent = queue.component(nodeGO, CGF.TransformComponent)
        offset = _GUN_EFFECT_OFFSET.get(vehicle.typeDescriptor.gun.name, 0.0)
        if transformComponent:
            transformComponent.transform = math_utils.createSRTMatrix((1.0, 1.0, 1.0), (0.0, 0.0, 0.0), (0.0, offset, 0.0))
        effectName = getEffectSuffixForGunLength(_GUN_LENGTH_RANGES, appearance)
        if queue.hasComponent(nodeGO, GenericComponents.AnimatorComponent):
            queue.removeComponent(nodeGO, GenericComponents.AnimatorComponent)
        queue.createComponent(nodeGO, GenericComponents.AnimatorComponent, nodeComponent.effectPathTemplate.format(effectName), 0, 1, -1, True, '')

    def inBattleUpgradeCompleted(self, vehicleAbilityComponent):
        self.__launch(vehicleAbilityComponent)

    def stopVisualizeAbility(self, gameObject, queue):
        corrodingShots = CGF.findInHierarchyWithComponent(gameObject, CorrodingShotPreparingComponent)
        for corrodingShot in corrodingShots:
            queue.removeGameObject(corrodingShot.object)
