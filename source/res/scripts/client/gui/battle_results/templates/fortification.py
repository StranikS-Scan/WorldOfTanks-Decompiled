# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/templates/fortification.py
from gui.battle_results.components import base
from gui.battle_results.components import common
from gui.battle_results.components import details
from gui.battle_results.components import personal
from gui.battle_results.components import shared
from gui.battle_results.components import vehicles
from gui.battle_results.templates import regular
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
regular.FINISH_RESULT_VO_META.bind(common.FortBattleFinishResultBlock)
SORTIE_BATTLE_COMMON_STATS_BLOCK = regular.REGULAR_COMMON_STATS_BLOCK.clone(0, 13)
SORTIE_BATTLE_COMMON_STATS_BLOCK.addComponent(0, shared.SortieSortingBlock())
SORTIE_BATTLE_COMMON_STATS_BLOCK.addComponent(13, common.SortieTeamsUiVisibility('uiVisibility'))
SORTIE_BATTLE_COMMON_STATS_BLOCK.addNextComponent(common.ClansInfoBlock(regular.CLANS_COMMON_VO_META, 'clans'))
SORTIE_BATTLE_COMMON_STATS_BLOCK.addNextComponent(common.TotalFortResourceItem('totalFortResourceStr'))
SORTIE_BATTLE_COMMON_STATS_BLOCK.addNextComponent(common.TotalInfluencePointsItem('totalInfluenceStr'))
SORTIE_PERSONAL_STATS_BLOCK = regular.REGULAR_PERSONAL_STATS_BLOCK.clone()
SORTIE_PERSONAL_STATS_BLOCK.addComponent(17, details.GainFortResourceInBattleItem('fortResourceTotal'))
SORTIE_PERSONAL_STATS_BLOCK.addComponent(18, personal.PlayerNoClanFlag('isLegionnaire'))
SORTIE_PERSONAL_STATS_BLOCK.addComponent(19, details.BaseFortResourcesBlock(base.ListMeta(), 'resValues', _RECORD.PERSONAL))
SORTIE_PERSONAL_STATS_BLOCK.addComponent(20, details.PremiumFortResourcesBlock(base.ListMeta(), 'resPremValues', _RECORD.PERSONAL))
SORTIE_PERSONAL_STATS_BLOCK.addComponent(21, details.FortResourceDetailsBlock(base.ListMeta(), 'resourceData', _RECORD.PERSONAL))
regular.TEAM_ITEM_VO_META.bind(vehicles.SortieVehicleStatsBlock)
SORTIE_TEAMS_STATS_BLOCK = vehicles.TwoTeamsStatsBlock(regular.TEAMS_VO_META.clone(), '', _RECORD.VEHICLES)
SORTIE_TEAMS_STATS_BLOCK.addNextComponent(vehicles.SortieTeamStatsBlock(meta=base.ListMeta(), field='team1'))
SORTIE_TEAMS_STATS_BLOCK.addNextComponent(vehicles.SortieTeamStatsBlock(meta=base.ListMeta(), field='team2'))
FORT_BATTLE_COMMON_STATS_BLOCK = regular.REGULAR_COMMON_STATS_BLOCK.clone(7)
FORT_BATTLE_COMMON_STATS_BLOCK.addComponent(7, common.FortBattleFinishResultBlock(None, '', _RECORD.PERSONAL, _RECORD.PERSONAL_AVATAR))
FORT_BATTLE_COMMON_STATS_BLOCK.addNextComponent(common.ClansInfoBlock(regular.CLANS_COMMON_VO_META, 'clans'))
regular.FINISH_RESULT_VO_META.bind(common.StrongholdBattleFinishResultBlock)
STRONGHOLD_BATTLE_COMMON_STATS_BLOCK = regular.REGULAR_COMMON_STATS_BLOCK.clone()
STRONGHOLD_BATTLE_COMMON_STATS_BLOCK.addNextComponent(common.StrongholdBattleFinishResultBlock(None, '', _RECORD.PERSONAL, _RECORD.PERSONAL_AVATAR))
