# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/abilities/self_buff.py
from __future__ import absolute_import
import BigWorld
import CGF
from typing import List
from cgf_script.registration import ComponentProperty, registerComponent
from constants import IS_CLIENT
from helpers import dependency
import GenericComponents
from items import vehicles
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicle_systems.model_assembler import loadAppearancePrefab
from battle_royale.abilities.common import getEffectSuffixForGunLength
if IS_CLIENT:
    from VehicleSelfBuffComponent import VehicleSelfBuffComponent
    from InBattleUpgrades import UpgradeInProgressComponent
else:

    class VehicleSelfBuffComponent(object):
        pass


    class UpgradeInProgressComponent(object):
        pass


_GUN_LENGTH_RANGES = {'short': (0.0, 2.0),
 'med': (2.0, 4.0),
 'med_02': (4.0, 5.0),
 'long': (5.0, float('inf'))}

@registerComponent
class SelfBuffComponent(object):
    editorTitle = 'Self Buff Component'
    group = 'Abilities'
    domain = CGF.Domain.Client
    gunNode = ComponentProperty(type=CGF.PropertyType.Link, value=CGF.GameObject, editorName='Gun Node')


@registerComponent
class SelfBuffNodeComponent(object):
    editorTitle = 'Self Buff Node Component'
    group = 'Abilities'
    domain = CGF.Domain.Client
    effectPathTemplate = ComponentProperty(type=CGF.PropertyType.String, value='', editorName='Effect Path Template')


class SelfBuffSystem(CGF.System):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    VehicleSelfBuffActivated = CGF.ActivateReaction(CGF.ReactRw(VehicleSelfBuffComponent))
    UpgradeDeactivated = CGF.DeactivateReaction(CGF.ReactRo(UpgradeInProgressComponent), CGF.Rw(VehicleSelfBuffComponent))
    SelfBuffNodeAccess = CGF.AccessReaction(CGF.Rw(SelfBuffNodeComponent))
    Reactions = CGF.Reactions(VehicleSelfBuffActivated, UpgradeDeactivated, SelfBuffNodeAccess)

    def update(self):
        for _, vehicleSelfBuffComponent in self.reaction(self.UpgradeDeactivated):
            self.inBattleUpgradeCompleted(vehicleSelfBuffComponent)

        for vehicleSelfBuffComponent in self.reaction(self.VehicleSelfBuffActivated):
            self.visualizeSelfBuff(vehicleSelfBuffComponent)

    def visualizeSelfBuff(self, vehicleSelfBuffComponent):
        self.__launch(vehicleSelfBuffComponent)

    def __launch(self, vehicleSelfBuffComponent):
        vehicle = vehicleSelfBuffComponent.entity
        if vehicle.isDestroyed:
            return
        appearance = vehicle.appearance
        finishTime = vehicleSelfBuffComponent.finishTime

        def postloadSetup(root, _, queue):
            selfBuffComponent = queue.component(root, SelfBuffComponent)
            node = queue.pendingGameObject(selfBuffComponent.gunNode)
            self.__setupVFX(node, appearance, queue)
            queue.createComponent(root, GenericComponents.RemoveGoDelayedComponent, finishTime - BigWorld.serverTime())

        equipmentID = vehicles.g_cache.equipmentIDs().get(VehicleSelfBuffComponent.EQUIPMENT_NAME)
        equipment = vehicles.g_cache.equipments()[equipmentID]
        loadAppearancePrefab(equipment.usagePrefab, appearance, postloadSetup, False)

    def __setupVFX(self, nodeGO, appearance, queue):
        nodeComponent = queue.component(nodeGO, SelfBuffNodeComponent)
        effectName = getEffectSuffixForGunLength(_GUN_LENGTH_RANGES, appearance)
        if queue.hasComponent(nodeGO, GenericComponents.AnimatorComponent):
            queue.removeComponent(nodeGO, GenericComponents.AnimatorComponent)
        queue.createComponent(nodeGO, GenericComponents.AnimatorComponent, nodeComponent.effectPathTemplate.format(effectName), 0, 1, -1, True, '')

    def inBattleUpgradeCompleted(self, vehicleSelfBuffComponent):
        self.__launch(vehicleSelfBuffComponent)
