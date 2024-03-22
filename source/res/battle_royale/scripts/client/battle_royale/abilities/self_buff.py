# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/abilities/self_buff.py
import BigWorld
import CGF
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from cgf_script.bonus_caps_rules import bonusCapsManager
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
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
    category = 'Abilities'
    domain = CGF.DomainOption.DomainClient
    gunNode = ComponentProperty(type=CGFMetaTypes.LINK, value=CGF.GameObject, editorName='Gun Node')


@registerComponent
class SelfBuffNodeComponent(object):
    editorTitle = 'Self Buff Node Component'
    category = 'Abilities'
    domain = CGF.DomainOption.DomainClient
    effectPathTemplate = ComponentProperty(type=CGFMetaTypes.STRING, value='', editorName='Effect Path Template')


@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, CGF.DomainOption.DomainClient)
class SelfBuffComponentManager(CGF.ComponentManager):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    @onAddedQuery(VehicleSelfBuffComponent, CGF.GameObject)
    def visualizeSelfBuff(self, vehicleSelfBuffComponent, _):
        self.__launch(vehicleSelfBuffComponent)

    def __launch(self, vehicleSelfBuffComponent):
        appearance = vehicleSelfBuffComponent.entity.appearance

        def postloadSetup(go):
            selfBuffComponent = go.findComponentByType(SelfBuffComponent)
            self.__setupVFX(selfBuffComponent.gunNode, appearance)
            go.createComponent(GenericComponents.RemoveGoDelayedComponent, vehicleSelfBuffComponent.finishTime - BigWorld.serverTime())

        equipmentID = vehicles.g_cache.equipmentIDs().get(VehicleSelfBuffComponent.EQUIPMENT_NAME)
        equipment = vehicles.g_cache.equipments()[equipmentID]
        loadAppearancePrefab(equipment.usagePrefab, appearance, postloadSetup)

    def __setupVFX(self, nodeGO, appearance):
        nodeComponent = nodeGO.findComponentByType(SelfBuffNodeComponent)
        effectName = getEffectSuffixForGunLength(_GUN_LENGTH_RANGES, appearance)
        nodeGO.removeComponentByType(GenericComponents.AnimatorComponent)
        nodeGO.createComponent(GenericComponents.AnimatorComponent, nodeComponent.effectPathTemplate.format(effectName), 0, 1, -1, True, '')
        nodeGO.deactivate()
        nodeGO.activate()

    @onRemovedQuery(VehicleSelfBuffComponent, CGF.GameObject, UpgradeInProgressComponent)
    def inBattleUpgradeCompleted(self, vehicleSelfBuffComponent, *_):
        self.__launch(vehicleSelfBuffComponent)
