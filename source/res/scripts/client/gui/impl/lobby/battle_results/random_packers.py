# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_results/random_packers.py
import typing
from gui.battle_results import stored_sorting
from gui.battle_results.presenters.packers.team.team_stats_packer import TeamStats, TeamAchievementsPacker
from gui.battle_results.presenters.packers.user_info import AccountInfo, PlayerInfo, UserStatus
from gui.impl.gen.view_models.views.lobby.battle_results.random.random_player_model import RandomPlayerModel
from gui.impl.gen.view_models.views.lobby.battle_results.random.random_team_stats_model import RandomColumnType
from gui.impl.gen.view_models.views.lobby.battle_results.team_stats_model import SortingOrder
from gui.shared.system_factory import collectBattleResultsStatsSorting
if typing.TYPE_CHECKING:
    from gui.battle_results.stats_ctrl import BattleResults
    from gui.impl.gen.view_models.views.lobby.battle_results.random.random_team_stats_model import RandomTeamStatsModel

class RandomPlayerInfo(PlayerInfo):
    __slots__ = ()

    @classmethod
    def packModel(cls, model, battleResults, vehicleSumInfo):
        super(RandomPlayerInfo, cls).packModel(model, battleResults, vehicleSumInfo)
        personalInfo = battleResults.reusable.getPlayerInfo()
        model.setPrebattleID(personalInfo.prebattleID if personalInfo.squadIndex else 0)
        TeamAchievementsPacker.packModel(model.getAchievements(), vehicleSumInfo, battleResults)

    @classmethod
    def _packAccountInfo(cls, model, battleResults, vehicleSumInfo):
        AccountInfo.packFullUserNames(model.userNames, vehicleSumInfo, battleResults)
        RandomUserStatus.packUserStatus(model.userStatus, battleResults, vehicleSumInfo)


class RandomUserStatus(UserStatus):
    _USER_INFO_PACKER = AccountInfo


class RandomTeamEfficiency(TeamStats):
    _PLAYER_MODEL_CLS = RandomPlayerModel
    _PLAYER_INFO_PACKER = RandomPlayerInfo

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
        model.setSortingColumn(RandomColumnType(column))
        model.setSortingOrder(SortingOrder(sortingOrder))
