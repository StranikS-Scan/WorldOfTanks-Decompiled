# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/templates/football_battles.py
from gui.battle_results.components import base
from gui.battle_results.components import shared
from gui.battle_results.components import style
from gui.battle_results.components import vehicles
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
from gui.battle_results.templates import regular
from gui.battle_results.components import common
from gui.Scaleform.locale.MENU import MENU
from helpers import i18n
regular.FINISH_RESULT_VO_META.bind(common.FootballBattleFinishResultBlock)
_FOOTBALL_TABS_VO_META = base.ListMeta([{'label': i18n.makeString(MENU.FINALSTATISTIC_TABS_COMMONSTATS),
  'linkage': 'CommonStats',
  'showWndBg': False}, {'label': i18n.makeString(MENU.FINALSTATISTIC_TABS_TEAMSTATS),
  'linkage': 'TeamStatsUI',
  'showWndBg': False}, {'label': i18n.makeString(MENU.FINALSTATISTIC_TABS_DETAILSSTATS),
  'linkage': 'DetailsStatsViewUI',
  'showWndBg': True}])
FOOTBALL_TABS_BLOCK = base.StatsBlock(_FOOTBALL_TABS_VO_META, 'tabInfo')
FOOTBALL_COMMON_STATS_BLOCK = regular.REGULAR_COMMON_STATS_BLOCK.clone(7)
FOOTBALL_COMMON_STATS_BLOCK.addComponent(7, common.FootballBattleFinishResultBlock())
FOOTBALL_COMMON_STATS_BLOCK.addNextComponent(shared.WasInFootballBattleItem('eventMode'))
FOOTBALL_COMMON_STATS_BLOCK.addNextComponent(shared.FootballBattleScoreItem('footballScore'))
FOOTBALL_PERSONAL_STATS_BLOCK = regular.REGULAR_PERSONAL_STATS_BLOCK.clone(15)
FOOTBALL_PERSONAL_STATS_BLOCK.addComponent(15, vehicles.PersonalVehiclesFootballStatsBlock(base.ListMeta(), 'statValues', _RECORD.PERSONAL))
FOOTBALL_VEHICLE_STATS_BLOCK_VO_META = base.PropertyMeta((('shots', 0, 'shots'),
 ('hits', style.SlashedValuesBlock('hits'), 'hits'),
 ('directHitsReceived', 0, 'directHitsReceived'),
 ('piercingsReceived', 0, 'piercingsReceived'),
 ('goals', 0, 'goals'),
 ('selfGoals', 0, 'selfGoals'),
 ('assists', 0, 'assists'),
 ('productivityPoints', 0, 'productivityPoints')))
FOOTBALL_VEHICLE_STATS_BLOCK_VO_META.bind(vehicles.FootballVehicleStatValuesBlock)
FOOTBALL_TEAM_ITEM_VO_META = regular.TEAM_ITEM_VO_META.replace(('statValues', vehicles.AllFootballVehicleStatValuesBlock(base.ListMeta(), 'statValues'), 'statValues'))
FOOTBALL_TEAM_ITEM_VO_META = FOOTBALL_TEAM_ITEM_VO_META.merge(('footballAssists', 0, 'assists'), ('footballGoalsStr', 0, 'goalsStr'), ('footballGoals', 0, 'goals'))
FOOTBALL_TEAM_ITEM_VO_META.bind(vehicles.FootballVehicleStatsBlock)
FOOTBALL_TEAMS_STATS_BLOCK = vehicles.TwoTeamsStatsBlock(regular.TEAMS_VO_META.clone(), '', _RECORD.VEHICLES)
FOOTBALL_TEAMS_STATS_BLOCK.addNextComponent(vehicles.FootballTeamStatsBlock(meta=base.ListMeta(), field='team1'))
FOOTBALL_TEAMS_STATS_BLOCK.addNextComponent(vehicles.FootballTeamStatsBlock(meta=base.ListMeta(), field='team2'))
