# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/battle_results/templates.py
from gui.battle_results.components import base
from battle_royale.gui.battle_results import components
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
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
 'arenaBonusType': 0,
 'hasPremium': False})
_PERSONAL_PLAYER_NAME_VO_META = base.PropertyMeta((('userName', '', 'userName'), ('clanAbbrev', '', 'clanAbbrev')))
_PERSONAL_PLAYER_NAME_VO_META.bind(components.PersonalPlayerNameBlock)
_VEHICLE_STATUS_BLOCK_VO_META = base.PropertyMeta((('killer', {}, 'killer'), ('vehicleState', -1, 'vehicleState'), ('isSelfDestroyer', False, 'isSelfDestroyer')))
_VEHICLE_STATUS_BLOCK_VO_META.bind(components.BattleRoyaleVehicleStatusBlock)
BR_COMMON_STATS_BLOCK = base.StatsBlock(_COMMON_VO_META, 'common')
BR_COMMON_STATS_BLOCK.addNextComponent(components.PersonalPlayerNameBlock(_PERSONAL_PLAYER_NAME_VO_META))
BR_COMMON_STATS_BLOCK.addNextComponent(components.BattleRoyaleArenaNameBlock('arenaStr'))
BR_COMMON_STATS_BLOCK.addNextComponent(components.ArenaBonusTypeNameBlock('arenaBonusType'))
BR_COMMON_STATS_BLOCK.addNextComponent(components.BattleRoyalePlayerPlaceBlock('playerPlace'))
BR_COMMON_STATS_BLOCK.addNextComponent(components.BattleRoyaleIsSquadModeBlock('isSquadMode'))
BR_COMMON_STATS_BLOCK.addNextComponent(components.BattleRoyaleVehicleStatusBlock(_VEHICLE_STATUS_BLOCK_VO_META, 'vehicleStatus', _RECORD.PERSONAL))
BR_COMMON_STATS_BLOCK.addNextComponent(components.BattleRoyaleVehiclesBlock(base.ListMeta(), 'playerVehicles', _RECORD.PERSONAL))
BR_COMMON_STATS_BLOCK.addNextComponent(components.BattleRoyaleIsPremiumBlock('hasPremium'))
_PERSONAL_VO_META = base.DictMeta({'financialBalance': {},
 'financialBalancePrem': {},
 'stats': [],
 'rewards': {},
 'battlePass': {}})
_PERSONAL_VEHICLE_VO_META = base.PropertyMeta((('vehicleName', '', 'vehicleName'), ('vehicleType', '', 'vehicleType'), ('isObserver', '', 'isObserver')))
_PERSONAL_VEHICLE_VO_META.bind(components.BattleRoyalePersonalVehicleBlock)
_FINANCIAL_BLOCK_VO_META = base.PropertyMeta((('credits', 0, 'credits'),
 ('xp', 0, 'xp'),
 ('crystal', 0, 'crystal'),
 ('brcoin', 0, 'brcoin')))
_FINANCIAL_BLOCK_VO_META.bind(components.BattleRoyaleFinancialBlock)
_FINANCIAL_PREM_BLOCK_VO_META = base.PropertyMeta((('credits', 0, 'credits'),
 ('xp', 0, 'xp'),
 ('crystal', 0, 'crystal'),
 ('brcoin', 0, 'brcoin')))
_FINANCIAL_PREM_BLOCK_VO_META.bind(components.BattleRoyaleFinancialPremBlock)
_STAT_ITEM_VO_META = base.PropertyMeta((('type', '', 'type'),
 ('value', 0, 'value'),
 ('maxValue', 0, 'maxValue'),
 ('wreathImage', R.invalid(), 'wreathImage')))
_STAT_ITEM_VO_META.bind(components.BattleRoyaleStatsItemBlock)
_BATTLE_PASS_VO_META = base.PropertyMeta((('currentLevel', 1, 'currentLevel'),
 ('maxPoints', 0, 'maxPoints'),
 ('earnedPoints', 0, 'earnedPoints'),
 ('currentLevelPoints', 0, 'currentLevelPoints'),
 ('isDone', 0, 'isDone'),
 ('hasBattlePass', 0, 'hasBattlePass'),
 ('battlePassComplete', 0, 'battlePassComplete'),
 ('chapterID', 0, 'chapterID'),
 ('pointsTotal', 0, 'pointsTotal'),
 ('bpTopPoints', 0, 'bpTopPoints'),
 ('pointsAux', 0, 'pointsAux'),
 ('availablePoints', 0, 'availablePoints')))
_BATTLE_PASS_VO_META.bind(components.BattlePassBlock)
_REWARDS_VO_META = base.PropertyMeta((('achievements', [], 'achievements'),
 ('bonuses', [], 'bonuses'),
 ('completedQuestsCount', 0, 'completedQuestsCount'),
 ('completedQuests', {}, 'completedQuests'),
 ('brAwardTokens', {}, 'brAwardTokens')))
_REWARDS_VO_META.bind(components.BattleRoyaleRewardsBlock)
BR_PERSONAL_STATS_BLOCK = base.StatsBlock(_PERSONAL_VO_META, 'personal')
BR_PERSONAL_STATS_BLOCK.addNextComponent(components.BattleRoyaleFinancialBlock(_FINANCIAL_BLOCK_VO_META, 'financialBalance'))
BR_PERSONAL_STATS_BLOCK.addNextComponent(components.BattleRoyaleFinancialPremBlock(_FINANCIAL_PREM_BLOCK_VO_META, 'financialBalancePrem'))
BR_PERSONAL_STATS_BLOCK.addNextComponent(components.BattleRoyaleStatsBlock(base.ListMeta(), 'stats'))
BR_PERSONAL_STATS_BLOCK.addNextComponent(components.BattleRoyaleRewardsBlock(_REWARDS_VO_META, 'rewards'))
BR_PERSONAL_STATS_BLOCK.addNextComponent(components.BattlePassBlock(_BATTLE_PASS_VO_META, 'battlePass', _RECORD.PERSONAL))
TEAM_ITEM_VO_META = base.PropertyMeta((('isPersonal', False, 'isPersonal'),
 ('isPersonalSquad', False, 'isPersonalSquad'),
 ('squadIdx', 0, 'squadIdx'),
 ('place', 0, 'place'),
 ('userName', '', 'userName'),
 ('hiddenName', '', 'hiddenName'),
 ('clanAbbrev', '', 'clanAbbrev'),
 ('vehicleName', '', 'vehicleName'),
 ('vehicleType', '', 'vehicleType'),
 ('achievedLevel', 0, 'achievedLevel'),
 ('damage', 0, 'damage'),
 ('kills', 0, 'kills'),
 ('databaseID', 0, 'databaseID'),
 ('prebattleID', 0, 'prebattleID')))
TEAM_ITEM_VO_META.bind(components.BattleRoyalePlayerBlock)
BR_TEAM_STATS_BLOCK = components.BattleRoyaleTeamStatsBlock(base.ListMeta(), 'leaderboard', _RECORD.VEHICLES)
