# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/templates/battle_royale.py
from gui.battle_results.components import base, battle_royale
from gui.battle_results.br_constants import BattleResultsRecord as _RECORD
from gui.impl.gen import R
from gui.Scaleform.genConsts.BATTLEROYALE_ALIASES import BATTLEROYALE_ALIASES
BR_TOTAL_VO_META = base.DictMeta({'tabInfo': [],
 'personal': {},
 'common': {},
 'leaderboard': []})
_BR_TABS_VO_META = base.ListMeta([{'id': BATTLEROYALE_ALIASES.BATTLE_ROYALE_SUMMARY_RESULTS_CMP,
  'label': '',
  'selected': True,
  'enabled': True}, {'id': BATTLEROYALE_ALIASES.BATTLE_ROYALE_SCORE_RESULTS_CMP,
  'label': '',
  'selected': False,
  'enabled': True}])
BR_TABS_BLOCK = base.StatsBlock(_BR_TABS_VO_META, 'tabInfo')
_COMMON_VO_META = base.DictMeta({'arenaStr': '',
 'userName': '',
 'clanAbbrev': '',
 'playerVehicles': [],
 'playerPlace': 0,
 'isSquadMode': False,
 'vehicleStatus': {},
 'arenaBonusType': 0})
_PERSONAL_PLAYER_NAME_VO_META = base.PropertyMeta((('userName', '', 'userName'), ('clanAbbrev', '', 'clanAbbrev')))
_PERSONAL_PLAYER_NAME_VO_META.bind(battle_royale.PersonalPlayerNameBlock)
_VEHICLE_STATUS_BLOCK_VO_META = base.PropertyMeta((('killer', {}, 'killer'), ('vehicleState', -1, 'vehicleState'), ('isSelfDestroyer', False, 'isSelfDestroyer')))
_VEHICLE_STATUS_BLOCK_VO_META.bind(battle_royale.BattleRoyaleVehicleStatusBlock)
BR_COMMON_STATS_BLOCK = base.StatsBlock(_COMMON_VO_META, 'common')
BR_COMMON_STATS_BLOCK.addNextComponent(battle_royale.PersonalPlayerNameBlock(_PERSONAL_PLAYER_NAME_VO_META))
BR_COMMON_STATS_BLOCK.addNextComponent(battle_royale.BattleRoyaleArenaNameBlock('arenaStr'))
BR_COMMON_STATS_BLOCK.addNextComponent(battle_royale.ArenaBonusTypeNameBlock('arenaBonusType'))
BR_COMMON_STATS_BLOCK.addNextComponent(battle_royale.BattleRoyalePlayerPlaceBlock('playerPlace'))
BR_COMMON_STATS_BLOCK.addNextComponent(battle_royale.BattleRoyaleIsSquadModeBlock('isSquadMode'))
BR_COMMON_STATS_BLOCK.addNextComponent(battle_royale.BattleRoyaleVehicleStatusBlock(_VEHICLE_STATUS_BLOCK_VO_META, 'vehicleStatus', _RECORD.PERSONAL))
BR_COMMON_STATS_BLOCK.addNextComponent(battle_royale.BattleRoyaleVehiclesBlock(base.ListMeta(), 'playerVehicles', _RECORD.PERSONAL))
_PERSONAL_VO_META = base.DictMeta({'financialBalance': {},
 'stats': [],
 'rewards': {},
 'battlePass': {}})
_PERSONAL_VEHICLE_VO_META = base.PropertyMeta((('nationName', '', 'nationName'), ('vehicleName', '', 'vehicleName'), ('isObserver', '', 'isObserver')))
_PERSONAL_VEHICLE_VO_META.bind(battle_royale.BattleRoyalePersonalVehicleBlock)
_FINANCIAL_BLOCK_VO_META = base.PropertyMeta((('credits', 0, 'credits'), ('xp', 0, 'xp'), ('crystal', 0, 'crystal')))
_FINANCIAL_BLOCK_VO_META.bind(battle_royale.BattleRoyaleFinancialBlock)
_STAT_ITEM_VO_META = base.PropertyMeta((('type', '', 'type'),
 ('value', 0, 'value'),
 ('maxValue', 0, 'maxValue'),
 ('wreathImage', R.invalid(), 'wreathImage')))
_STAT_ITEM_VO_META.bind(battle_royale.BattleRoyaleStatsItemBlock)
_BATTLE_PASS_VO_META = base.PropertyMeta((('currentLevel', 1, 'currentLevel'),
 ('maxPoints', 0, 'maxPoints'),
 ('earnedPoints', 0, 'earnedPoints'),
 ('currentLevelPoints', 0, 'currentLevelPoints'),
 ('isDone', 0, 'isDone')))
_BATTLE_PASS_VO_META.bind(battle_royale.BattlePassBlock)
_REWARDS_VO_META = base.PropertyMeta((('achievements', [], 'achievements'),
 ('bonuses', [], 'bonuses'),
 ('completedQuestsCount', 0, 'completedQuestsCount'),
 ('completedQuests', {}, 'completedQuests')))
_REWARDS_VO_META.bind(battle_royale.BattleRoyaleRewardsBlock)
BR_PERSONAL_STATS_BLOCK = base.StatsBlock(_PERSONAL_VO_META, 'personal')
BR_PERSONAL_STATS_BLOCK.addNextComponent(battle_royale.BattleRoyaleFinancialBlock(_FINANCIAL_BLOCK_VO_META, 'financialBalance'))
BR_PERSONAL_STATS_BLOCK.addNextComponent(battle_royale.BattleRoyaleStatsBlock(base.ListMeta(), 'stats'))
BR_PERSONAL_STATS_BLOCK.addNextComponent(battle_royale.BattleRoyaleRewardsBlock(_REWARDS_VO_META, 'rewards'))
BR_PERSONAL_STATS_BLOCK.addNextComponent(battle_royale.BattlePassBlock(_BATTLE_PASS_VO_META, 'battlePass', _RECORD.PERSONAL))
TEAM_ITEM_VO_META = base.PropertyMeta((('isPersonal', False, 'isPersonal'),
 ('isPersonalSquad', False, 'isPersonalSquad'),
 ('squadIdx', 0, 'squadIdx'),
 ('place', 0, 'place'),
 ('userName', '', 'userName'),
 ('hiddenName', '', 'hiddenName'),
 ('clanAbbrev', '', 'clanAbbrev'),
 ('vehicleName', '', 'vehicleName'),
 ('nationName', '', 'nationName'),
 ('achievedLevel', 0, 'achievedLevel'),
 ('damage', 0, 'damage'),
 ('kills', 0, 'kills')))
TEAM_ITEM_VO_META.bind(battle_royale.BattleRoyalePlayerBlock)
BR_TEAM_STATS_BLOCK = battle_royale.BattleRoyaleTeamStatsBlock(base.ListMeta(), 'leaderboard', _RECORD.VEHICLES)
