# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/templates/event.py
from gui.battle_results.templates import regular
from gui.battle_results.components import base
from gui.battle_results.components import event
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
EVENT_TOTAL_VO_META = base.DictMeta({'common': {},
 'captureStatus': {},
 'tankStatus': {},
 'gameStatus': {},
 'damage': 0,
 'kills': 0,
 'points': {},
 'players': [],
 'damageTooltip': {},
 'killsTooltip': {},
 'assistTooltip': {},
 'armorTooltip': {},
 'alliesDamageTooltip': {},
 'alliesKillsTooltip': {},
 'alliesAssistTooltip': {},
 'alliesArmorTooltip': {},
 'alliesVehiclesTooltip': {},
 'objectives': {},
 'background': '',
 'assist': 0,
 'armor': 0,
 'personalMission': [],
 'crewMission': []})
_EVENT_PLAYER_INFO_VO_META_TUPLE = regular.TEAM_ITEM_VO_META_TUPLE + (('tankType', '', 'tankType'),
 ('generalLevel', 0, 'generalLevel'),
 ('assist', 0, 'assist'),
 ('armor', 0, 'armor'))
_EVENT_PLAYER_INFO_VO_META = base.PropertyMeta(_EVENT_PLAYER_INFO_VO_META_TUPLE)
_EVENT_PLAYER_INFO_VO_META.bind(event.EventVehicleStatsBlock)
EVENT_BATTLE_COMMON_STATS_BLOCK = regular.REGULAR_COMMON_STATS_BLOCK.clone()
EVENT_TOTAL_RESULTS_BLOCK = base.StatsBlock(EVENT_TOTAL_VO_META, 'victoryData')
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(EVENT_BATTLE_COMMON_STATS_BLOCK)
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.ReasonItem('captureStatus', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.TankStatusItem('tankStatus', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.GameStatusItem('gameStatus', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.DamageItem('damage', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.KillsItem('kills', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.PointsItem('points', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.DamageTooltip('damageTooltip', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.KillTooltip('killsTooltip', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.AssistTooltip('assistTooltip', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.ArmorTooltip('armorTooltip', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.AlliesDamageTooltip('alliesDamageTooltip', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.AlliesKillTooltip('alliesKillsTooltip', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.AlliesAssistTooltip('alliesAssistTooltip', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.AlliesArmorTooltip('alliesArmorTooltip', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.AlliesVehiclesTooltip('alliesVehiclesTooltip', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.Objectives('objectives', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.BackGroundItem('background', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.AssistItem('assist', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.ArmorItem('armor', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.PersonalMissionItem('personalMission', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.CrewMissionItem('crewMission', _RECORD.PERSONAL))
EVENT_TOTAL_RESULTS_BLOCK.addNextComponent(event.EventBattlesTeamStatsBlock(base.ListMeta(), 'players', _RECORD.VEHICLES))
