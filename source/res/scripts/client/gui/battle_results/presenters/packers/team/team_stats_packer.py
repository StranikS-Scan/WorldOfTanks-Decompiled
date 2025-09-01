# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/team/team_stats_packer.py
import typing
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as _CAPS
from frameworks.wulf.view.array import fillViewModelsArray
from gui.battle_results import stored_sorting
from gui.battle_results.pbs_helpers.common import getTeamPlayerAchievements
from gui.battle_results.presenters.packers.interfaces import IBattleResultsPacker
from gui.battle_results.presenters.packers.team.statistics_packer import Statistics
from gui.battle_results.presenters.packers.user_info import PlayerInfo
from gui.impl.gen.view_models.views.lobby.battle_results.player_model import PlayerModel
from gui.impl.gen.view_models.views.lobby.battle_results.team_stats_column_types import TeamStatsColumnTypes
from gui.impl.gen.view_models.views.lobby.battle_results.team_stats_model import TeamStatsModel, SortingOrder
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.system_factory import collectBattleResultsStatsSorting
from gui.impl.gen.view_models.views.lobby.battle_results.postbattle_achievement_model import PostbattleAchievementModel
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.battle_results.pbs_helpers.common import _AchievementData
    from gui.battle_results.reusable import _ReusableInfo
    from gui.battle_results.stats_ctrl import BattleResults
    from gui.battle_results.reusable.shared import VehicleSummarizeInfo
    from gui.impl.gen.view_models.views.lobby.battle_results.stats_efficiency_model import StatsEfficiencyModel
_VehicleTags = (VEHICLE_TAGS.PREMIUM_IGR,)

class TeamStats(IBattleResultsPacker):
    _PLAYER_MODEL_CLS = PlayerModel
    _PLAYER_INFO_PACKER = PlayerInfo
    _STATS_VALUES_COLUMNS = {TeamStatsColumnTypes.DAMAGE: None,
     TeamStatsColumnTypes.FRAG: None,
     TeamStatsColumnTypes.XP: lambda reusable: reusable.common.checkBonusCaps(_CAPS.XP)}
    _SORTING_PRIORITIES = ()

    @classmethod
    def packModel(cls, model, battleResults):
        allies, enemies = battleResults.reusable.getBiDirectionTeamsIterator(battleResults.results['vehicles'])
        cls._packTeam(model.getAllies(), allies, battleResults)
        cls._packTeam(model.getEnemies(), enemies, battleResults)
        cls._packShownColumns(model.getShownValueColumns(), battleResults)
        cls._packSortingParams(model, battleResults)

    @classmethod
    def packPlayer(cls, playerModel, summarizeInfo, battleResults):
        cls._PLAYER_INFO_PACKER.packModel(playerModel, battleResults, summarizeInfo)
        Statistics.packModel(playerModel.getDetailedStatistics(), summarizeInfo, battleResults)
        cls._packEfficiency(playerModel.efficiencyValues, summarizeInfo)
        fillVehicleModel(playerModel.vehicle, summarizeInfo.vehicle, _VehicleTags)

    @classmethod
    def _getAlternativeSortingParams(cls, reusable):
        for column, sortingOrder in cls._SORTING_PRIORITIES:
            condition = cls._STATS_VALUES_COLUMNS.get(column)
            if condition is None or condition(reusable):
                return (column, sortingOrder)

        return (TeamStatsColumnTypes.VEHICLE, SortingOrder.DESC.value)

    @classmethod
    def _packEfficiency(cls, efficiencyModel, summarizeInfo):
        efficiencyModel.setDamageDealt(summarizeInfo.damageDealt)
        efficiencyModel.setKills(summarizeInfo.kills)
        efficiencyModel.setEarnedXp(summarizeInfo.xp)

    @classmethod
    def _packSortingParams(cls, model, battleResults):
        reusable = battleResults.reusable
        bonusType = reusable.common.arenaBonusType
        sortingKey = collectBattleResultsStatsSorting().get(bonusType)
        column, sortingOrder = stored_sorting.readStatsSorting(sortingKey)
        condition = cls._STATS_VALUES_COLUMNS.get(column)
        if condition is not None and not condition(reusable):
            column, sortingOrder = cls._getAlternativeSortingParams(reusable)
        model.setSortingColumn(column)
        model.setSortingOrder(SortingOrder(sortingOrder))
        return

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
            playerModel = cls._PLAYER_MODEL_CLS()
            playerModel.setPlayerIndex(idx)
            cls.packPlayer(playerModel, summarizeInfo, battleResults)
            teamModel.addViewModel(playerModel)

        teamModel.invalidate()


class TeamAchievementsPacker(object):

    @classmethod
    def packModel(cls, playerAchievementsModel, summarizeInfo, battleResults):
        reusable = battleResults.reusable
        playerAchievements = getTeamPlayerAchievements(summarizeInfo, reusable)
        viewModels = [ cls.__setAchievementsResults(achievement) for achievement in playerAchievements ]
        fillViewModelsArray(viewModels, playerAchievementsModel)

    @classmethod
    def __setAchievementsResults(cls, achievement):
        achievementModel = PostbattleAchievementModel()
        achievementModel.setName(achievement.name)
        achievementModel.setIsEpic(achievement.isEpic)
        achievementModel.setIconName(achievement.iconName)
        achievementModel.setGroupID(achievement.groupID)
        achievementModel.setTooltipId(achievement.tooltipType)
        achievementModel.setTooltipArgs(achievement.tooltipArgs)
        return achievementModel
