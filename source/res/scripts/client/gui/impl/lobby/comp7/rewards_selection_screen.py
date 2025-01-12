# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/rewards_selection_screen.py
from enum import Enum
import typing
from AccountCommands import RES_SUCCESS
from comp7_common import COMP7_OFFER_YEARLY_REWARD_TOKEN_PREFIX
from frameworks.wulf import WindowFlags
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.rewards_selection_screen_model import RewardsSelectionScreenModel
from gui.impl.lobby.common.selectable_reward_base import SelectableRewardBase
from gui.impl.lobby.comp7.comp7_quest_helpers import getComp7OfferWeeklyQuestsRewardToken
from gui.impl.pub.lobby_window import LobbyWindow
from gui.selectable_reward.common import Comp7SelectableRewardManager
from gui.shared.event_dispatcher import showComp7SelectedRewardsScreen
if typing.TYPE_CHECKING:
    from typing import Callable
    from gui.SystemMessages import ResultMsg

class Comp7SelectableRewardType(Enum):
    NONE = 0
    YEARLY = 1
    WEEKLY_QUESTS = 2


class Comp7RewardsSelectionView(SelectableRewardBase):
    _helper = Comp7SelectableRewardManager

    def __init__(self, tokenCondition):
        self.__onCloseCallback = None
        super(Comp7RewardsSelectionView, self).__init__(R.views.lobby.comp7.RewardsSelectionScreen(), self._helper.getAvailableSelectableBonuses(tokenCondition), RewardsSelectionScreenModel)
        return

    def setNoNotifyViewClosedCallback(self, callback):
        self.__onCloseCallback = callback

    def destroyWindow(self):
        super(Comp7RewardsSelectionView, self).destroyWindow()
        if self.__onCloseCallback:
            self.__onCloseCallback()
            self.__onCloseCallback = None
        return

    def _processReceivedRewards(self, result):
        if result.success and result.auxData:
            successRewards = result.auxData.get(RES_SUCCESS, {})
            if successRewards:
                showComp7SelectedRewardsScreen(successRewards)
        else:
            SystemMessages.pushI18nMessage(backport.text(R.strings.system_messages.battlePass.rewardChoice.error()), type=SystemMessages.SM_TYPE.Error)
        self.destroyWindow()


class Comp7RewardsSelectionWindow(LobbyWindow):
    __slots__ = ('__rewardTokens',)

    def __init__(self, *rewardSelectionTypes):
        tokenByRewardType = {Comp7SelectableRewardType.YEARLY: COMP7_OFFER_YEARLY_REWARD_TOKEN_PREFIX,
         Comp7SelectableRewardType.WEEKLY_QUESTS: getComp7OfferWeeklyQuestsRewardToken()}
        self.__rewardTokens = tuple((token for rewardType, token in tokenByRewardType.iteritems() if rewardType in rewardSelectionTypes))
        super(Comp7RewardsSelectionWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=Comp7RewardsSelectionView(self.tokenCondition))

    def tokenCondition(self, token):
        return not self.__rewardTokens or any((token.startswith(prefix) for prefix in self.__rewardTokens))
