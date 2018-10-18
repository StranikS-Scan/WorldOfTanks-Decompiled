# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/templates/halloween.py
from gui.battle_results.templates import regular
from gui.battle_results.components import base, personal, halloween
from gui.battle_results.components.halloween import ProgressStatsBlock, ProgressItemStatsBlock, ProgressValueBlock, HalloweenVehicleStatsBlock
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
HALLOWEEN_TOTAL_VO_META = base.DictMeta({'victoryData': {},
 'progressData': [],
 'progressValue': (0, 0)})
_HALLOWEEN_PLAYER_INFO_VO_META_TUPLE = regular.TEAM_ITEM_VO_META_TUPLE + (('level', 0, 'level'), ('souls', 0, 'souls'), ('status', '', 'status'))
_HALLOWEEN_PLAYER_INFO_VO_META = base.PropertyMeta(_HALLOWEEN_PLAYER_INFO_VO_META_TUPLE)
_HALLOWEEN_PLAYER_INFO_VO_META.bind(HalloweenVehicleStatsBlock)
_HALLOWEEN_PROGRESS_ITEM_META = base.PropertyMeta((('index', 0, 'index'),
 ('unlocked', False, 'unlocked'),
 ('value', 0, 'value'),
 ('tooltip', '', 'tooltip'),
 ('specialAlias', None, 'specialAlias'),
 ('specialArgs', None, 'specialArgs'),
 ('isSpecial', None, 'isSpecial'),
 ('bonus', [], 'bonus'),
 ('statusDescription', '', 'statusDescription')))
_HALLOWEEN_PROGRESS_ITEM_META.bind(ProgressItemStatsBlock)
_HALLOWEEN_VICTORY_VO_META = base.DictMeta({'userName': '',
 'souls': 0,
 'hasPremium': False,
 'isLastLevel': 0,
 'players': [],
 'soulsStats': {},
 'levelStats': {},
 'premiumStats': {},
 'withPremium': {},
 'withMaxSouls': {},
 'withPremiumAndSouls': {},
 'common': {},
 'exp1Tooltip': '',
 'exp2Tooltip': ''})
HALLOWEEN_BATTLE_COMMON_STATS_BLOCK = regular.REGULAR_COMMON_STATS_BLOCK.clone()
HALLOWEEN_VICTORY_RESULTS_BLOCK = base.StatsBlock(_HALLOWEEN_VICTORY_VO_META, 'victoryData')
HALLOWEEN_VICTORY_RESULTS_BLOCK.addNextComponent(halloween.UserNameItem('userName'))
HALLOWEEN_VICTORY_RESULTS_BLOCK.addNextComponent(halloween.SoulsItem('souls', _RECORD.PERSONAL))
HALLOWEEN_VICTORY_RESULTS_BLOCK.addNextComponent(personal.PremiumAccountFlag('hasPremium'))
HALLOWEEN_VICTORY_RESULTS_BLOCK.addNextComponent(halloween.IsCompletedFlag('isLastLevel', _RECORD.PERSONAL))
HALLOWEEN_VICTORY_RESULTS_BLOCK.addNextComponent(halloween.HalloweenBattlesTeamStatsBlock(base.ListMeta(), 'players', _RECORD.VEHICLES))
HALLOWEEN_VICTORY_RESULTS_BLOCK.addNextComponent(halloween.OriginalRewardStats('soulsStats', _RECORD.PERSONAL))
HALLOWEEN_VICTORY_RESULTS_BLOCK.addNextComponent(halloween.LevelRewardStats('levelStats', _RECORD.PERSONAL))
HALLOWEEN_VICTORY_RESULTS_BLOCK.addNextComponent(halloween.PremiumRewardStats('premiumStats'))
HALLOWEEN_VICTORY_RESULTS_BLOCK.addNextComponent(halloween.WithPremiumRewardStats('withPremium'))
HALLOWEEN_VICTORY_RESULTS_BLOCK.addNextComponent(halloween.WithMaxSoulsRewardStats('withMaxSouls'))
HALLOWEEN_VICTORY_RESULTS_BLOCK.addNextComponent(halloween.Exp1Tooltip('exp1Tooltip'))
HALLOWEEN_VICTORY_RESULTS_BLOCK.addNextComponent(halloween.Exp2Tooltip('exp2Tooltip'))
HALLOWEEN_VICTORY_RESULTS_BLOCK.addNextComponent(HALLOWEEN_BATTLE_COMMON_STATS_BLOCK)
HALLOWEEN_PROGRESS_DATA_BLOCK = ProgressStatsBlock(base.ListMeta(), 'progressData', _RECORD.PERSONAL)
HALLOWEEN_PROGRESS_VALUE_BLOCK = ProgressValueBlock('progressValue', _RECORD.PERSONAL)
