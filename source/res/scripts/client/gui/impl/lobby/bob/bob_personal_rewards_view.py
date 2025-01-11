# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/bob/bob_personal_rewards_view.py
import logging
import SoundGroups
from chat_shared import SYS_MESSAGE_TYPE
from frameworks.wulf import ViewSettings
from gui.battle_pass.sounds import BattlePassSounds
from gui.bob.bob_bonuses_packers import packBonusModelAndTooltipData
from gui.impl import backport
from gui.impl.auxiliary.rewards_helper import getBobTeamRewardsBonuses
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.bob.bob_personal_rewards_view_model import BobPersonalRewardsViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from helpers import dependency
from messenger.proto.events import g_messengerEvents
from skeletons.gui.game_control import IBobController
_logger = logging.getLogger(__name__)

class BobPersonalRewardView(ViewImpl):
    __slots__ = ('__tooltipItems', '__tooltipWindow')
    __bobController = dependency.descriptor(IBobController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.bob.BobPersonalRewardsView())
        settings.model = BobPersonalRewardsViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__tooltipItems = {}
        self.__tooltipWindow = None
        super(BobPersonalRewardView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(BobPersonalRewardView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId is None:
                return
            tooltipData = self.__tooltipItems.get(tooltipId)
            if tooltipData is None:
                return
            window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
            self.__tooltipWindow = window
            window.load()
            return window
        else:
            return super(BobPersonalRewardView, self).createToolTip(event)

    def _initialize(self, *args, **kwargs):
        g_messengerEvents.serviceChannel.onChatMessageReceived += self.__onChatMessageReceived
        self.__bobController.onTokensUpdated += self.__onTokensUpdated
        self.viewModel.onOpenNext += self.__onOpenNext

    def _onLoading(self, bonuses, *args, **kwargs):
        super(BobPersonalRewardView, self)._onLoading(*args, **kwargs)
        self.viewModel.setTitle(backport.text(R.strings.bob.personalReward.title()))
        self.__updateViewModel(bonuses)
        SoundGroups.g_instance.playSound2D(BattlePassSounds.REWARD_SCREEN)

    def _finalize(self):
        g_messengerEvents.serviceChannel.onChatMessageReceived -= self.__onChatMessageReceived
        self.__bobController.onTokensUpdated -= self.__onTokensUpdated
        self.viewModel.onOpenNext -= self.__onOpenNext
        self.__clearTooltips()

    def __updateViewModel(self, bonuses):
        self.__clearTooltips()
        with self.getViewModel().transaction() as model:
            self.__updateAvailableCount(model=model)
            model.rewards.clearItems()
            packBonusModelAndTooltipData(bonuses, model.rewards, self.__tooltipItems)

    @replaceNoneKwargsModel
    def __updateAvailableCount(self, model=None):
        model.setAvailableCount(self.__bobController.getAvailablePersonalRewardCount())

    def __onOpenNext(self):
        self.__bobController.claimReward(self.__bobController.tokenToClaimPersonalReward)

    def __onChatMessageReceived(self, *args):
        _, message = args
        isRightMessage = message is not None and message.type == SYS_MESSAGE_TYPE.tokenQuests.index() and message.data
        if not isRightMessage:
            return
        else:
            rewards = message.data.get('detailedRewards', {}).get(self.__bobController.personalRewardQuestName, {})
            if rewards:
                bonuses = getBobTeamRewardsBonuses(rewards)
                if bonuses:
                    self.__updateViewModel(bonuses)
                else:
                    _logger.error('Could not show empty bonuses')
            return

    def __onTokensUpdated(self):
        self.__updateAvailableCount()

    def __clearTooltips(self):
        self.__tooltipItems.clear()
        if self.__tooltipWindow is not None:
            self.__tooltipWindow.destroy()
            self.__tooltipWindow = None
        return


class BobPersonalRewardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, bonuses):
        super(BobPersonalRewardWindow, self).__init__(content=BobPersonalRewardView(bonuses))
