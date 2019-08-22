# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/templates/battle_royale.py
from gui.Scaleform.genConsts.BATTLEROYALE_ALIASES import BATTLEROYALE_ALIASES
from gui.battle_results.components import base, vehicles, personal, common, details
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
from gui.impl import backport
from gui.impl.gen import R
BR_TOTAL_VO_META = base.DictMeta({'tabInfo': [],
 'personal': {},
 'common': {},
 'teams': []})
_BR_TABS_VO_META = base.ListMeta([{'id': BATTLEROYALE_ALIASES.BATTLE_ROYALE_SUMMARY_RESULTS_CMP,
  'label': backport.text(R.strings.battle_royale.hangarResults.btns.summary()),
  'selected': True,
  'enabled': True}, {'id': BATTLEROYALE_ALIASES.BATTLE_ROYALE_SCORE_RESULTS_CMP,
  'label': backport.text(R.strings.battle_royale.hangarResults.btns.score()),
  'selected': False,
  'enabled': True}])
BR_TABS_BLOCK = base.StatsBlock(_BR_TABS_VO_META, 'tabInfo')
TEAM_ITEM_VO_META = base.PropertyMeta((('isPersonal', False, 'isPersonal'),
 ('kills', 0, 'kills'),
 ('team', 0, 'team'),
 ('isPersonalSquad', False, 'isPersonalSquad'),
 ('place', 0, 'place'),
 ('index', 0, 'index'),
 ('nameLabel', '', 'nameLabel'),
 ('isPrematureLeave', False, 'isPrematureLeave')))
TEAM_ITEM_VO_META.bind(vehicles.BattleRoyaleVehicleStatsBlock)
_COMMON_VO_META = base.DictMeta({'playerNameStr': '',
 'playerFullNameStr': '',
 'clanNameStr': '',
 'regionNameStr': '',
 'isInSquad': False})
_PERSONAL_PLAYER_NAME_VO_META = base.PropertyMeta((('playerNameStr', '', 'nameLabel'),
 ('playerFullNameStr', '', 'fullNameLabel'),
 ('clanNameStr', '', 'clanLabel'),
 ('regionNameStr', '', 'regionLabel')))
_PERSONAL_PLAYER_NAME_VO_META.bind(personal.PersonalPlayerNameBlock)
BR_COMMON_STATS_BLOCK = base.StatsBlock(_COMMON_VO_META, 'common')
BR_COMMON_STATS_BLOCK.addNextComponent(personal.PersonalPlayerNameBlock())
BR_COMMON_STATS_BLOCK.addNextComponent(common.IsInSquadBattleRoyaleFlag('isInSquad'))
_PERSONAL_VO_META = base.DictMeta({'credits': 0,
 'xp': 0,
 'crystal': 0,
 'efficiency': {},
 'eventProgression': {}})
_TOTAL_EFFICIENCY_HEADER_META = base.PropertyMeta((('accPlace', 0, 'accPlace'),
 ('chevrons', 0, 'chevrons'),
 ('kills', 0, 'kills'),
 ('squadKills', 0, 'squadKills'),
 ('damageDealt', 0, 'damageDealt'),
 ('criticalDamages', 0, 'criticalDamages'),
 ('damageBlockedByArmor', 0, 'damageBlockedByArmor')))
_TOTAL_EFFICIENCY_HEADER_META.bind(personal.BRTotalEfficiencyDetailsHeader)
_EVENT_PROGRESSION_VO_META = base.PropertyMeta((('accBRTitle', (0, 0), 'accBRTitle'),
 ('maxBRTitle', (0, 0), 'maxBRTitle'),
 ('lastBRTitle', (0, 0), 'lastBRTitle'),
 ('brPointsChanges', 0, 'brPointsChanges'),
 ('questProgress', [], 'questProgress')))
_EVENT_PROGRESSION_VO_META.bind(personal.BREventProgressionBlock)
BR_PERSONAL_STATS_BLOCK = base.StatsBlock(_PERSONAL_VO_META, 'personal')
BR_PERSONAL_STATS_BLOCK.addNextComponent(personal.BRTotalEfficiencyDetailsHeader(_TOTAL_EFFICIENCY_HEADER_META, 'efficiency'))
BR_PERSONAL_STATS_BLOCK.addNextComponent(personal.BREventProgressionBlock(_EVENT_PROGRESSION_VO_META, 'eventProgression', _RECORD.PERSONAL))
BR_PERSONAL_STATS_BLOCK.addNextComponent(details.BRCredits('credits', _RECORD.PERSONAL))
BR_PERSONAL_STATS_BLOCK.addNextComponent(details.BRXp('xp', _RECORD.PERSONAL))
BR_PERSONAL_STATS_BLOCK.addNextComponent(details.BRCrystal('crystal', _RECORD.PERSONAL))
BR_TEAM_STATS_BLOCK = vehicles.BattleRoyaleTeamStatsBlock(base.ListMeta(), 'teams', _RECORD.VEHICLES)
