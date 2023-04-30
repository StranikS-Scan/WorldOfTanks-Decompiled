# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/abilities/shot_passion.py
import BigWorld
import CGF
import Math
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from battle_royale.gui.constants import BattleRoyaleEquipments
from cgf_script.bonus_caps_rules import bonusCapsManager
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from constants import IS_CLIENT
from Event import EventsSubscriber
from helpers import dependency
import math_utils
import GenericComponents
from items import vehicles
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicle_systems.model_assembler import loadAppearancePrefab
from vehicle_systems.tankStructure import TankNodeNames
if IS_CLIENT:
    from VehicleShotPassionComponent import VehicleShotPassionComponent
    from InBattleUpgrades import UpgradeInProgressComponent
else:

    class VehicleShotPassionComponent(object):
        pass


    class UpgradeInProgressComponent(object):
        pass


_NODE_NAME_IDX = {TankNodeNames.TURRET_JOINT: 0,
 TankNodeNames.GUN_INCLINATION: 1}

@registerComponent
class ShotPassionComponent(object):
    editorTitle = 'Shot Passion Component'
    category = 'Abilities'
    domain = CGF.DomainOption.DomainClient
    turretNode = ComponentProperty(type=CGFMetaTypes.LINK, value=CGF.GameObject, editorName='Turret Node')
    gunNode = ComponentProperty(type=CGFMetaTypes.LINK, value=CGF.GameObject, editorName='Gun Node')


@registerComponent
class ShotPassionNodeComponent(object):
    editorTitle = 'Shot Passion Node Component'
    category = 'Abilities'
    domain = CGF.DomainOption.DomainClient
    effectTemplate = ComponentProperty(type=CGFMetaTypes.STRING, value='', editorName='Effect Template')
    maxAnimationStage = ComponentProperty(type=CGFMetaTypes.INT, value=0, editorName='Max animation stage')


@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE)
class ShotPassionManager(CGF.ComponentManager):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(ShotPassionManager, self).__init__()
        self.__eventSubscriber = None
        return

    def deactivate(self):
        if self.__eventSubscriber is not None:
            self.__eventSubscriber.unsubscribeFromAllEvents()
            self.__eventSubscriber = None
        return

    @onAddedQuery(VehicleShotPassionComponent, CGF.GameObject)
    def visualizeShotPassion(self, shotPassionComponent, go):
        if self.__eventSubscriber is None:
            self.__eventSubscriber = EventsSubscriber()
            self.__eventSubscriber.subscribeToContextEvent(self.__guiSessionProvider.shared.vehicleState.onEquipmentComponentUpdated, self.__onEquipmentComponentUpdated, VehicleShotPassionComponent.EQUIPMENT_NAME)
        self.__launch(shotPassionComponent)
        return

    def endShotPassion(self, vehicle):

        def postloadSetup(go):
            go.createComponent(GenericComponents.RedirectorComponent, vehicle.appearance.gameObject)

        if vehicle is not None and vehicle.isAlive() and vehicle.appearance:
            equipmentID = vehicles.g_cache.equipmentIDs().get(VehicleShotPassionComponent.EQUIPMENT_NAME)
            equipment = vehicles.g_cache.equipments()[equipmentID]
            CGF.loadGameObjectIntoHierarchy(equipment.posteffectPrefab, vehicle.appearance.partsGameObjects.getPartGameObject(TankNodeNames.GUN_INCLINATION, vehicle.appearance.gameObject.spaceID, vehicle.appearance.gameObject), Math.Vector3(0, 0, 0), postloadSetup)
        return

    def __launch(self, vehicleShotPassionComponent):

        def postloadSetup(go):
            shotPassionComponent = go.findComponentByType(ShotPassionComponent)
            stage = vehicleShotPassionComponent.stage
            self.__setupVFX(shotPassionComponent.gunNode, stage)
            self.__setupVFX(shotPassionComponent.turretNode, stage)
            go.createComponent(GenericComponents.RemoveGoDelayedComponent, vehicleShotPassionComponent.finishTime - BigWorld.serverTime())

        appearance = vehicleShotPassionComponent.entity.appearance
        equipmentID = vehicles.g_cache.equipmentIDs().get(VehicleShotPassionComponent.EQUIPMENT_NAME)
        equipment = vehicles.g_cache.equipments()[equipmentID]
        loadAppearancePrefab(equipment.usagePrefab, appearance, postloadSetup)

    def __setupVFX(self, nodeGO, stage):
        nodeComponent = nodeGO.findComponentByType(ShotPassionNodeComponent)
        effectTemplate = nodeComponent.effectTemplate
        nodeGO.removeComponentByType(GenericComponents.AnimatorComponent)
        nodeGO.createComponent(GenericComponents.AnimatorComponent, effectTemplate.format(math_utils.clamp(0, nodeComponent.maxAnimationStage, stage)), 0, 1, -1, True, '')
        nodeGO.deactivate()
        nodeGO.activate()

    def __onEquipmentComponentUpdated(self, _, vehicleID, data):
        vehicle = BigWorld.entity(vehicleID)
        duration = data.get('duration', 0)
        if duration > 0:
            effectGO = self.getEffectGO(vehicle.entityGameObject)
            if not effectGO.isValid():
                return
            stage = data.get('stage', 0)
            shotPassionComponent = effectGO.findComponentByType(ShotPassionComponent)
            self.__setupVFX(shotPassionComponent.turretNode, stage)
            self.__setupVFX(shotPassionComponent.gunNode, stage)
        else:
            self.endShotPassion(vehicle)

    def getEffectGO(self, partGO):
        return CGF.HierarchyManager(partGO.spaceID).findFirstNode(partGO, BattleRoyaleEquipments.SHOT_PASSION)

    @onRemovedQuery(VehicleShotPassionComponent, CGF.GameObject, UpgradeInProgressComponent)
    def inBattleUpgradeCompleted(self, shotPassionComponent, gameObject, _):
        self.__launch(shotPassionComponent)
