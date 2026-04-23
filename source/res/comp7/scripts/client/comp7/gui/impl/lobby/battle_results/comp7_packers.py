# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/battle_results/comp7_packers.py
from __future__ import absolute_import
from copy import deepcopy
import typing
from comp7.gui.impl.gen.view_models.views.lobby.battle_results.comp7_detailed_stats_parameter_model import Comp7ParamType
from comp7.gui.impl.lobby.battle_results.comp7_team_stats_params_settings import COMP7_PARAMETERS_UPDATE
from comp7.gui.impl.lobby.comp7_helpers import comp7_shared
from comp7.gui.impl.gen.view_models.views.lobby.battle_results.comp7_player_model import Comp7PlayerModel
from comp7.gui.impl.gen.view_models.views.lobby.battle_results.comp7_stats_efficiency_model import Comp7StatsEfficiencyModel
from comp7.gui.impl.gen.view_models.views.lobby.battle_results.comp7_team_stats_model import Comp7ColumnType
from comp7.gui.impl.lobby.comp7_helpers.comp7_shared import getPlayerDivisionByRankAndIndex
from gui.battle_results import stored_sorting
from gui.battle_results.presenters.packers.team.statistics_packer import Statistics
from gui.battle_results.presenters.packers.team.stats_params_settings import REGULAR_PARAMETERS
from gui.battle_results.presenters.packers.team.team_stats_packer import TeamStats, TeamAchievementsPacker
from gui.battle_results.presenters.packers.user_info import AccountInfo, PlayerInfo, UserStatus
from gui.impl.gen.view_models.views.lobby.battle_results.team_stats_model import SortingOrder
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.system_factory import collectBattleResultsStatsSorting
if typing.TYPE_CHECKING:
    from comp7.gui.impl.gen.view_models.views.lobby.battle_results.comp7_team_stats_model import Comp7TeamStatsModel
    from comp7_core.gui.battle_results.reusable.shared import Comp7CoreVehicleSummarizeInfo
    from gui.battle_results.stats_ctrl import BattleResults
_VehicleTags = (VEHICLE_TAGS.PREMIUM_IGR,)

class Comp7PlayerInfo(PlayerInfo):
    __slots__ = ()

    @classmethod
    def packModel(cls, model, battleResults, vehicleSumInfo):
        super(Comp7PlayerInfo, cls).packModel(model, battleResults, vehicleSumInfo)
        personalInfo = battleResults.reusable.getPlayerInfo()
        model.setPrebattleID(personalInfo.prebattleID if personalInfo.squadIndex else 0)
        TeamAchievementsPacker.packModel(model.getAchievements(), vehicleSumInfo, battleResults)
        if vehicleSumInfo.avatar:
            comp7QualActive = vehicleSumInfo.avatar.extensionInfo.get('comp7QualActive', False)
            rank, divisionIdx, _serialIdx = vehicleSumInfo.avatar.extensionInfo.get('comp7Rank', (0, 0, 0))
            if rank > 0:
                division = getPlayerDivisionByRankAndIndex(rank, divisionIdx)
                rank = comp7_shared.getRankEnumValue(division)
                model.setDivision(comp7_shared.getDivisionEnumValue(division))
                model.setRank(rank)
            model.setIsQualification(comp7QualActive)
            if vehicleSumInfo.avatar.extensionInfo.get('isSuperSquad', False):
                model.setSquadIndex(Comp7PlayerModel.SUPER_PLATOON_SQUAD_INDEX)

    @classmethod
    def _packAccountInfo(cls, model, battleResults, vehicleSumInfo):
        AccountInfo.packFullUserNames(model.userNames, vehicleSumInfo, battleResults)
        Comp7UserStatus.packUserStatus(model.userStatus, battleResults, vehicleSumInfo)


class Comp7UserStatus(UserStatus):
    _USER_INFO_PACKER = AccountInfo


class Comp7Statistics(Statistics):
    __ALL_PARAMETERS = {}
    _STATS_PARAMETERS = Statistics._STATS_PARAMETERS + (Comp7ParamType.HEALED, Comp7ParamType.CAPTUREDPOINTSOFINTEREST, Comp7ParamType.ROLESKILLUSED)

    @classmethod
    def _getAllParameters(cls):
        if not cls.__ALL_PARAMETERS:
            cls.__ALL_PARAMETERS = deepcopy(REGULAR_PARAMETERS)
            cls.__ALL_PARAMETERS.update(COMP7_PARAMETERS_UPDATE)
        return cls.__ALL_PARAMETERS


class Comp7TeamEfficiency(TeamStats):
    _PLAYER_MODEL_CLS = Comp7PlayerModel
    _PLAYER_INFO_PACKER = Comp7PlayerInfo
    _STATS_PACKER = Comp7Statistics

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
        comp7ColumnValues = {item.value for item in Comp7ColumnType}
        model.setSortingOrder(SortingOrder(sortingOrder))
        model.setSortingColumn(Comp7ColumnType(column) if column in comp7ColumnValues else Comp7ColumnType.VEHICLE)

    @classmethod
    def _packEfficiency(cls, efficiencyModel, summarizeInfo):
        efficiencyModel.setDamageDealt(summarizeInfo.damageDealt)
        efficiencyModel.setKills(summarizeInfo.kills)
        efficiencyModel.setEarnedXp(summarizeInfo.xp)
        efficiencyModel.setPrestigePoints(summarizeInfo.prestigePoints)
