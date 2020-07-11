# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/battle_royale/battle_result_view_base.py
import typing
from collections import OrderedDict
from constants import ATTACK_REASON_INDICES, ATTACK_REASON, DEATH_REASON_ALIVE
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.views.battle_royale.battle_results.personal.stat_item_model import StatItemModel
from gui.impl.gen.view_models.views.battle_royale.battle_results.personal.battle_reward_item_model import BattleRewardItemModel
from gui.impl.gen.view_models.views.battle_royale.battle_results.leaderboard.group_model import GroupModel
from gui.impl.gen.view_models.views.battle_royale.battle_results.leaderboard.row_model import RowModel
from gui.impl.gen.view_models.views.battle_royale.battle_results.leaderboard.leaderboard_constants import LeaderboardConstants
from gui.server_events.battle_royale_formatters import BRSections
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from frameworks.wulf.view.array import Array
    from gui.impl.gen.view_models.views.battle_royale.battle_results.player_vehicle_status_model import PlayerVehicleStatusModel
    from gui.impl.gen.view_models.views.battle_royale.battle_results.personal.personal_results_model import PersonalResultsModel
    from gui.impl.gen.view_models.views.battle_royale.battle_results.leaderboard.leaderboard_model import LeaderboardModel
    from gui.impl.gen.view_models.views.battle.battle_royale.battle_result_view_model import BattleResultViewModel as BattleResultViewModelInBattle
    from gui.impl.gen.view_models.views.lobby.battle_royale.battle_result_view.battle_result_view_model import BattleResultViewModel as BattleResultViewModelInLobby
_HIDDEN_BONUSES_WITH_ZERO_VALUES = frozenset([BattleRewardItemModel.CRYSTALS])

def _getAttackReason(vehicleState, hasKiller):
    if vehicleState == DEATH_REASON_ALIVE:
        reason = R.strings.battle_royale.battleResult.playerVehicleStatus.alive()
    elif vehicleState == ATTACK_REASON_INDICES[ATTACK_REASON.DEATH_ZONE]:
        reason = R.strings.battle_royale.battleResult.playerVehicleStatus.reason.deathByZone()
    elif hasKiller:
        reason = R.strings.battle_royale.battleResult.playerVehicleStatus.reason.deathByPlayer()
    else:
        reason = R.strings.battle_royale.battleResult.playerVehicleStatus.reason.other()
    return reason


