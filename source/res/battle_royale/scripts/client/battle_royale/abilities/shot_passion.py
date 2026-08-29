# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/abilities/shot_passion.py
from __future__ import absolute_import
import BigWorld
import CGF
import Math
from typing import List, Any
from battle_royale.gui.constants import BattleRoyaleEquipments
from cgf_script.registration import ComponentProperty, registerComponent
from constants import IS_CLIENT
from Event import EventsSubscriber
from helpers import dependency
import math_utils
import GenericComponents
from items import vehicles
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicle_systems.model_assembler import loadAppearancePrefab
from vehicle_systems.tankStructure import TankNodeNames, TankPartNames
from battle_royale.abilities.common import getEffectSuffixForGunLength
if IS_CLIENT:
    from VehicleShotPassionComponent import VehicleShotPassionComponent
    from InBattleUpgrades import UpgradeInProgressComponent
else:

    class VehicleShotPassionComponent(object):
        pass


    class UpgradeInProgressComponent(object):
        pass


_GUN_LENGTH_RANGES = {'short': (0.0, 3.7),
 'med': (3.7, 4.2),
 'med_02': (4.2, 5.0),
 'long': (5.0, float('inf'))}
_NODE_NAME_IDX = {TankNodeNames.TURRET_JOINT: 0,
 TankNodeNames.GUN_INCLINATION: 1}

@registerComponent
class ShotPassionComponent(object):
    editorTitle = 'Shot Passion Component'
    group = 'Abilities'
    domain = CGF.Domain.Client
    turretNode = ComponentProperty(type=CGF.PropertyType.Link, value=CGF.GameObject, editorName='Turret Node')
    gunNode = ComponentProperty(type=CGF.PropertyType.Link, value=CGF.GameObject, editorName='Gun Node')


@registerComponent
class ShotPassionNodeComponent(object):
    editorTitle = 'Shot Passion Node Component'
    group = 'Abilities'
    domain = CGF.Domain.Client
    effectTemplate = ComponentProperty(type=CGF.PropertyType.String, value='', editorName='Effect Template')
    maxAnimationStage = ComponentProperty(type=CGF.PropertyType.Int, value=0, editorName='Max animation stage')


