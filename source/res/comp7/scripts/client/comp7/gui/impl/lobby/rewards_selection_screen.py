# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/rewards_selection_screen.py
from enum import Enum
import typing
from comp7.gui.impl.gen.view_models.views.lobby.enums import MetaRootViews
from helpers import dependency
from AccountCommands import RES_SUCCESS
from comp7_common_const import COMP7_OFFER_YEARLY_REWARD_TOKEN_PREFIX, offerRewardCategoryToken
from comp7.gui.impl.gen.view_models.views.lobby.rewards_selection_screen_model import RewardsSelectionScreenModel
from comp7.gui.impl.lobby.comp7_helpers.comp7_quest_helpers import getComp7OfferWeeklyQuestsRewardTokenPrefix
from comp7.gui.selectable_reward.common import Comp7SelectableRewardManager
from comp7.gui.shared.event_dispatcher import showComp7SelectedRewardsScreen
from frameworks.wulf import WindowFlags
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.common.selectable_reward_base import SelectableRewardBase
from gui.impl.pub.lobby_window import LobbyWindow
from skeletons.gui.impl import IGuiLoader
if typing.TYPE_CHECKING:
    from typing import Callable, Optional
    from gui.SystemMessages import ResultMsg
WEEKLY_TAB_PARTIAL = 'weekly:'
YEARLY_TAB_PARTIAL = 'yearly:'
TABS_PRIORITY = (WEEKLY_TAB_PARTIAL, '%s%s' % (YEARLY_TAB_PARTIAL, 'modernized'), '%s%s' % (YEARLY_TAB_PARTIAL, 'deluxe'))

class Comp7SelectableRewardType(Enum):
    NONE = 0
    YEARLY = 1
    WEEKLY_QUESTS = 2


class Comp7RewardsSelectionView(SelectableRewardBase):
    _helper = Comp7SelectableRewardManager

    def __init__(self, tokenCondition):
        super(Comp7RewardsSelectionView, self).__init__(R.views.comp7.lobby.RewardsSelectionScreen(), self._helper.getAvailableSelectableBonuses(tokenCondition), RewardsSelectionScreenModel)

    def _processReceivedRewards(self, result):
        if result.success and result.auxData:
            successRewards = result.auxData.get(RES_SUCCESS, {})
            if successRewards:
                showComp7SelectedRewardsScreen(successRewards)
        else:
            SystemMessages.pushI18nMessage(backport.text(R.strings.system_messages.battlePass.rewardChoice.error()), type=SystemMessages.SM_TYPE.Error)
        self.destroyWindow()

    def _getTypesComparator(self):

        def _getPriority(token):
            return next((i for i, value in enumerate(TABS_PRIORITY) if value in token), len(TABS_PRIORITY))

        def _tabsCompare(first, second):
            return _getPriority(first[0]) - _getPriority(second[0])

        return _tabsCompare

    def _getRewardType(self, reward):
        return self._helper.getBonusOfferToken(reward)

    def _getDefaultTab(self):
        tabs = self.viewModel.selectableRewardModel.getTabs()
        metaSelectedTabId = self.__getSelectedMetaTabId()
        pattern = ''
        if metaSelectedTabId == MetaRootViews.WEEKLYQUESTS:
            pattern = WEEKLY_TAB_PARTIAL
        if metaSelectedTabId == MetaRootViews.YEARLYREWARDS:
            pattern = YEARLY_TAB_PARTIAL
        return next((tab for tab in tabs if pattern in tab.getType()), tabs[0])

    @staticmethod
    @dependency.replace_none_kwargs(uiLoader=IGuiLoader)
    def __getSelectedMetaTabId(uiLoader=None):
        contentResId = R.views.comp7.mono.lobby.meta_root_view()
        metaView = uiLoader.windowsManager.getViewByLayoutID(contentResId)
        return metaView.tabId if metaView else None


class Comp7RewardsSelectionWindow(LobbyWindow):
    __slots__ = ('__rewardTokens',)

    def __init__(self, rewardSelectionType=Comp7SelectableRewardType.NONE, category=None):
        if category and category.endswith('_gift'):
            category = category.rsplit('_', 1)[0]
        yearlyToken = COMP7_OFFER_YEARLY_REWARD_TOKEN_PREFIX
        weeklyToken = getComp7OfferWeeklyQuestsRewardTokenPrefix()
        if rewardSelectionType is Comp7SelectableRewardType.NONE:
            self.__rewardTokens = (yearlyToken, weeklyToken)
        elif rewardSelectionType is Comp7SelectableRewardType.WEEKLY_QUESTS:
            self.__rewardTokens = (offerRewardCategoryToken(weeklyToken, category),) if category else (weeklyToken,)
        elif rewardSelectionType is Comp7SelectableRewardType.YEARLY:
            self.__rewardTokens = (offerRewardCategoryToken(yearlyToken, category),) if category else (yearlyToken,)
        else:
            self.__rewardTokens = ()
        super(Comp7RewardsSelectionWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=Comp7RewardsSelectionView(self.tokenCondition))

    def tokenCondition(self, token):
        return not self.__rewardTokens or any((token.startswith(prefix) for prefix in self.__rewardTokens))
