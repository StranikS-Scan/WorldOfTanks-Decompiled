# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/battle_results/templates.py
from gui.battle_results.components import base
from gui.battle_results.components.details import GainCreditsValueInBattleItem
from gui.battle_results.components.progress import QuestsProgressBlock
from gui.battle_results.templates import regular
from last_stand.gui.battle_results import components as ex
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
LS_TOTAL_VO_META = base.DictMeta({'common': {},
 'phase': 0,
 'phasesCount': 0,
 'players': [],
 'quests': None,
 'rewards': {},
 'prevBestMissionsCount': 0,
 'time': -1,
 'completedDifficultyMissions': []})
LS_TEAM_ITEM_VO_META = base.PropertyMeta((('playerDBID', 0, 'playerDBID'),
 ('playerName', '', 'playerName'),
 ('vehicleName', '', 'vehicleName'),
 ('vehicleShortName', '', 'vehicleShortName'),
 ('vehicleIsIGR', '', 'vehicleIsIGR'),
 ('vehicleType', '', 'vehicleType'),
 ('vehicleCD', 0, 'vehicleCD'),
 ('vehicleLvl', -1, 'vehicleLvl'),
 ('clanAbbrev', '', 'clanAbbrev'),
 ('artefactKeys', 0, 'artefactKeys'),
 ('isPlayer', False, 'isPlayer'),
 ('squadID', 0, 'squadID'),
 ('isOwnSquad', False, 'isOwnSquad'),
 ('killerName', '', 'killerName'),
 ('deathReason', -1, 'deathReason'),
 ('kills', 0, 'kills'),
 ('damageDealt', 0, 'damageDealt'),
 ('badgeID', 0, 'badgeID'),
 ('badgeSuffixID', 0, 'badgeSuffixID'),
 ('respawnsCount', 0, 'respawnsCount'),
 ('hasPenalties', False, 'hasPenalties')))
LS_TEAM_ITEM_VO_META.bind(ex.LSVehicleStatsBlock)
LS_TOTAL_RESULTS_BLOCK = base.StatsBlock(LS_TOTAL_VO_META, 'lsVictoryData')
LS_PERSONAL_REWARDS_VO_META = base.DictMeta({'credits': 0,
 'effectivenessKeys': 0})
LS_PERSONAL_REWARDS_BLOCK = base.StatsBlock(LS_PERSONAL_REWARDS_VO_META, 'rewards')
LS_PERSONAL_REWARDS_BLOCK.addNextComponent(GainCreditsValueInBattleItem('credits', _RECORD.PERSONAL))
LS_PERSONAL_REWARDS_BLOCK.addNextComponent(ex.LSEffectivenessArtefactKeysItem('effectivenessKeys', _RECORD.PERSONAL))
LS_BATTLE_COMMON_STATS_BLOCK = regular.REGULAR_COMMON_STATS_BLOCK.clone(7)
regular.FINISH_RESULT_VO_META.bind(ex.LSBattleFinishResultBlock)
LS_TOTAL_RESULTS_BLOCK.addNextComponent(LS_BATTLE_COMMON_STATS_BLOCK)
LS_BATTLE_COMMON_STATS_BLOCK.addComponent(7, ex.LSBattleFinishResultBlock())
LS_TOTAL_RESULTS_BLOCK.addNextComponent(ex.LSPrevBestMissionsCountItem('prevBestMissionsCount', _RECORD.PERSONAL))
LS_TOTAL_RESULTS_BLOCK.addNextComponent(ex.LSTimeItem('time', _RECORD.COMMON, 'duration'))
LS_TOTAL_RESULTS_BLOCK.addNextComponent(ex.LSCompletedDifficultyMissions('completedDifficultyMissions', _RECORD.PERSONAL))
LS_TOTAL_RESULTS_BLOCK.addNextComponent(ex.LSPhaseItem('phase', _RECORD.PERSONAL))
LS_TOTAL_RESULTS_BLOCK.addNextComponent(ex.LSPhasesCountItem('phasesCount', _RECORD.PERSONAL))
LS_TOTAL_RESULTS_BLOCK.addNextComponent(ex.LSBattlesTeamStatsBlock(base.ListMeta(), 'players', _RECORD.VEHICLES))
LS_TOTAL_RESULTS_BLOCK.addNextComponent(QuestsProgressBlock(base.ListMeta(), 'quests', _RECORD.PERSONAL))
LS_TOTAL_RESULTS_BLOCK.addNextComponent(LS_PERSONAL_REWARDS_BLOCK)
