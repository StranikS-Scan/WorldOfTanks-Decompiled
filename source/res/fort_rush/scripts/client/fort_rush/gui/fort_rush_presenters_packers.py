# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/fort_rush_presenters_packers.py
from __future__ import absolute_import
import typing
from copy import deepcopy
from fort_rush.gui.battle_results.pbs_helpers import getProgressionPointsCountToShow, isProgressionPointsShown, FORT_RUSH_PARAMETERS_UPDATE
from fort_rush.gui.impl.gen.view_models.views.lobby.post_battle_results_view.battle_team_stats_model import FortRushColumnType
from fort_rush.gui.impl.gen.view_models.views.lobby.post_battle_results_view.detailed_personal_efficiency_item_model import DetailedPersonalEfficiencyItemModel
from fort_rush.gui.impl.gen.view_models.views.lobby.post_battle_results_view.fort_rush_reward_item_model import FortRushRewardTypes, FortRushRewardItemModel
from fort_rush.gui.impl.gen.view_models.views.lobby.post_battle_results_view.player_model import PlayerModel
from fort_rush.gui.impl.gen.view_models.views.lobby.post_battle_results_view.vehicle_stats_model import VehicleStatsModel
from gui.battle_results import stored_sorting
from gui.battle_results.pbs_helpers.economics import getTotalCreditsToShow
from gui.battle_results.presenters.packers.personal_efficiency import PersonalEfficiency
from gui.battle_results.presenters.packers.personal_rewards import PersonalRewards
from gui.battle_results.presenters.packers.team.statistics_packer import Statistics
from gui.battle_results.presenters.packers.team.stats_params_settings import REGULAR_PARAMETERS
from gui.battle_results.presenters.packers.team.team_stats_packer import TeamStats
from gui.battle_results.presenters.packers.user_info import AccountInfo, PlayerInfo
from gui.impl.gen.view_models.views.lobby.battle_results.simple_stats_parameter_model import RegularParamType
from gui.impl.gen.view_models.views.lobby.battle_results.team_stats_model import SortingOrder
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.shared.system_factory import collectBattleResultsStatsSorting
if typing.TYPE_CHECKING:
    from gui.battle_results.stats_ctrl import BattleResults
    from fort_rush.gui.battle_results.reusable.fort_rush_shared import FortRushVehicleSummarizeInfo
    from fort_rush.gui.impl.gen.view_models.views.lobby.post_battle_results_view.fort_rush_stats_efficiency_model import FortRushStatsEfficiencyModel
    from fort_rush.gui.impl.gen.view_models.views.lobby.post_battle_results_view.battle_team_stats_model import BattleTeamStatsModel

class FortRushPersonalEfficiency(PersonalEfficiency):
    _DEFAULT_PARAMS = (DetailedPersonalEfficiencyItemModel.FORT_RUSH_SCORE,
     DetailedPersonalEfficiencyItemModel.KILLED,
     DetailedPersonalEfficiencyItemModel.SPOTTED,
     DetailedPersonalEfficiencyItemModel.DAMAGE_DEALT,
     DetailedPersonalEfficiencyItemModel.PIERCINGS,
     DetailedPersonalEfficiencyItemModel.DAMAGE_ASSISTED,
     DetailedPersonalEfficiencyItemModel.CRITICAL_DAMAGE,
     DetailedPersonalEfficiencyItemModel.DAMAGE_BLOCKED_BY_ARMOR,
     DetailedPersonalEfficiencyItemModel.RICKOCHETS_RECEIVED,
     DetailedPersonalEfficiencyItemModel.NO_DAMAGE_DIRECT_HITS_RECIEVEVD)
    _VALUE_EXTRACTORS = {DetailedPersonalEfficiencyItemModel.KILLED: lambda info, _: info.kills}
    _EFFICIENCY_ITEM_MODEL_CLS = DetailedPersonalEfficiencyItemModel

    @classmethod
    def _createParameterModel(cls, parameter, vehicleInfo):
        efficiencyParameter = cls._EFFICIENCY_ITEM_MODEL_CLS()
        efficiencyParameter.setParamType(parameter)
        valueExtractor = cls._VALUE_EXTRACTORS.get(parameter, getattr)
        efficiencyParameter.setValue(valueExtractor(vehicleInfo, parameter))
        return efficiencyParameter


class FortRushPlayerInfo(PlayerInfo):
    __slots__ = ()

    @classmethod
    def _packAccountInfo(cls, model, battleResults, vehicleSumInfo):
        AccountInfo.packFullUserNames(model.userNames, vehicleSumInfo, battleResults)


