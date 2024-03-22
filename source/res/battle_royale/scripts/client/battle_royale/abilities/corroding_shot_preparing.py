# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/abilities/corroding_shot_preparing.py
import CGF
import math_utils
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from cgf_script.bonus_caps_rules import bonusCapsManager
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
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
    category = 'Abilities'
    domain = CGF.DomainOption.DomainClient
    gunNode = ComponentProperty(type=CGFMetaTypes.LINK, value=CGF.GameObject, editorName='Gun Node')


@registerComponent
class CorrodingShotPreparingNodeComponent(object):
    editorTitle = 'Corroding Shot Preparing Node Component'
    category = 'Abilities'
    domain = CGF.DomainOption.DomainClient
    effectPathTemplate = ComponentProperty(type=CGFMetaTypes.STRING, value='', editorName='Effect Path Template')


@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, CGF.DomainOption.DomainClient)
class CorrodingShotPreparingManager(CGF.ComponentManager):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    @onAddedQuery(VehicleCorrodingShotPreparingComponent, CGF.GameObject)
    def visualizeAbility(self, vehicleAbilityComponent, _):
        self.__launch(vehicleAbilityComponent)

    def __launch(self, vehicleAbilityComponent):
        appearance = vehicleAbilityComponent.entity.appearance

        def postloadSetup(go):
            corrodingShotPreparingComponent = go.findComponentByType(CorrodingShotPreparingComponent)
            self.__setupVFX(corrodingShotPreparingComponent.gunNode, vehicleAbilityComponent.entity)

        equipmentID = vehicles.g_cache.equipmentIDs().get(VehicleCorrodingShotPreparingComponent.EQUIPMENT_NAME)
        equipment = vehicles.g_cache.equipments()[equipmentID]
        loadAppearancePrefab(equipment.usagePrefab, appearance, postloadSetup)

    def __setupVFX(self, nodeGO, vehicle):
        appearance = vehicle.appearance
        nodeComponent = nodeGO.findComponentByType(CorrodingShotPreparingNodeComponent)
        transformComponent = nodeGO.findComponentByType(GenericComponents.TransformComponent)
        offset = _GUN_EFFECT_OFFSET.get(vehicle.typeDescriptor.gun.name, 0.0)
        if transformComponent:
            transformComponent.transform = math_utils.createSRTMatrix((1.0, 1.0, 1.0), (0.0, 0.0, 0.0), (0.0, offset, 0.0))
        effectName = getEffectSuffixForGunLength(_GUN_LENGTH_RANGES, appearance)
        nodeGO.removeComponentByType(GenericComponents.AnimatorComponent)
        nodeGO.createComponent(GenericComponents.AnimatorComponent, nodeComponent.effectPathTemplate.format(effectName), 0, 1, -1, True, '')
        nodeGO.deactivate()
        nodeGO.activate()

    @onRemovedQuery(VehicleCorrodingShotPreparingComponent, CGF.GameObject, UpgradeInProgressComponent)
    def inBattleUpgradeCompleted(self, vehicleAbilityComponent, *_):
        self.__launch(vehicleAbilityComponent)

    @onRemovedQuery(VehicleCorrodingShotPreparingComponent, CGF.GameObject)
    def stopVisualizeAbility(self, _, gameObject):
        h = CGF.HierarchyManager(gameObject.spaceID)
        effectRoots = h.findComponentsInHierarchy(gameObject, CorrodingShotPreparingComponent)
        for effectRoot, _ in effectRoots:
            CGF.removeGameObject(effectRoot)
