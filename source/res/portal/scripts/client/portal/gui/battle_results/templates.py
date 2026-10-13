# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/battle_results/templates.py
from gui.battle_results.components import base
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
from gui.impl.gen import R
from portal.gui.battle_results import components as ex
from portal.gui.battle_results.components import StatsItemBlock, StatsBlock
PORTAL_TOTAL_VO_META = base.DictMeta({'results': {},
 'reusable': {},
 'common': {},
 'personal': {},
 'leaderboard': {},
 'progressionTokens': 0,
 'vehicleExperience': 0,
 'portalBattleLevel': 0,
 'portalWaveCount': 0,
 'portalCurrentWave': 0})
PORTAL_TOTAL_RESULTS_BLOCK = base.StatsBlock(PORTAL_TOTAL_VO_META, 'victoryData')
PORTAL_TOTAL_RESULTS_BLOCK.addNextComponent(ex.ProgressionTokensItem('progressionTokens', _RECORD.PERSONAL))
PORTAL_TOTAL_RESULTS_BLOCK.addNextComponent(ex.VehicleExperienceItem('vehicleExperience', _RECORD.PERSONAL))
PORTAL_TOTAL_RESULTS_BLOCK.addNextComponent(ex.BattleLevelItem('portalBattleLevel', _RECORD.PERSONAL))
PORTAL_TOTAL_RESULTS_BLOCK.addNextComponent(ex.CurrentWaveItem('portalCurrentWave', _RECORD.PERSONAL))
PORTAL_TOTAL_RESULTS_BLOCK.addNextComponent(ex.WaveCountItem('portalWaveCount', _RECORD.PERSONAL))
STAT_ITEM_VO_META = base.PropertyMeta((('type', '', 'type'), ('value', 0, 'value'), ('wreathImage', R.invalid(), 'wreathImage')))
STAT_ITEM_VO_META.bind(StatsItemBlock)
PERSONAL_VO_META = base.DictMeta({'stats': []})
PERSONAL_STATS_BLOCK = base.StatsBlock(PERSONAL_VO_META, 'personal')
PERSONAL_STATS_BLOCK.addNextComponent(StatsBlock(base.ListMeta(), 'stats'))
TEAM_ITEM_VO_META = base.PropertyMeta((('isPersonal', False, 'isPersonal'),
 ('isSquadMode', False, 'isSquadMode'),
 ('squadIdx', 0, 'squadIdx'),
 ('place', 0, 'place'),
 ('userName', '', 'userName'),
 ('hiddenName', '', 'hiddenName'),
 ('clanAbbrev', '', 'clanAbbrev'),
 ('vehicleName', '', 'vehicleName'),
 ('vehicleType', '', 'vehicleType'),
 ('damage', 0, 'damage'),
 ('damageBlocked', 0, 'damageBlocked'),
 ('kills', 0, 'kills'),
 ('databaseID', 0, 'databaseID')))
TEAM_ITEM_VO_META.bind(ex.PlayerBlock)
TEAM_STATS_BLOCK = ex.TeamStatsBlock(base.ListMeta(), 'leaderboard', _RECORD.VEHICLES)