class BrBattleResultsViewBase(ViewImpl):
    __slots__ = ('_data',)
    _BR_POINTS_ICON = R.images.gui.maps.icons.battleRoyale.battleResult.leaderboard.br_selector_16()
    _CURRENCIES = [BattleRewardItemModel.XP,
     BattleRewardItemModel.CREDITS,
     BattleRewardItemModel.PROGRESSION_POINTS,
     BattleRewardItemModel.CRYSTALS]

    def __init__(self, settings, *args, **kwargs):
        super(BrBattleResultsViewBase, self).__init__(settings)
        self._data = self._getData(**kwargs)
        if not self._data:
            raise SoftException('There is not battleResults')

    def _finalize(self):
        self._data = None
        super(BrBattleResultsViewBase, self)._finalize()
        return

    def _getData(self, **kwargs):
        raise NotImplementedError

    def _getFinishReason(self):
        raise NotImplementedError

    def _getStats(self):
        raise NotImplementedError

    def _getFinancialData(self):
        raise NotImplementedError

    def _fillLeaderboardGroups(self, leaderboard, groupList):
        raise NotImplementedError

    def _setTabsData(self, battleResultModel):
        if self._data is None:
            raise SoftException('There is no battle results')
        with battleResultModel.transaction() as model:
            self._setLeaderboard(model.leaderboardModel)
            self._setPlayerVehicleStatus(model.playerVehicleStatus)
            self._setPersonalResult(model.personalResults)
        return

    def _setPersonalResult(self, personalResultModel):
        self.__setFinishResult(personalResultModel)
        self.__setStats(personalResultModel)
        self.__setBattleRewards(personalResultModel)

    def _setPlayerVehicleStatus(self, statusModel):
        commonInfo = self._data.get(BRSections.COMMON)
        if commonInfo is None:
            raise SoftException('There is no vehicle status info in battle results')
        statusInfo = commonInfo['vehicleStatus']
        self.__setUserName(statusModel.user, commonInfo)
        killerInfo = statusInfo['killer']
        hasKiller = killerInfo and not statusInfo['isSelfDestroyer']
        statusModel.setReason(_getAttackReason(statusInfo.get('vehicleState', ''), hasKiller))
        if hasKiller:
            self.__setUserName(statusModel.killer, killerInfo)
        return

    def _setLeaderboard(self, leaderboardModel):
        leaderboard = self._data.get(BRSections.LEADERBOARD)
        if leaderboard is None:
            raise SoftException("There is no players' table in battle results")
        leaderboardModel.setType(self.__getLeaderboardType())
        groupList = leaderboardModel.getGroupList()
        groupList.clear()
        self._fillLeaderboardGroups(leaderboard, groupList)
        groupList.invalidate()
        return

    def _fillLeaderbordGroup(self, groupList, group, points, place=0, isPersonalSquad=False):
        groupModel = GroupModel()
        groupModel.setRewardCount(points)
        groupModel.setRewardIcon(self._BR_POINTS_ICON)
        groupModel.setPlace(str(place) if place > 0 else '')
        groupModel.setIsPersonalSquad(isPersonalSquad)
        if group:
            self._setPlayers(groupModel, group)
        groupList.addViewModel(groupModel)

    def _setPlayers(self, groupModel, players):
        playerList = groupModel.getPlayersList()
        playerList.clear()
        for player in players:
            playerModel = RowModel()
            place = self._getPlayerPlace(player)
            playerModel.setPlace(str(place) if place > 0 else '')
            self.__setUserName(playerModel.user, player)
            playerModel.setType(self.__getRowType(player))
            playerList.addViewModel(playerModel)

        playerList.invalidate()

    def _getPlayerPlace(self, player):
        return 0 if self._isSquadMode() else player['place']

    def _isSquadMode(self):
        return self._data[BRSections.COMMON]['isSquadMode']

    def __getLeaderboardType(self):
        return LeaderboardConstants.LIST_TYPE_BR_PLATOON if self._isSquadMode() else LeaderboardConstants.LIST_TYPE_BR_SOLO

    def __setFinishResult(self, personalResultsModel):
        finishReason = self._getFinishReason()
        personalResultsModel.setFinishResultLabel(finishReason)

    def __setBattleRewards(self, rewardsModel):
        rewardList = rewardsModel.getBattleRewardsList()
        rewardList.clear()
        rewards = self.__getEarnedFinance()
        for reward in rewards:
            rewardList.addViewModel(reward)

        rewardList.invalidate()

    def __setStats(self, statsModel):
        statsInfo = self._getStats()
        if statsInfo is None:
            raise SoftException("There is no player's efficiency in battle results")
        statList = statsModel.getStatsList()
        statList.clear()
        for statData in statsInfo:
            statModel = StatItemModel()
            statModel.setType(statData['type'])
            statModel.setWreathImage(statData.get('wreathImage', R.invalid()))
            statModel.setCurrentValue(statData['value'])
            statModel.setMaxValue(statData['maxValue'])
            statList.addViewModel(statModel)

        statList.invalidate()
        return

    def __getEarnedFinance(self):
        earned = self._getFinancialData()
        sortedEarned = OrderedDict(sorted(earned.iteritems(), key=lambda x: self._CURRENCIES.index(x[0])))
        financialList = []
        for bonusType, value in sortedEarned.iteritems():
            if value > 0 or bonusType not in _HIDDEN_BONUSES_WITH_ZERO_VALUES:
                statModel = BattleRewardItemModel()
                statModel.setType(bonusType)
                statModel.setValue(value)
                financialList.append(statModel)

        return financialList

    @staticmethod
    def __setUserName(model, info):
        model.setUserName(info.get('userName', ''))
        model.setClanAbbrev(info.get('clanAbbrev', ''))

    @staticmethod
    def __getRowType(playerData):
        if playerData['isPersonal']:
            rowType = LeaderboardConstants.ROW_TYPE_BR_PLAYER
        elif playerData['isPersonalSquad']:
            rowType = LeaderboardConstants.ROW_TYPE_BR_PLATOON
        else:
            rowType = LeaderboardConstants.ROW_TYPE_BR_ENEMY
        return rowType