class FortRushPersonalRewards(PersonalRewards):
    _AVAILABLE_REWARDS = [FortRushRewardTypes.CREDITS, FortRushRewardTypes.PROGRESSION_POINTS]
    _ITEM_MODEL_CLS = FortRushRewardItemModel
    _REWARD_GETTERS = {FortRushRewardTypes.CREDITS: getTotalCreditsToShow,
     FortRushRewardTypes.PROGRESSION_POINTS: getProgressionPointsCountToShow}
    _REWARDS_TO_CONDITION_MAP = {FortRushRewardTypes.PROGRESSION_POINTS: isProgressionPointsShown}


class FortRushStatisticsPacker(Statistics):
    __ALL_PARAMETERS = {}
    _STATS_PARAMETERS = (RegularParamType.CAPTUREPOINTSVAL,
     RegularParamType.SHOTS,
     RegularParamType.DAMAGEDEALT,
     RegularParamType.DIRECTHITSRECEIVED,
     RegularParamType.EXPLOSIONHITSRECEIVED,
     RegularParamType.DAMAGEBLOCKEDBYARMOR,
     RegularParamType.TEAMHITSDAMAGE,
     RegularParamType.SPOTTED,
     RegularParamType.DAMAGEDKILLED,
     RegularParamType.DAMAGEASSISTED,
     RegularParamType.DAMAGEASSISTEDSELF,
     RegularParamType.STUNDURATION,
     RegularParamType.DAMAGEASSISTEDSTUN,
     RegularParamType.DAMAGEASSISTEDSTUNSELF,
     RegularParamType.STUNNUM,
     RegularParamType.MILEAGE)

    @classmethod
    def _getAllParameters(cls):
        if not cls.__ALL_PARAMETERS:
            cls.__ALL_PARAMETERS = deepcopy(REGULAR_PARAMETERS)
            cls.__ALL_PARAMETERS.update(FORT_RUSH_PARAMETERS_UPDATE)
        return cls.__ALL_PARAMETERS


class FortRushTeamEfficiency(TeamStats):
    _PLAYER_MODEL_CLS = PlayerModel
    _PLAYER_INFO_PACKER = FortRushPlayerInfo

    @classmethod
    def packModel(cls, model, battleResults):
        allies, enemies = battleResults.reusable.getBiDirectionTeamsIterator(battleResults.results['vehicles'])
        cls._packTeam(model.getAllies(), allies, battleResults)
        cls._packTeam(model.getEnemies(), enemies, battleResults)
        cls._packSortingParams(model, battleResults)

    @classmethod
    def packPlayer(cls, playerModel, summarizeInfo, battleResults):
        cls._PLAYER_INFO_PACKER.packModel(playerModel, battleResults, summarizeInfo)
        cls.packVehStatistics(playerModel, summarizeInfo, battleResults)
        cls._packEfficiency(playerModel.efficiencyValues, summarizeInfo)

    @classmethod
    def _packEfficiency(cls, efficiencyModel, summarizeInfo):
        efficiencyModel.setDamageDealt(summarizeInfo.damageDealt)
        efficiencyModel.setKills(summarizeInfo.kills)
        efficiencyModel.setFortRushScore(summarizeInfo.fortRushScore)
        efficiencyModel.setRespawns(summarizeInfo.respawns)

    @classmethod
    def packVehStatistics(cls, playerModel, summarizeInfo, battleResults):
        vehStatsVmArr = playerModel.getVehiclesStats()
        vehStatsVmArr.clear()
        allVehStatsModel = VehicleStatsModel()
        allVehStatsModel.setIsGeneralInfo(True)
        allDetailedStatsModel = allVehStatsModel.getDetailedStatistics()
        FortRushStatisticsPacker.packModel(allDetailedStatsModel, summarizeInfo, battleResults)
        allDetailedStatsModel.invalidate()
        vehStatsVmArr.addViewModel(allVehStatsModel)
        for vehDetailedInfo in summarizeInfo.vehicles:
            vehStatsModel = VehicleStatsModel()
            vehStatsModel.setIsGeneralInfo(False)
            detailedStatsModel = vehStatsModel.getDetailedStatistics()
            FortRushStatisticsPacker.packModel(detailedStatsModel, vehDetailedInfo, battleResults)
            detailedStatsModel.invalidate()
            fillVehicleModel(vehStatsModel.vehicle, vehDetailedInfo.vehicle)
            vehStatsVmArr.addViewModel(vehStatsModel)

        vehStatsVmArr.invalidate()

    @classmethod
    def _packSortingParams(cls, model, battleResults):
        reusable = battleResults.reusable
        bonusType = reusable.common.arenaBonusType
        sortingKey = collectBattleResultsStatsSorting().get(bonusType)
        column, sortingOrder = stored_sorting.readStatsSorting(sortingKey)
        fortRushColumnValues = {item.value for item in FortRushColumnType}
        model.setSortingOrder(SortingOrder(sortingOrder))
        model.setSortingColumn(FortRushColumnType(column) if column in fortRushColumnValues else FortRushColumnType.PLAYER)
