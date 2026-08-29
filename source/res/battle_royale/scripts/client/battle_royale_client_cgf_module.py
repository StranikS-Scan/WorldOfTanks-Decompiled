# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale_client_cgf_module.py
from __future__ import absolute_import
import CGF
from battleground.berserker_effect import BerserkerEffectObjectsSystem
from battleground.components import BattlegroundSequenceSystem
from battleground.loot_drop_object import PlaneLootAirdropSystem
from constants import IS_EDITOR
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from battle_royale.mechanics.death_zones import DeathZoneDrawSystem
from cgf_script.registration import bonusCapsPredicate, registerModule
from BattleRoyaleAbilities import HealthRestoreAbilitySystem
from battle_royale.abilities.adaptation_restore_health import AdaptationHealthRestoreEffectSystem, AdaptationHealthRestoreAbilityPart, AdaptationHealthRestoreEffectArea
from battle_royale.abilities.area_abilities import AreaAbilityVisualizationSystem, AreaAbilityVisualizer
from battle_royale.abilities.corroding_shot_preparing import CorrodingShotPreparingSystem, CorrodingShotPreparingComponent, CorrodingShotPreparingNodeComponent
from battle_royale.abilities.influence_zones import InfluenceZoneVisualizationSystem, InfluenceZoneEquipmentComponent, InfluenceZoneMultiVisualizer, InfluenceZoneTerrainArea
from battle_royale.abilities.self_buff import SelfBuffSystem, SelfBuffComponent, SelfBuffNodeComponent
from battle_royale.abilities.shot_passion import ShotPassionSystem, ShotPassionComponent, ShotPassionNodeComponent
from battle_royale.abilities.thunder_strike import ThunderStrikeSystem, ThunderStrikeVisualizer
from battle_royale.cgf_components.loot_transparency import LootSensorSystem, LootSensorComponent, LootTransparencyTriggerComponent
from battle_royale.cgf_components.vehicle_highlight import VehicleHighlightSystem
from battle_royale.abilities.dynamic_cache_loader import DynamicObjectsCacheLoaderSystem
if IS_EDITOR:

    class MineFieldSystem(object):
        pass


    class AffectComponentsSystem(object):
        pass


else:
    from Mine import MineFieldSystem
    from AffectComponent import AffectComponentsSystem

@registerModule
class ClientBattleRoyaleCommonModule(object):
    name = 'Battle Royale Common Client Module'
    group = 'Common'
    systems = [CGF.RegisterSystem(VehicleHighlightSystem, domain=CGF.Domain.Client, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, spaceID)), CGF.RegisterSystem(MineFieldSystem, domain=CGF.Domain.Client, updatePeriod=0.5, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, spaceID)), CGF.RegisterSystem(PlaneLootAirdropSystem, domain=CGF.Domain.Client, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, spaceID))]
    components = []


@registerModule
class ClientBattleRoyaleAbilitiesModule(object):
    name = 'Battle Royale Abilities Client Module'
    group = 'Abilities'
    systems = [CGF.RegisterSystem(AdaptationHealthRestoreEffectSystem, domain=CGF.Domain.Client, updateAfter=(CGF.TransformUpdateSystem, HealthRestoreAbilitySystem), predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, spaceID)),
     CGF.RegisterSystem(AreaAbilityVisualizationSystem, domain=CGF.Domain.Client, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, spaceID)),
     CGF.RegisterSystem(CorrodingShotPreparingSystem, domain=CGF.Domain.Client, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, spaceID)),
     CGF.RegisterSystem(InfluenceZoneVisualizationSystem, domain=CGF.Domain.Client, updateAfter=(CGF.TransformUpdateSystem,), predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, spaceID)),
     CGF.RegisterSystem(SelfBuffSystem, domain=CGF.Domain.Client, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, spaceID)),
     CGF.RegisterSystem(ShotPassionSystem, domain=CGF.Domain.Client, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, spaceID)),
     CGF.RegisterSystem(ThunderStrikeSystem, domain=CGF.Domain.Client, updateAfter=(CGF.TransformUpdateSystem,), predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, spaceID)),
     CGF.RegisterSystem(BerserkerEffectObjectsSystem, domain=CGF.Domain.Client, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, spaceID)),
     CGF.RegisterSystem(BattlegroundSequenceSystem, domain=CGF.Domain.Client, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, spaceID)),
     CGF.RegisterSystem(DynamicObjectsCacheLoaderSystem, domain=CGF.Domain.Client, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, spaceID)),
     CGF.RegisterSystem(AffectComponentsSystem, domain=CGF.Domain.Client, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, spaceID))]
    components = [AdaptationHealthRestoreAbilityPart,
     AdaptationHealthRestoreEffectArea,
     AreaAbilityVisualizer,
     CorrodingShotPreparingComponent,
     CorrodingShotPreparingNodeComponent,
     InfluenceZoneEquipmentComponent,
     InfluenceZoneMultiVisualizer,
     InfluenceZoneTerrainArea,
     SelfBuffComponent,
     SelfBuffNodeComponent,
     ShotPassionComponent,
     ShotPassionNodeComponent,
     ThunderStrikeVisualizer]


@registerModule
class ClientBattleRoyaleSteelHunterModule(object):
    name = 'Battle Royale SteelHunter Client Module'
    group = 'Steel Hunter'
    systems = [CGF.RegisterSystem(LootSensorSystem, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, spaceID))]
    components = [LootSensorComponent, LootTransparencyTriggerComponent]


@registerModule
class DeathZonesModule(object):
    name = 'Death Zones Mechanics Module'
    desc = 'All things related to death zones in battle royale'
    group = 'Steel Hunter'
    systems = [CGF.RegisterSystem(DeathZoneDrawSystem, domain=CGF.Domain.Client, updateAfter=(CGF.TransformUpdateSystem,), updatePeriod=0.1, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, spaceID))]
