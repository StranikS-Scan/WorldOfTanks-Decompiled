# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/views/rewards_screen.py
from collections import namedtuple
import typing
from frameworks.wulf import ViewSettings, WindowFlags
from frameworks.wulf.view.array import fillViewModelsArray
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.views.rewards_screen_model import Type, Rank, RewardsScreenModel
from gui.impl.lobby.comp7.comp7_bonus_packer import packRanksRewardsQuestBonuses, packTokensRewardsQuestBonuses
from gui.impl.lobby.comp7.comp7_quest_helpers import parseComp7RanksQuestID, parseComp7TokensQuestID, parseComp7PeriodicQuestID
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from shared_utils import findFirst
from gui.impl.lobby.comp7 import comp7_shared
if typing.TYPE_CHECKING:
    from comp7_ranks_common import Comp7Division
    from frameworks.wulf.view.view_event import ViewEvent
    from gui.server_events.event_items import TokenQuest
_RANKS_MAIN_REWARDS_COUNT = {Rank.FIRST: 1,
 Rank.SECOND: 3,
 Rank.THIRD: 2,
 Rank.FOURTH: 3,
 Rank.FIFTH: 2,
 Rank.SIXTH: 3,
 Rank.SEVENTH: 4}
_WINS_MAIN_REWARDS_COUNT = 4
_BonusData = namedtuple('_BonusData', ('bonus', 'tooltip'))

class _BaseRewardsView(ViewImpl):
    __slots__ = ('_bonusData',)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.comp7.views.RewardsScreen())
        settings.model = RewardsScreenModel()
        settings.args = args
        settings.kwargs = kwargs
        super(_BaseRewardsView, self).__init__(settings)
        self._bonusData = []

    @property
    def viewModel(self):
        return super(_BaseRewardsView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId is not None:
                bonusData = self._bonusData[int(tooltipId)]
                window = BackportTooltipWindow(bonusData.tooltip, self.getParentWindow())
                window.load()
                return window
        return super(_BaseRewardsView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            showCount = int(event.getArgument('showCount'))
            showCount += self._getMainRewardsCount()
            bonuses = [ d.bonus for d in self._bonusData[showCount:] ]
            return AdditionalRewardsTooltip(bonuses)
        else:
            return None

    def _initialize(self, *args, **kwargs):
        super(_BaseRewardsView, self)._initialize(*args, **kwargs)
        self._addListeners()

    def _finalize(self):
        self._removeListeners()
        self._bonusData = None
        super(_BaseRewardsView, self)._finalize()
        return

    def _onLoading(self, quest, *args, **kwargs):
        super(_BaseRewardsView, self)._onLoading(*args, **kwargs)
        self._setModelData(quest, *args, **kwargs)

    def _setModelData(self, quest, *args, **kwargs):
        raise NotImplementedError

    def _packQuestBonuses(self, quest):
        raise NotImplementedError

    def _getMainRewardsCount(self):
        raise NotImplementedError

    def _setRewards(self, model, quest):
        packedBonuses, tooltipsData = self._packQuestBonuses(quest)
        self._bonusData = []
        for idx, (packedBonus, tooltipData) in enumerate(zip(packedBonuses, tooltipsData)):
            packedBonus.setTooltipId(str(idx))
            self._bonusData.append(_BonusData(packedBonus, tooltipData))

        mainRewardsCount = self._getMainRewardsCount()
        fillViewModelsArray(packedBonuses[:mainRewardsCount], model.getMainRewards())
        fillViewModelsArray(packedBonuses[mainRewardsCount:], model.getAdditionalRewards())

    def _addListeners(self):
        self.viewModel.onClose += self._onClose

    def _removeListeners(self):
        self.viewModel.onClose -= self._onClose

    def _onClose(self):
        self.destroyWindow()


class RanksRewardsView(_BaseRewardsView):
    __slots__ = ('__division', '__periodicQuests')

    def __init__(self, *args, **kwargs):
        super(RanksRewardsView, self).__init__(*args, **kwargs)
        self.__division = None
        self.__periodicQuests = None
        return

    def _packQuestBonuses(self, quest):
        periodicQuest = findFirst(lambda q: parseComp7PeriodicQuestID(q.getID()) == self.__division, self.__periodicQuests)
        return packRanksRewardsQuestBonuses(quest=quest, periodicQuest=periodicQuest)

    def _setModelData(self, quest, periodicQuests):
        with self.viewModel.transaction() as vm:
            self.__division = parseComp7RanksQuestID(quest.getID())
            self.__periodicQuests = periodicQuests
            rankValue = comp7_shared.getRankEnumValue(self.__division)
            divisionValue = comp7_shared.getDivisionEnumValue(self.__division)
            vm.setType(self._getType(rankValue))
            vm.setRank(rankValue)
            vm.setDivision(divisionValue)
            vm.setHasRankInactivity(comp7_shared.hasRankInactivity(self.__division.rank))
            self._setRewards(vm, quest)

    def _getMainRewardsCount(self):
        rankValue = comp7_shared.getRankEnumValue(self.__division)
        return _RANKS_MAIN_REWARDS_COUNT.get(rankValue, 0)

    def _onClose(self):
        if self.viewModel.getType() == Type.RANK:
            self.viewModel.setType(Type.RANKREWARDS)
        else:
            self.destroyWindow()

    def _getType(self, rankValue):
        if self.__isFirstRankReward(rankValue):
            return Type.FIRSTRANKREWARDS
        return Type.RANK if self.__isRankUpgrade(self.__division) else Type.DIVISION

    def __isFirstRankReward(self, rankValue):
        return rankValue == Rank.FIRST and self.__division.index == 0

    @staticmethod
    def __isRankUpgrade(division):
        return division.index == 0


class TokensRewardsView(_BaseRewardsView):
    __slots__ = ('__tokensCount',)

    def __init__(self, *args, **kwargs):
        super(TokensRewardsView, self).__init__(*args, **kwargs)
        self.__tokensCount = None
        return

    def _packQuestBonuses(self, quest):
        return packTokensRewardsQuestBonuses(quest=quest)

    def _setModelData(self, quest):
        self.__tokensCount = parseComp7TokensQuestID(quest.getID())
        with self.viewModel.transaction() as vm:
            vm.setType(Type.TOKENSREWARDS)
            vm.setTokensCount(self.__tokensCount)
            self._setRewards(vm, quest)

    def _getMainRewardsCount(self):
        return _WINS_MAIN_REWARDS_COUNT


class RanksRewardsScreenWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, quest, periodicQuests, parent=None):
        super(RanksRewardsScreenWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=RanksRewardsView(quest, periodicQuests), parent=parent)


class TokensRewardsScreenWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, quest, parent=None):
        super(TokensRewardsScreenWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=TokensRewardsView(quest), parent=parent)
