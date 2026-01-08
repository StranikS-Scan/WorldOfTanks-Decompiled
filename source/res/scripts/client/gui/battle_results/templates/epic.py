# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/templates/epic.py
from gui.battle_results.templates import regular
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES
from helpers import i18n
from gui.Scaleform.locale.MENU import MENU
from gui.battle_results.components import base
from gui.battle_results.components import personal
from gui.battle_results.components import vehicles
from gui.battle_results.components import common
from gui.battle_results.components import shared
from gui.battle_results.components import style
from gui.battle_results.components import epic
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
regular.FINISH_RESULT_VO_META.bind(common.EpicBattleBattleFinishResultBlock)
_EPIC_TABS_VO_META = base.ListMeta([{'label': i18n.makeString(MENU.FINALSTATISTIC_TABS_EPICSTATS),
  'linkage': 'EpicStatsUI',
  'viewId': 'EpicStatsUI',
  'showWndBg': False}, {'label': i18n.makeString(MENU.FINALSTATISTIC_TABS_TEAMSTATS),
  'linkage': 'TeamStatsUI',
  'viewId': 'TeamStatsUI',
  'showWndBg': False}, {'label': i18n.makeString(MENU.FINALSTATISTIC_TABS_DETAILSSTATS),
  'linkage': 'DetailsStatsViewUI',
  'viewId': 'DetailsStatsViewUI',
  'showWndBg': True}])
_TOTAL_EFFICIENCY_EPIC_HEADER_META = base.PropertyMeta(((BATTLE_EFFICIENCY_TYPES.DESTRUCTION, '-', 'kills'),
 (BATTLE_EFFICIENCY_TYPES.DAMAGE, '-', 'damageDealt'),
 (BATTLE_EFFICIENCY_TYPES.CRITS, '-', 'criticalDamages'),
 (BATTLE_EFFICIENCY_TYPES.ARMOR, '-', 'damageBlockedByArmor'),
 (BATTLE_EFFICIENCY_TYPES.ASSIST, '-', 'damageAssisted'),
 (BATTLE_EFFICIENCY_TYPES.DETECTION, '-', 'spotted'),
 (BATTLE_EFFICIENCY_TYPES.ASSIST_STUN, '-', 'damageAssistedStun'),
 ('killTooltip', None, 'killsTooltip'),
 ('damageTooltip', None, 'damageDealtTooltip'),
 ('critsTooltip', None, 'criticalDamagesTooltip'),
 ('armorTooltip', None, 'damageBlockedTooltip'),
 ('assistTooltip', None, 'damageAssistedTooltip'),
 ('spottedTooltip', None, 'spottedTooltip'),
 ('stunTooltip', None, 'damageAssistedStunTooltip'),
 ('hasEfficencyStats', None, 'hasEfficencyStats'),
 ('damageToSupplies', None, 'damageToSupplies'),
 ('suppliesDestroyed', None, 'suppliesDestroyed'),
 ('questsCompleted', None, 'questsCompleted')))
