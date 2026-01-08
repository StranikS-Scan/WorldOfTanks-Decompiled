# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/frontline_presenters_packers.py
import typing
import json
from epic_constants import EPIC_BATTLE_TEAM_ID
from frameworks.wulf.view.array import fillViewModelsArray
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.battle_results import stored_sorting
from gui.battle_results.pbs_helpers.common import getTeamPlayerAchievements
from gui.battle_results.presenters.packers.team.statistics_packer import Statistics
from gui.battle_results.presenters.packers.team.team_stats_packer import TeamStats
from gui.battle_results.presenters.packers.user_info import AccountInfo, PlayerInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_results.detailed_stats_parameter_model import DetailedStatsParameterModel
from gui.impl.gen.view_models.views.lobby.battle_results.team_stats_model import SortingOrder
from gui.impl.gen.view_models.views.lobby.battle_results.simple_stats_parameter_model import ValueType
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.system_factory import collectBattleResultsStatsSorting
from frontline.gui.impl.gen.view_models.views.lobby.views.post_battle_results_view.player_model import PlayerModel
from frontline.gui.impl.gen.view_models.views.lobby.views.post_battle_results_view.battle_team_stats_model import FrontlineColumnType
from frontline.gui.impl.gen.view_models.views.lobby.views.post_battle_results_view.achievement_model import AchievementModel
from frontline.gui.impl.gen.view_models.views.lobby.views.post_battle_results_view.vehicle_stats_model import VehicleStatsModel
from frontline.gui.impl.gen.view_models.views.lobby.views.post_battle_results_view.vehicle_stats_model import FrontlineParamType
if typing.TYPE_CHECKING:
    from gui.battle_results.stats_ctrl import BattleResults
    from frontline.gui.impl.gen.view_models.views.lobby.views.post_battle_results_view.battle_team_stats_model import BattleTeamStatsModel

class FrontlinePlayerInfo(PlayerInfo):
    __slots__ = ()

    @classmethod
    def packModel(cls, model, battleResults, vehicleSumInfo):
        super(FrontlinePlayerInfo, cls).packModel(model, battleResults, vehicleSumInfo)
        if vehicleSumInfo.avatar is not None:
            model.setRank(vehicleSumInfo.avatar.extensionInfo.get('playerRank', 0))
        model.setRespawns(vehicleSumInfo.respawns)
        personalInfo = battleResults.reusable.getPlayerInfo()
        model.setPrebattleID(personalInfo.prebattleID if personalInfo.squadIndex else 0)
        FrontlineTeamAchievementsPacker.packModel(model.getAchievements(), vehicleSumInfo, battleResults)
        return

    @classmethod
    def _packAccountInfo(cls, model, battleResults, vehicleSumInfo):
        AccountInfo.packFullUserNames(model.userNames, vehicleSumInfo, battleResults)


