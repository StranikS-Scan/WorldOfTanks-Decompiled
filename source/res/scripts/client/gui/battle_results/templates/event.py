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
 'players': [],
 'matterTooltip': {},
 'damageTooltip': {},
 'killsTooltip': {},
 'blockedTooltip': {},
 'keysTooltip': {},
 'medalsTooltip': {},
 'platoonTooltip': {},
 'tankTooltip': {},
 'nameTooltip': {},
 'background': '',
 'time': '',
 'hw21Rewards': {},
 'teamCombinedStats': {},
 'tankIcon': '',
 'isWin': False,
 'difficultyString': '',
 'difficultyIcon': '',
 'playerName': '',
 'playerClan': '',
 'hw21NarrativeInfo': None})
_EVENT_PLAYER_INFO_VO_META_TUPLE = regular.TEAM_ITEM_VO_META_TUPLE + (('matter', 0, 'matter'),
 ('blocked', 0, 'damageBlockedByArmor'),
 ('tankType', 0, 'tankType'),
 ('banStatus', '', 'banStatus'),
 ('banStatusTooltip', '', 'banStatusTooltip'),
 ('teamFightPlace', -1, 'teamFightPlace'),
 ('rewardBoxKeys', 0, 'rewardBoxKeys'),
 ('medals', [], 'medals'))
_EVENT_PLAYER_INFO_VO_META = base.PropertyMeta(_EVENT_PLAYER_INFO_VO_META_TUPLE)
_EVENT_PLAYER_INFO_VO_META.bind(event.EventVehicleStatsBlock)
EVENT_BATTLE_COMMON_STATS_BLOCK = regular.REGULAR_COMMON_STATS_BLOCK.clone()
EVENT_TOTAL_RESULTS_BLOCK = base.StatsBlock(EVENT_TOTAL_VO_META, 'victoryData')
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(EVENT_BATTLE_COMMON_STATS_BLOCK)
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.CaptureStatusItem('captureStatus', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.TankNameItem('tankName', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.TankTypeItem('tankType', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.MatterTooltip('matterTooltip', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.DamageTooltip('damageTooltip', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.KillTooltip('killsTooltip', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.DamageBlockedByArmorTooltip('blockedTooltip', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.RewardBoxKeysTooltip('keysTooltip', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.MedalsTooltip('medalsTooltip', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.BackGroundItem('background', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.HW21RewardsItem('hw21Rewards', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.ArenaDateTimeItem('time', _RECORD.COMMON, 'arenaCreateTime'))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.EventCombinedTeamStatBlock('teamCombinedStats', _RECORD.VEHICLES))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.VehicleIconItem('tankIcon', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.IsWinItem('isWin', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.DifficultyTextItem('difficultyString', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.DifficultyIconItem('difficultyIcon', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.PlayerNameItem('playerName', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.PlayerClanItem('playerClan', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.PlatoonTooltip('platoonTooltip', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.NameTooltip('nameTooltip', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.TankTooltip('tankTooltip', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.EventBattlesTeamStatsBlock(base.ListMeta(), 'players', _RECORD.VEHICLES))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.HW21NarrativeInfoItem('hw21NarrativeInfo', _RECORD.PERSONAL))