class ShotPassionSystem(CGF.System):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    VehicleShotPassionActivated = CGF.ActivateReaction(CGF.ReactRw(VehicleShotPassionComponent))
    UpgradeDeactivated = CGF.DeactivateReaction(CGF.ReactRo(UpgradeInProgressComponent), CGF.Rw(VehicleShotPassionComponent))
    ShotPassionAccess = CGF.AccessReaction(CGF.Rw(ShotPassionComponent))
    ShotPassionNodeAccess = CGF.AccessReaction(CGF.Rw(ShotPassionNodeComponent))
    Reactions = CGF.Reactions(VehicleShotPassionActivated, UpgradeDeactivated, ShotPassionAccess, ShotPassionNodeAccess)

    def update(self):
        for _, shotPassionComponent in self.reaction(self.UpgradeDeactivated):
            self.inBattleUpgradeCompleted(shotPassionComponent)

        for shotPassionComponent in self.reaction(self.VehicleShotPassionActivated):
            self.visualizeShotPassion(shotPassionComponent)

    def __init__(self):
        super(ShotPassionSystem, self).__init__()
        self.__eventSubscriber = None
        return

    def onMappingUnloaded(self):
        if self.__eventSubscriber is not None:
            self.__eventSubscriber.unsubscribeFromAllEvents()
            self.__eventSubscriber = None
        return

    def visualizeShotPassion(self, shotPassionComponent):
        if self.__eventSubscriber is None:
            self.__eventSubscriber = EventsSubscriber()
            self.__eventSubscriber.subscribeToContextEvent(self.__guiSessionProvider.shared.vehicleState.onEquipmentComponentUpdated, self.__onEquipmentComponentUpdated, VehicleShotPassionComponent.EQUIPMENT_NAME)
        self.__launch(shotPassionComponent)
        return

    def endShotPassion(self, vehicle):

        def postloadSetup(objects, queue):
            root = objects[0]
            queue.createComponent(root, GenericComponents.RedirectorComponent, vehicle.appearance.gameObject)

        if vehicle is not None and vehicle.isAlive() and vehicle.appearance:
            equipmentID = vehicles.g_cache.equipmentIDs().get(VehicleShotPassionComponent.EQUIPMENT_NAME)
            equipment = vehicles.g_cache.equipments()[equipmentID]
            CGF.loadAndCreatePrefabWithParent(equipment.posteffectPrefab, vehicle.appearance.partsGameObjects.getPartGameObject(TankNodeNames.GUN_INCLINATION, vehicle.appearance.gameObject.spaceID, vehicle.appearance.gameObject), Math.Vector3(0, 0, 0), postloadSetup)
        return

    def __launch(self, vehicleShotPassionComponent):
        vehicle = vehicleShotPassionComponent.entity
        if vehicle.isDestroyed:
            return
        appearance = vehicle.appearance
        stage = vehicleShotPassionComponent.stage
        finishTime = vehicleShotPassionComponent.finishTime

        def postloadSetup(root, _, queue):
            shotPassionComponent = queue.component(root, ShotPassionComponent)
            gun = queue.pendingGameObject(shotPassionComponent.gunNode)
            turret = queue.pendingGameObject(shotPassionComponent.turretNode)
            self.__setupPostLoadVFX(gun, stage, appearance, TankPartNames.GUN, queue)
            self.__setupPostLoadVFX(turret, stage, appearance, TankPartNames.TURRET, queue)
            queue.createComponent(root, GenericComponents.RemoveGoDelayedComponent, finishTime - BigWorld.serverTime())

        equipmentID = vehicles.g_cache.equipmentIDs().get(VehicleShotPassionComponent.EQUIPMENT_NAME)
        equipment = vehicles.g_cache.equipments()[equipmentID]
        loadAppearancePrefab(equipment.usagePrefab, appearance, postloadSetup, False)

    def __setupPostLoadVFX(self, nodeGO, stage, appearance, nodeType, queue):
        nodeComponent = queue.component(nodeGO, ShotPassionNodeComponent)
        effectTemplate = nodeComponent.effectTemplate
        stageClamp = math_utils.clamp(0, nodeComponent.maxAnimationStage, stage)
        if nodeType == TankPartNames.GUN:
            effectPath = effectTemplate.format(stage=stageClamp, length=getEffectSuffixForGunLength(_GUN_LENGTH_RANGES, appearance))
        else:
            effectPath = effectTemplate.format(stage=stageClamp)
        if queue.hasComponent(nodeGO, GenericComponents.AnimatorComponent):
            queue.removeComponent(nodeGO, GenericComponents.AnimatorComponent)
        queue.createComponent(nodeGO, GenericComponents.AnimatorComponent, effectPath, 0, 1, -1, True, '')

    def __onEquipmentComponentUpdated(self, _, vehicleID, data):
        vehicle = BigWorld.entity(vehicleID)
        duration = data.get('duration', 0)
        if duration > 0:
            effectGO = self.getEffectGO(vehicle.entityGameObject)
            if not effectGO.valid:
                return
            stage = data.get('stage', 0)
            shotPassionAccess = self.reaction(self.ShotPassionAccess)
            shotPassionNodeAccess = self.reaction(self.ShotPassionNodeAccess)
            shotPassionComponent = shotPassionAccess.find(effectGO)
            manager = self.gom
            q = CGF.CommandQueue(manager)
            turret = manager.gameObject(shotPassionComponent.turretNode)
            gun = manager.gameObject(shotPassionComponent.gunNode)
            self.__setupVFX(turret, q, stage, vehicle.appearance, TankPartNames.TURRET, shotPassionNodeAccess)
            self.__setupVFX(gun, q, stage, vehicle.appearance, TankPartNames.GUN, shotPassionNodeAccess)
        else:
            self.endShotPassion(vehicle)

    def __setupVFX(self, nodeGO, queue, stage, appearance, nodeType, nodeAccess):
        nodeComponent = nodeAccess.find(nodeGO)
        if not nodeComponent or nodeComponent is None:
            return
        else:
            effectTemplate = nodeComponent.effectTemplate
            stageClamp = math_utils.clamp(0, nodeComponent.maxAnimationStage, stage)
            if nodeType == TankPartNames.GUN:
                effectPath = effectTemplate.format(stage=stageClamp, length=getEffectSuffixForGunLength(_GUN_LENGTH_RANGES, appearance))
            else:
                effectPath = effectTemplate.format(stage=stageClamp)
            queue.removeComponent(nodeGO, GenericComponents.AnimatorComponent)
            queue.createComponent(nodeGO, GenericComponents.AnimatorComponent, effectPath, 0, 1, -1, True, '')
            nodeGO.deactivate()
            nodeGO.activate()
            return

    def getEffectGO(self, partGO):
        return self.hierarchy.findFirstNodeByName(partGO, BattleRoyaleEquipments.SHOT_PASSION)

    def inBattleUpgradeCompleted(self, shotPassionComponent):
        self.__launch(shotPassionComponent)
