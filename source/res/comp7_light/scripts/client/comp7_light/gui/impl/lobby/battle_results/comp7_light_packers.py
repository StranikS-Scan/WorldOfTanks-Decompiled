# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/battle_results/comp7_light_packers.py
from __future__ import absolute_import
from copy import deepcopy
import typing
from comp7_light.gui.impl.gen.view_models.views.lobby.battle_results import comp7_light_detailed_stats_parameter_model as detailed_stats_model
from comp7_light.gui.impl.lobby.battle_results.comp7_light_team_stats_params_settings import COMP7_LIGHT_PARAMETERS_UPDATE
from comp7_light.gui.impl.gen.view_models.views.lobby.battle_results.comp7_light_player_model import Comp7LightPlayerModel
from comp7_light.gui.impl.gen.view_models.views.lobby.battle_results.comp7_light_stats_efficiency_model import Comp7LightStatsEfficiencyModel
from comp7_light.gui.impl.gen.view_models.views.lobby.battle_results.comp7_light_team_stats_model import Comp7LightColumnType
from gui.battle_results import stored_sorting
from gui.battle_results.presenters.packers.team.statistics_packer import Statistics
from gui.battle_results.presenters.packers.team.stats_params_settings import REGULAR_PARAMETERS
from gui.battle_results.presenters.packers.team.team_stats_packer import TeamStats, TeamAchievementsPacker
from gui.battle_results.presenters.packers.user_info import AccountInfo, PlayerInfo, UserStatus
from gui.impl.gen.view_models.views.lobby.battle_results.team_stats_model import SortingOrder
from gui.shared.system_factory import collectBattleResultsStatsSorting
if typing.TYPE_CHECKING:
    from comp7_light.gui.impl.gen.view_models.views.lobby.battle_results.comp7_light_team_stats_model import Comp7LightTeamStatsModel
    from comp7_core.gui.battle_results.reusable.shared import Comp7CoreVehicleSummarizeInfo
    from gui.battle_results.stats_ctrl import BattleResults

class Comp7LightPlayerInfo(PlayerInfo):
    __slots__ = ()

    @classmethod
    def packModel(cls, model, battleResults, vehicleSumInfo):
        super(Comp7LightPlayerInfo, cls).packModel(model, battleResults, vehicleSumInfo)
        personalInfo = battleResults.reusable.getPlayerInfo()
        model.setPrebattleID(personalInfo.prebattleID if personalInfo.squadIndex else 0)
        TeamAchievementsPacker.packModel(model.getAchievements(), vehicleSumInfo, battleResults)

    @classmethod
    def _packAccountInfo(cls, model, battleResults, vehicleSumInfo):
        AccountInfo.packFullUserNames(model.userNames, vehicleSumInfo, battleResults)
        Comp7LightUserStatus.packUserStatus(model.userStatus, battleResults, vehicleSumInfo)


class Comp7LightUserStatus(UserStatus):
    _USER_INFO_PACKER = AccountInfo


class Comp7LightStatistics(Statistics):
    __ALL_PARAMETERS = {}
    _STATS_PARAMETERS = Statistics._STATS_PARAMETERS + (detailed_stats_model.Comp7LightParamType.HEALED, detailed_stats_model.Comp7LightParamType.CAPTUREDPOINTSOFINTEREST, detailed_stats_model.Comp7LightParamType.ROLESKILLUSED)

    @classmethod
    def _getAllParameters(cls):
        if not cls.__ALL_PARAMETERS:
            cls.__ALL_PARAMETERS = deepcopy(REGULAR_PARAMETERS)
            cls.__ALL_PARAMETERS.update(COMP7_LIGHT_PARAMETERS_UPDATE)
        return cls.__ALL_PARAMETERS


class Comp7LightTeamEfficiency(TeamStats):
    _PLAYER_MODEL_CLS = Comp7LightPlayerModel
    _PLAYER_INFO_PACKER = Comp7LightPlayerInfo
    _STATS_PACKER = Comp7LightStatistics

    @classmethod
    def packModel(cls, model, battleResults):
        allies, enemies = battleResults.reusable.getBiDirectionTeamsIterator(battleResults.results['vehicles'])
        cls._packTeam(model.getAllies(), allies, battleResults)
        cls._packTeam(model.getEnemies(), enemies, battleResults)
        cls._packSortingParams(model, battleResults)

    @classmethod
    def _packSortingParams(cls, model, battleResults):
        reusable = battleResults.reusable
        bonusType = reusable.common.arenaBonusType
        sortingKey = collectBattleResultsStatsSorting().get(bonusType)
        column, sortingOrder = stored_sorting.readStatsSorting(sortingKey)
        comp7LightColumnValues = {item.value for item in Comp7LightColumnType}
        model.setSortingOrder(SortingOrder(sortingOrder))
        if column and column in comp7LightColumnValues:
            model.setSortingColumn(Comp7LightColumnType(column))

    @classmethod
    def _packEfficiency(cls, efficiencyModel, summarizeInfo):
        efficiencyModel.setDamageDealt(summarizeInfo.damageDealt)
        efficiencyModel.setKills(summarizeInfo.kills)
        efficiencyModel.setEarnedXp(summarizeInfo.xp)
        efficiencyModel.setPrestigePoints(summarizeInfo.prestigePoints)