_TOTAL_EFFICIENCY_EPIC_HEADER_META.bind(epic.EpicTotalEfficiencyDetailsHeader)
EPIC_TABS_BLOCK = base.StatsBlock(_EPIC_TABS_VO_META, 'tabInfo')
EPIC_TIME_STATS_BLOCK = base.StatsBlock(base.ListMeta(runtime=False), 'timeStats', _RECORD.COMMON)
EPIC_TIME_STATS_BLOCK.addComponent(0, common.ArenaShortTimeVO('arenaCreateTimeOnlyStr', 'arenaCreateTime'))
EPIC_TIME_STATS_BLOCK.addComponent(1, common.ArenaDurationVO('duration', 'duration'))
EPIC_TIME_STATS_BLOCK.addNextComponent(common.ObjectivesReachedVO('objectivesReached'))
EPIC_TIME_STATS_BLOCK.addNextComponent(common.ObjectivesDestroyedVO('objectivesDestroyed'))
EPIC_TIME_STATS_BLOCK.addNextComponent(common.BasesCapturedVO('basesCaptured'))
EPIC_COMMON_STATS_BLOCK = regular.REGULAR_COMMON_STATS_BLOCK.clone(7, 9, 10, 11)
EPIC_COMMON_STATS_BLOCK.addComponent(7, common.EpicBattleBattleFinishResultBlock())
EPIC_COMMON_STATS_BLOCK.addComponent(9, personal.EpicVehicleNamesBlock(base.ListMeta(), 'playerVehicleNames'))
EPIC_COMMON_STATS_BLOCK.addComponent(10, personal.EpicVehiclesBlock(base.ListMeta(), 'playerVehicles', _RECORD.PERSONAL))
EPIC_COMMON_STATS_BLOCK.addComponent(11, EPIC_TIME_STATS_BLOCK.clone())
EPIC_COMMON_STATS_BLOCK.addNextComponent(shared.WasInEpicBattleItem('epicMode'))
EPIC_PERSONAL_STATS_BLOCK = regular.REGULAR_PERSONAL_STATS_BLOCK.clone(0, 8)
EPIC_PERSONAL_STATS_BLOCK.addComponent(0, epic.EpicTotalEfficiencyDetailsHeader(_TOTAL_EFFICIENCY_EPIC_HEADER_META, 'efficiencyHeader', _RECORD.PERSONAL))
EPIC_PERSONAL_STATS_BLOCK.addComponent(8, vehicles.PersonalVehiclesEpicStatsBlock(base.ListMeta(), 'statValues', _RECORD.PERSONAL))
EPIC_PERSONAL_STATS_BLOCK.addNextComponent(personal.PlayerRank('playerRank'))
EPIC_TEAM_ITEM_VO_META = regular.TEAM_ITEM_VO_META.replace(('statValues', vehicles.AllEpicVehicleStatValuesBlock(base.ListMeta(), 'statValues'), 'statValues'))
EPIC_TEAM_ITEM_VO_META.bind(vehicles.EpicVehicleStatsBlock)
EPIC_VEHICLE_STATS_BLOCK_VO_META = base.PropertyMeta((('shots', 0, 'shots'),
 ('hits', style.SlashedValuesBlock('hits'), 'hits'),
 ('explosionHits', 0, 'explosionHits'),
 ('damageDealt', 0, 'damageDealt'),
 ('sniperDamageDealt', 0, 'sniperDamageDealt'),
 ('destructiblesDamageDealt', 0, 'destructiblesDamageDealt'),
 ('equipmentDamageDealt', 0, 'equipmentDamageDealt'),
 ('directHitsReceived', 0, 'directHitsReceived'),
 ('piercingsReceived', 0, 'piercingsReceived'),
 ('noDamageDirectHitsReceived', 0, 'noDamageDirectHitsReceived'),
 ('explosionHitsReceived', 0, 'explosionHitsReceived'),
 ('damageBlockedByArmor', 0, 'damageBlockedByArmor'),
 ('teamHitsDamage', style.RedSlashedValuesBlock('teamHitsDamage'), 'teamHitsDamage'),
 ('spotted', 0, 'spotted'),
 ('damagedKilled', style.SlashedValuesBlock('damagedKilled'), 'damagedKilled'),
 ('damageAssisted', 0, 'damageAssisted'),
 ('equipmentDamageAssisted', 0, 'equipmentDamageAssisted'),
 ('damageAssistedStun', 0, 'damageAssistedStun'),
 ('stunNum', 0, 'stunNum'),
 ('capturePointsVal', style.SlashedValuesBlock('capturePointsVal'), 'capturePoints'),
 ('timesDestroyed', 0, 'timesDestroyed'),
 ('teamSpecificStat', 0, 'teamSpecificStat'),
 ('damageToSupplies', 0, 'damageToSupplies'),
 ('damageFromSupplies', 0, 'damageFromSupplies'),
 ('suppliesDestroyed', 0, 'suppliesDestroyed'),
 ('distributedSupplyDamage', 0, 'distributedSupplyDamage'),
 ('distributedSupplyBasePoints', style.SlashedValuesBlock('distributedSupplyBasePoints'), 'distributedSupplyBasePoints')))
EPIC_VEHICLE_STATS_BLOCK_VO_META.bind(vehicles.EpicVehicleStatValuesBlock)
EPIC_TEAMS_STATS_BLOCK = vehicles.TwoTeamsStatsBlock(regular.TEAMS_VO_META.clone(), '', _RECORD.VEHICLES)
EPIC_TEAMS_STATS_BLOCK.addNextComponent(vehicles.EpicTeamStatsBlock(meta=base.ListMeta(), field='team1'))
EPIC_TEAMS_STATS_BLOCK.addNextComponent(vehicles.EpicTeamStatsBlock(meta=base.ListMeta(), field='team2'))