class FrontlineTeamEfficiency(TeamStats):
    _PLAYER_MODEL_CLS = PlayerModel
    _PLAYER_INFO_PACKER = FrontlinePlayerInfo

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
    def packVehStatistics(cls, playerModel, summarizeInfo, battleResults):
        vehStatsVmArr = playerModel.getVehiclesStats()
        vehStatsVmArr.clear()
        summVehStatsModel = VehicleStatsModel()
        summVehStatsModel.setIsGeneralInfo(True)
        summVehStatsModel.setObjectivesReached(battleResults.results['common']['commonNumStarted'] > 0)
        summVehStatsModel.setObjectivesDestroyed(battleResults.results['common']['commonNumDestroyed'])
        summVehStatsModel.setZoneCaptured(battleResults.results['common']['commonNumCaptured'])
        summDetailedStatsModel = summVehStatsModel.getDetailedStatistics()
        Statistics.packModel(summDetailedStatsModel, summarizeInfo, battleResults)
        if summarizeInfo.player.team == EPIC_BATTLE_TEAM_ID.TEAM_ATTACKER:
            paramModel = cls.getAdditionalStatModel(True, FrontlineParamType.ATKOBJECTIVES, summarizeInfo.numCaptured, summarizeInfo.numDestroyed)
        else:
            paramModel = cls.getAdditionalStatModel(False, FrontlineParamType.DEFOBJECTIVES, summarizeInfo.numDefended, battleResults.reusable.common.numDefended)
        summDetailedStatsModel.addViewModel(paramModel)
        summDetailedStatsModel.invalidate()
        vehStatsVmArr.addViewModel(summVehStatsModel)
        for vehDetailedInfo in summarizeInfo.vehicles:
            if summarizeInfo.player.team == EPIC_BATTLE_TEAM_ID.TEAM_ATTACKER:
                vehParamModel = cls.getAdditionalStatModel(True, FrontlineParamType.ATKOBJECTIVES, vehDetailedInfo.numCaptured, vehDetailedInfo.numDestroyed)
            else:
                vehParamModel = cls.getAdditionalStatModel(False, FrontlineParamType.DEFOBJECTIVES, vehDetailedInfo.numDefended, battleResults.reusable.common.numDefended)
            vehStatsModel = VehicleStatsModel()
            vehStatsModel.setIsGeneralInfo(False)
            detailedStatsModel = vehStatsModel.getDetailedStatistics()
            Statistics.packModel(detailedStatsModel, vehDetailedInfo, battleResults)
            detailedStatsModel.addViewModel(vehParamModel)
            detailedStatsModel.invalidate()
            fillVehicleModel(vehStatsModel.vehicle, vehDetailedInfo.vehicle, (VEHICLE_TAGS.PREMIUM_IGR,))
            vehStatsVmArr.addViewModel(vehStatsModel)

        vehStatsVmArr.invalidate()

    @classmethod
    def getAdditionalStatModel(cls, isTeamAttacker, key, val1, val2):
        paramModel = DetailedStatsParameterModel()
        paramModel.setLabel(R.strings.battle_results.team.stats.labels_atkObjectives() if isTeamAttacker else R.strings.battle_results.team.stats.labels_defObjectives())
        paramModel.setLabelKey(key.value)
        paramModel.setParamValueType(ValueType.INTEGER)
        valueArr = paramModel.getValue()
        valueArr.clear()
        valueArr.addReal(val1)
        valueArr.addReal(val2)
        valueArr.invalidate()
        return paramModel

    @classmethod
    def _packSortingParams(cls, model, battleResults):
        reusable = battleResults.reusable
        bonusType = reusable.common.arenaBonusType
        sortingKey = collectBattleResultsStatsSorting().get(bonusType)
        column, sortingOrder = stored_sorting.readStatsSorting(sortingKey)
        model.setSortingOrder(SortingOrder(sortingOrder))
        model.setSortingColumn(FrontlineColumnType(column) if column in FrontlineColumnType else FrontlineColumnType.PLAYER)


class FrontlineTeamAchievementsPacker(object):

    @classmethod
    def packModel(cls, playerAchievementsModel, summarizeInfo, battleResults):
        reusable = battleResults.reusable
        playerAchievements = getTeamPlayerAchievements(summarizeInfo, reusable)
        viewModels = [ getAchievementResultsModel(achievement) for achievement in playerAchievements ]
        fillViewModelsArray(viewModels, playerAchievementsModel)


def getAchievementResultsModel(achievement):
    achievementModel = AchievementModel()
    achievementModel.setName(achievement.name)
    achievementModel.setIconName(achievement.iconName)
    achievementModel.setGroupID(achievement.groupID)
    achievementModel.setTooltipId(achievement.tooltipType)
    achievementModel.setTooltipArgs(achievement.tooltipArgs)
    return achievementModel


def getRankAchievementResultsModel(playerRank):
    achievementModel = AchievementModel()
    achievementModel.setName('rank{}'.format(playerRank))
    achievementModel.setIconName('rank_{}'.format(playerRank))
    achievementModel.setGroupID(AchievementModel.RANK)
    achievementModel.setTooltipId(TOOLTIPS_CONSTANTS.FRONTLINE_RANK)
    achievementTooltipArgs = [playerRank]
    achievementModel.setTooltipArgs(json.dumps(achievementTooltipArgs))
    return achievementModel
