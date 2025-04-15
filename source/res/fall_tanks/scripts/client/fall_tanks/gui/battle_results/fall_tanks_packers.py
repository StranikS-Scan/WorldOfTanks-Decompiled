# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/battle_results/fall_tanks_packers.py
from gui.battle_results.presenters.packers.personal_efficiency import PersonalEfficiency
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_results.team_stats_model import SortingOrder
from gui.impl.gen.view_models.views.lobby.battle_results.team_stats_column_types import TeamStatsColumnTypes
from shared_utils import first
from fun_random.gui.battle_results.packers.fun_packers import FunRandomTeamStats, FunRandomBattleInfo
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_efficiency_param import FunEfficiencyParam
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_team_stats_column_types import FunTeamStatsColumnTypes
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_battle_status import FunBattleStatus
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_battle_type import FunBattleType
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_player_model import FunPlayerModel
from fall_tanks.gui.battle_results.fall_tanks_pbs_helper import isFinished, getFinishPlace, getFinishTime, getRespawnCount

class FallTanksTeamStats(FunRandomTeamStats):
    __slots__ = ()
    _PLAYER_MODEL_CLS = FunPlayerModel
    _STATS_VALUES_COLUMNS = {FunTeamStatsColumnTypes.FINISH_POSITION: None,
     FunTeamStatsColumnTypes.FINISH_TIME: None,
     TeamStatsColumnTypes.FRAG: None}
    _SORTING_PRIORITIES = ((FunTeamStatsColumnTypes.FINISH_TIME, SortingOrder.ASC),)

    @classmethod
    def packModel(cls, model, battleResults):
        players = battleResults.reusable.getAllPlayersIterator(battleResults.results['vehicles'])
        cls._packTeam(model.getEnemies(), players, battleResults)
        cls._packShownColumns(model.getShownValueColumns(), battleResults)
        cls._packSortingParams(model, battleResults)
        model.setIsSingleTeamPostbattle(True)

    @classmethod
    def _packEfficiency(cls, efficiencyModel, summarizeInfo):
        efficiencyModel.setKills(summarizeInfo.kills)
        efficiencyModel.setCheckpointsPassed(summarizeInfo.checkpointsPassed)
        finishTime = max(summarizeInfo.finishTime, 0.0)
        efficiencyModel.setFinishTime(finishTime)
        finishPosition = summarizeInfo.finishPosition if finishTime > 0.0 else 0
        efficiencyModel.setFinishPosition(finishPosition)

    @classmethod
    def _packSortingParams(cls, model, _):
        defaultSorting = first(cls._SORTING_PRIORITIES)
        if defaultSorting is not None:
            column, order = defaultSorting
            model.setSortingColumn(column)
            model.setSortingOrder(SortingOrder(order))
        return


class FallTanksBattleInfo(FunRandomBattleInfo):
    __slots__ = ()
    _BATTLE_TYPE = FunBattleType.RACE

    @classmethod
    def _getFinishReasonResource(cls, reusable, results):
        return R.strings.fall_tanks.battleResults.finishReason.finished() if isFinished(reusable, results) else R.strings.fall_tanks.battleResults.finishReason.notFinished()

    @classmethod
    def _getWinStatus(cls, reusable, results):
        return FunBattleStatus.FINISHED if isFinished(reusable, results) else FunBattleStatus.NOT_FINISHED


class FallTanksPersonalEfficiency(PersonalEfficiency):
    _DEFAULT_PARAMS = (FunEfficiencyParam.FINISH_POSITION,
     FunEfficiencyParam.FINISH_TIME,
     FunEfficiencyParam.CHECKPOINTS_PASSED,
     FunEfficiencyParam.DESTROYED,
     FunEfficiencyParam.DEATH_COUNT)
    _VALUE_EXTRACTORS = {FunEfficiencyParam.FINISH_POSITION: getFinishPlace,
     FunEfficiencyParam.FINISH_TIME: getFinishTime,
     FunEfficiencyParam.DEATH_COUNT: getRespawnCount}
