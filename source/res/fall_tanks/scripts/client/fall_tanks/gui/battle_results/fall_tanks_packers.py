# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/battle_results/fall_tanks_packers.py
from __future__ import absolute_import
from gui.battle_results.presenters.packers.personal_efficiency import PersonalEfficiency
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_results.personal_efficiency_model import ValueType
from gui.impl.gen.view_models.views.lobby.battle_results.team_stats_model import SortingOrder
from gui.impl.gen.view_models.views.lobby.battle_results.team_stats_column_types import TeamStatsColumnTypes
from shared_utils import first
from fun_random.gui.battle_results.packers.fun_packers import FunRandomTeamStats, FunRandomBattleInfo
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_team_stats_column_types import FunTeamStatsColumnTypes
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_stats_efficiency_param_model import StatsValueType
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_battle_type import FunBattleType
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_player_model import FunPlayerModel
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_race_status import FunRaceStatus
from fall_tanks.gui.battle_results.fall_tanks_pbs_constants import FallTanksEfficiencyParam
from fall_tanks.gui.battle_results.fall_tanks_pbs_helper import isFinished, getFinishPlace, getFinishTime, getRespawnCount

class FallTanksTeamStats(FunRandomTeamStats):
    _PLAYER_MODEL_CLS = FunPlayerModel
    _STATS_VALUES_COLUMNS = {FunTeamStatsColumnTypes.FINISH_POSITION: None,
     FunTeamStatsColumnTypes.FINISH_TIME: None,
     TeamStatsColumnTypes.FRAG: None}
    _SORTING_PRIORITIES = ((FunTeamStatsColumnTypes.FINISH_TIME, SortingOrder.ASC),)
    _STATS_EFFICIENCY = ((FunTeamStatsColumnTypes.FINISH_POSITION, getFinishPlace, StatsValueType.INTEGER),
     (FunTeamStatsColumnTypes.FINISH_TIME, getFinishTime, StatsValueType.FLOAT),
     (FunTeamStatsColumnTypes.CHECKPOINTS, lambda sInfo: sInfo.checkpointsPassed, StatsValueType.INTEGER),
     (TeamStatsColumnTypes.FRAG, lambda sInfo: sInfo.kills, StatsValueType.INTEGER))

    @classmethod
    def packModel(cls, model, battleResults):
        players = battleResults.reusable.getAllPlayersIterator(battleResults.results['vehicles'])
        cls._packTeam(model.getEnemies(), players, battleResults)
        cls._packShownColumns(model.getShownValueColumns(), battleResults)
        cls._packSortingParams(model, battleResults)
        model.setIsSingleTeamPostbattle(True)

    @classmethod
    def _packSortingParams(cls, model, _):
        defaultSorting = first(cls._SORTING_PRIORITIES)
        if defaultSorting is not None:
            column, order = defaultSorting
            model.setSortingColumn(column)
            model.setSortingOrder(SortingOrder(order))
        return


class FallTanksBattleInfo(FunRandomBattleInfo):
    _BATTLE_TYPE = FunBattleType.RACE

    @classmethod
    def _getFinishReasonResource(cls, reusable, results):
        return R.strings.fall_tanks.battleResults.finishReason.finished() if isFinished(reusable, results) else R.strings.fall_tanks.battleResults.finishReason.notFinished()

    @classmethod
    def _getWinStatus(cls, reusable, results):
        return FunRaceStatus.FINISHED if isFinished(reusable, results) else FunRaceStatus.NOT_FINISHED


class FallTanksPersonalEfficiency(PersonalEfficiency):
    _DEFAULT_PARAMS = (FallTanksEfficiencyParam.FINISH_POSITION,
     FallTanksEfficiencyParam.FINISH_TIME,
     FallTanksEfficiencyParam.CHECKPOINTS_PASSED,
     FallTanksEfficiencyParam.DESTROYED,
     FallTanksEfficiencyParam.DEATH_COUNT)
    _VALUE_EXTRACTORS = {FallTanksEfficiencyParam.FINISH_POSITION: getFinishPlace,
     FallTanksEfficiencyParam.FINISH_TIME: getFinishTime,
     FallTanksEfficiencyParam.DEATH_COUNT: getRespawnCount}
    _VALUE_TYPES = {FallTanksEfficiencyParam.FINISH_TIME: ValueType.TIME,
     FallTanksEfficiencyParam.FINISH_POSITION: ValueType.NON_NEGATIVE_INTEGER}
