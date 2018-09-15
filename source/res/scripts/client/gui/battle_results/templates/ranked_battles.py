# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/templates/ranked_battles.py
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.battle_results.components import base, vehicles, common
from gui.battle_results.templates import regular
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
RANKED_COMMON_STATS_BLOCK = regular.REGULAR_COMMON_STATS_BLOCK.clone()
_RANK_COMMON_VO_META = base.PropertyMeta((('state', '', 'state'),
 ('linkage', '', 'linkage'),
 ('title', '', 'title'),
 ('description', '', 'description'),
 ('topIcon', '', 'topIcon'),
 ('icon', '', 'rankIcon')))
_RANK_COMMON_VO_META.bind(common.RankChangesBlock)
RANKED_COMMON_STATS_BLOCK.addNextComponent(common.RankChangesBlock(_RANK_COMMON_VO_META, 'rank'))
regular.TEAM_ITEM_VO_META.bind(vehicles.RankedBattlesVehicleStatsBlock)
RANKED_TEAMS_STATS_BLOCK = vehicles.TwoTeamsStatsBlock(regular.TEAMS_VO_META.clone(), '', _RECORD.VEHICLES)
RANKED_TEAMS_STATS_BLOCK.addNextComponent(vehicles.RankedBattlesTeamStatsBlock(meta=base.ListMeta(), field='team1'))
RANKED_TEAMS_STATS_BLOCK.addNextComponent(vehicles.RankedBattlesTeamStatsBlock(meta=base.ListMeta(), field='team2'))
RANKED_RESULTS_BLOCK = base.DictMeta({'title': '',
 'readyBtn': RANKED_BATTLES.BATTLERESULT_YES,
 'readyBtnVisible': True,
 'mainBackground': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_BG_RANK_BLUR,
 'leftData': {},
 'rightData': {}})
RANKED_RESULTS_BLOCK_TITLE = common.RankedResultsBlockTitle('title')
_RANKED_RESULTS_TEAMS_VO_META = base.DictMeta({'leftData': {},
 'rightData': {}})
_RANKED_RESULTS_TEAM_DATA_VO_META = base.PropertyMeta((('title', '', 'title'), ('titleAlpha', 1.0, 'titleAlpha'), ('tops', [], 'teamList')))
_RANKED_RESULTS_TEAM_DATA_VO_META.bind(vehicles.RankedResultsTeamDataStatsBlock)
_RANKED_RESULTS_TEAM_PART_DATA_VO_META = base.PropertyMeta((('listData', [], 'listData'),
 ('backgroundType', '', 'backgroundType'),
 ('backgroundBlink', False, 'backgroundBlink'),
 ('topIcon', '', 'icon'),
 ('topCapacity', 0, 'capacity'),
 ('isColorBlind', False, 'isColorBlind')))
_RANKED_RESULTS_TEAM_PART_DATA_VO_META.bind(vehicles.RankedResultsTeamPartDataStatsBlock)
RANKED_RESULTS_TEAMS_STATS_BLOCK = vehicles.RankedResultsTeamStatsBlock(_RANKED_RESULTS_TEAMS_VO_META.clone(), '', _RECORD.VEHICLES)
RANKED_RESULTS_TEAMS_STATS_BLOCK.addNextComponent(vehicles.RankedResultsTeamDataStatsBlock(field='leftData'))
RANKED_RESULTS_TEAMS_STATS_BLOCK.addNextComponent(vehicles.RankedResultsTeamDataStatsBlock(field='rightData'))
_RANKED_RESULTS_LIST_ITEM_VO_META = base.PropertyMeta((('nickName', '', 'nickName'),
 ('nickNameHuge', '', 'nickNameHuge'),
 ('points', '', 'points'),
 ('pointsHuge', '', 'pointsHuge'),
 ('selected', False, 'selected'),
 ('standoff', 0, 'standoff')))
_RANKED_RESULTS_LIST_ITEM_VO_META.bind(vehicles.RankedResultsListItemStatsBlock)
