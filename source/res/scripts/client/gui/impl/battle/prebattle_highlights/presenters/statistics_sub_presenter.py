# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/prebattle_highlights/presenters/statistics_sub_presenter.py
from __future__ import absolute_import
import typing
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.impl.gen.view_models.views.battle.prebattle_highlights.prebattle_highlights_player_stats_model import PrebattleHighlightsPlayerStatsModel
from gui.impl.gen.view_models.views.battle.prebattle_highlights.stats_parameter_model import StatsParameterModel
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
_STATS_PARAMS_TO_MODEL_MAP = {'pbhDynVeh.battlesCount': StatsParameterModel.CURRENT_TANK_SESSION_BATTLES_COUNT,
 'pbhDynVeh.maxFrags': StatsParameterModel.CURRENT_TANK_SESSION_MAX_FRAGS,
 'pbhDynVeh.maxDamageBlockedByArmor': StatsParameterModel.CURRENT_TANK_SESSION_MAX_DAMAGE_BLOCKED_BY_ARMOR,
 'pbhDynVeh.maxDamageDealt': StatsParameterModel.CURRENT_TANK_SESSION_MAX_DAMAGE_DEALT,
 'pbhDynVeh.maxAssisted': StatsParameterModel.CURRENT_TANK_SESSION_MAX_ASSISTED,
 'pbhDynVeh.maxSpotted': StatsParameterModel.CURRENT_TANK_SESSION_MAX_SPOTTED,
 'pbhDynVeh.survivedCount': StatsParameterModel.CURRENT_TANK_SESSION_MAX_SURVIVED,
 'pbhDynVeh.winsCount': StatsParameterModel.CURRENT_TANK_SESSION_WIN_STREAK,
 'pbhDynAcc.battlesCount': StatsParameterModel.ACCOUNT_SESSION_BATTLES_COUNT,
 'pbhDynAcc.totalTanksUsed': StatsParameterModel.ACCOUNT_SESSION_TOTAL_TANKS_USED,
 'pbhDynAcc.totalFrags': StatsParameterModel.ACCOUNT_SESSION_TOTAL_FRAGS,
 'pbhDynAcc.totalWins': StatsParameterModel.ACCOUNT_SESSION_TOTAL_WINS,
 'pbhDynAcc.totalDamageBlockedByArmor': StatsParameterModel.ACCOUNT_SESSION_TOTAL_DAMAGE_BLOCKED_BY_ARMOR,
 'pbhDynAcc.totalDamageDealt': StatsParameterModel.ACCOUNT_SESSION_TOTAL_DAMAGE_DEALT,
 'pbhDynAcc.totalAssisted': StatsParameterModel.ACCOUNT_SESSION_TOTAL_ASSISTED,
 'pbhDynAcc.totalSpotted': StatsParameterModel.ACCOUNT_SESSION_TOTAL_SPOTTED,
 'pbhDynAcc.winStreak': StatsParameterModel.ACCOUNT_SESSION_WIN_STREAK,
 'veh.battlesCount': StatsParameterModel.CURRENT_TANK_BATTLES_COUNT,
 'veh.frags': StatsParameterModel.CURRENT_TANK_FRAGS,
 'veh.spotted': StatsParameterModel.CURRENT_TANK_SPOTTED,
 'veh.damageDealt': StatsParameterModel.CURRENT_TANK_DAMAGE_DEALT,
 'veh.damageBlockedByArmor': StatsParameterModel.CURRENT_TANK_DAMAGE_BLOCKED_BY_ARMOR,
 'veh.assisted': StatsParameterModel.CURRENT_TANK_ASSISTED,
 'veh.wins': StatsParameterModel.CURRENT_TANK_WINS,
 'acc.totalDamageDealt': StatsParameterModel.ACCOUNT_TOTAL_DAMAGE_DEALT,
 'acc.totalWins': StatsParameterModel.ACCOUNT_TOTAL_WINS,
 'acc.totalSpotted': StatsParameterModel.ACCOUNT_TOTAL_SPOTTED,
 'acc.battlesCount': StatsParameterModel.ACCOUNT_BATTLES_COUNT,
 'fun.accAge': StatsParameterModel.ACCOUNT_FUN_AGE,
 'fun.treesDestroyed': StatsParameterModel.ACCOUNT_FUN_TREES_DESTROYED,
 'fun.totalMileage': StatsParameterModel.ACCOUNT_TOTAL_MILEAGE}

def getStatsParametersToModelMap():
    return _STATS_PARAMS_TO_MODEL_MAP


class StatisticsSubPresenter(SubModelPresenter):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def packModel(self):
        playersStats = self.__sessionProvider.dynamic.prebattleHighlightsController.winnersStats
        if not playersStats:
            return
        else:
            playersStatsModel = self.getViewModel()
            playersStatsModel.clear()
            for playerInfo in playersStats:
                vehId = playerInfo.get('id')
                playerStats = playerInfo.get('stats')
                if vehId is None or playerStats is None:
                    return
                playerStatsModel = PrebattleHighlightsPlayerStatsModel()
                playerStatsModel.setVehId(vehId)
                statsParamsModel = playerStatsModel.getStatsParams()
                statsParamsModel.clear()
                for paramName, paramValue in playerStats.items():
                    paramModel = StatsParameterModel()
                    paramsMap = getStatsParametersToModelMap()
                    paramModel.setParameter(paramsMap.get(paramName, ''))
                    paramModel.setValue(paramValue if paramValue is not None else 0)
                    statsParamsModel.addViewModel(paramModel)

                playersStatsModel.addViewModel(playerStatsModel)

            playersStatsModel.invalidate()
            return
