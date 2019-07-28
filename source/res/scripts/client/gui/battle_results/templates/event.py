# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/templates/event.py
from gui.battle_results.templates import regular
from gui.battle_results.components import base, event
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
EVENT_TOTAL_VO_META = base.DictMeta({'victoryData': {}})
_EVENT_VICTORY_VO_META = base.DictMeta({'common': {},
 'isVictory': False,
 'players': {},
 'frontText': '',
 'generalText': '',
 'generalExpReward': 0,
 'frontPoints': 0,
 'generalExp': 0,
 'generalTooltip': '',
 'frontTooltip': ''})
_EVENT_PLAYER_INFO_VO_META_TUPLE = regular.TEAM_ITEM_VO_META_TUPLE + (('generalIcon', 0, 'generalIcon'),
 ('levelIcon', 0, 'levelIcon'),
 ('tooltipData', '', 'tooltipData'),
 ('status', '', 'status'),
 ('inactive', False, 'inactive'),
 ('background', '', 'background'),
 ('position', 0, 'position'),
 ('reward', 0, 'reward'))
_EVENT_PLAYER_INFO_VO_META = base.PropertyMeta(_EVENT_PLAYER_INFO_VO_META_TUPLE)
_EVENT_PLAYER_INFO_VO_META.bind(event.EventVehicleStatsBlock)
EVENT_BATTLE_COMMON_STATS_BLOCK = regular.REGULAR_COMMON_STATS_BLOCK.clone()
EVENT_VICTORY_RESULTS_BLOCK = base.StatsBlock(_EVENT_VICTORY_VO_META, 'victoryData')
EVENT_VICTORY_RESULTS_BLOCK.addNextComponent(EVENT_BATTLE_COMMON_STATS_BLOCK)
EVENT_VICTORY_RESULTS_BLOCK.addNextComponent(event.IsVictory('isVictory'))
EVENT_VICTORY_RESULTS_BLOCK.addNextComponent(event.EventBattlesTeamStatsBlock(base.ListMeta(), 'players', _RECORD.VEHICLES))
EVENT_VICTORY_RESULTS_BLOCK.addNextComponent(event.EventPoints('frontPoints', _RECORD.PERSONAL))
EVENT_VICTORY_RESULTS_BLOCK.addNextComponent(event.GeneralPoints('generalExp', _RECORD.PERSONAL))
EVENT_VICTORY_RESULTS_BLOCK.addNextComponent(event.FrontText('frontText', _RECORD.PERSONAL))
EVENT_VICTORY_RESULTS_BLOCK.addNextComponent(event.GeneralText('generalText', _RECORD.PERSONAL))
EVENT_VICTORY_RESULTS_BLOCK.addNextComponent(event.GeneralTooltip('generalTooltip', _RECORD.PERSONAL))
EVENT_VICTORY_RESULTS_BLOCK.addNextComponent(event.FrontTooltip('frontTooltip', _RECORD.PERSONAL))
