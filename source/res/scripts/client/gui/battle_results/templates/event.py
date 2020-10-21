# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/templates/event.py
from gui.battle_results.templates import regular
from gui.battle_results.components import base
from gui.battle_results.components import event
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
EVENT_TOTAL_VO_META = base.DictMeta({'common': {},
 'captureStatus': '',
 'tankType': '',
 'tankName': '',
 'damage': 0,
 'matter': 0,
 'matterOnTank': 0,
 'kills': 0,
 'players': [],
 'deathReason': -1,
 'matterTooltip': {},
 'matterOnTankTooltip': {},
 'damageTooltip': {},
 'killsTooltip': {},
 'background': '',
 'time': '',
 'reward': {},
 'missions': []})
_EVENT_REWARD_VO_META = base.PropertyMeta((('exp', 0, 'exp'),
 ('credits', 0, 'credits'),
 ('freeXP', 0, 'freeXP'),
 ('expTooltip', 0, 'expTooltip'),
 ('creditsTooltip', 0, 'creditsTooltip'),
 ('freeXPTooltip', 0, 'freeXPTooltip')))
_EVENT_REWARD_VO_META.bind(event.EventRewardStatsBlock)
_EVENT_PLAYER_INFO_VO_META_TUPLE = regular.TEAM_ITEM_VO_META_TUPLE + (('matter', 0, 'matter'),
 ('matterOnTank', 0, 'matterOnTank'),
 ('tankType', 0, 'tankType'),
 ('banStatus', '', 'banStatus'),
 ('banStatusTooltip', '', 'banStatusTooltip'))
_EVENT_PLAYER_INFO_VO_META = base.PropertyMeta(_EVENT_PLAYER_INFO_VO_META_TUPLE)
_EVENT_PLAYER_INFO_VO_META.bind(event.EventVehicleStatsBlock)
EVENT_BATTLE_COMMON_STATS_BLOCK = regular.REGULAR_COMMON_STATS_BLOCK.clone()
EVENT_TOTAL_RESULTS_BLOCK = base.StatsBlock(EVENT_TOTAL_VO_META, 'victoryData')
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(EVENT_BATTLE_COMMON_STATS_BLOCK)
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.CaptureStatusItem('captureStatus', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.TankNameItem('tankName', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.DamageItem('damage', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.EventPointsItem('matter', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.EventPointsLeftItem('matterOnTank', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.KillsItem('kills', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.MissionsItem('missions', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.DeathReason('deathReason', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.MatterTooltip('matterTooltip', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.MatterOnTankTooltip('matterOnTankTooltip', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.DamageTooltip('damageTooltip', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.KillTooltip('killsTooltip', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.BackGroundItem('background', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.ArenaDateTimeItem('time', _RECORD.COMMON, 'arenaCreateTime'))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.EventRewardStatsBlock(_EVENT_REWARD_VO_META, 'reward', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.EventBattlesTeamStatsBlock(base.ListMeta(), 'players', _RECORD.VEHICLES))
