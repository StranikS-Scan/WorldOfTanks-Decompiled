# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/team/team_stats_packer.py
import typing
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as _CAPS
from gui.battle_results import stored_sorting
from gui.battle_results.presenters.packers.interfaces import IBattleResultsPacker
from gui.battle_results.presenters.packers.team.statistics_packer import Statistics
from gui.battle_results.presenters.packers.user_info import PlayerInfo
from gui.impl.gen.view_models.views.lobby.battle_results.player_model import PlayerModel
from gui.impl.gen.view_models.views.lobby.battle_results.team_stats_model import ColumnType, SortingOrder
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.system_factory import collectBattleResultsStatsSorting
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.battle_results.stats_ctrl import BattleResults
    from gui.battle_results.reusable import _ReusableInfo
    from gui.battle_results.reusable.shared import VehicleSummarizeInfo
    from gui.impl.gen.view_models.views.lobby.battle_results.stats_efficiency_model import StatsEfficiencyModel
    from gui.impl.gen.view_models.views.lobby.battle_results.team_stats_model import TeamStatsModel
_VehicleTags = (VEHICLE_TAGS.PREMIUM_IGR,)

class TeamStats(IBattleResultsPacker):
    _STATS_VALUES_COLUMNS = {ColumnType.DAMAGE.value: None,
     ColumnType.FRAG.value: None,
     ColumnType.XP.value: lambda reusable: reusable.common.checkBonusCaps(_CAPS.XP)}
    _SORTING_PRIORITIES = ()

    @classmethod
    def packModel(cls, model, battleResults):
        allies, enemies = battleResults.reusable.getBiDirectionTeamsIterator(battleResults.results['vehicles'])
        cls._packTeam(model.getAllies(), allies, battleResults)
        cls._packTeam(model.getEnemies(), enemies, battleResults)
        cls._packShownColumns(model.getShownValueColumns(), battleResults)
        cls.__packSortingParams(model, battleResults)

    @classmethod
    def _getAlternativeSortingParams(cls, reusable):
        for column, sortingOrder in cls._SORTING_PRIORITIES:
            condition = cls._STATS_VALUES_COLUMNS.get(column)
            if condition is None or condition(reusable):
                return (column, sortingOrder)

        return (ColumnType.VEHICLE.value, SortingOrder.DESC.value)

    @classmethod
    def _packEfficiency(cls, efficiencyModel, summarizeInfo):
        efficiencyModel.setDamageDealt(summarizeInfo.damageDealt)
        efficiencyModel.setKills(summarizeInfo.kills)
        efficiencyModel.setEarnedXp(summarizeInfo.xp)

    @classmethod
    def _packPlayer(cls, playerModel, summarizeInfo, battleResults):
        PlayerInfo.packModel(playerModel, battleResults, summarizeInfo)
        Statistics.packModel(playerModel.getDetailedStatistics(), summarizeInfo, battleResults)
        cls._packEfficiency(playerModel.efficiencyValues, summarizeInfo)
        fillVehicleModel(playerModel.vehicle, summarizeInfo.vehicle, _VehicleTags)

    @classmethod
    def _packShownColumns(cls, columnsModel, battleResults):
        reusable = battleResults.reusable
        columnsModel.clear()
        for columnType, condition in cls._STATS_VALUES_COLUMNS.items():
            if condition is None or condition(reusable):
                columnsModel.addString(columnType)

        columnsModel.invalidate()
        return

    @classmethod
    def _packTeam(cls, teamModel, teamData, battleResults):
        teamModel.clear()
        for idx, summarizeInfo in enumerate(teamData):
            playerModel = PlayerModel()
            playerModel.setPlayerIndex(idx)
            cls._packPlayer(playerModel, summarizeInfo, battleResults)
            teamModel.addViewModel(playerModel)

        teamModel.invalidate()

    @classmethod
    def __packSortingParams(cls, model, battleResults):
        reusable = battleResults.reusable
        bonusType = reusable.common.arenaBonusType
        sortingKey = collectBattleResultsStatsSorting().get(bonusType)
        column, sortingOrder = stored_sorting.readStatsSorting(sortingKey)
        condition = cls._STATS_VALUES_COLUMNS.get(column)
        if condition is not None and not condition(reusable):
            column, sortingOrder = cls._getAlternativeSortingParams(reusable)
        model.setSortingColumn(ColumnType(column))
        model.setSortingOrder(SortingOrder(sortingOrder))
        return
