# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/friends/resource_box_presenter.py
import logging
from adisp import adisp_process
from constants import PremiumConfigs
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.new_year import new_year_bonus_packer
from gui.impl.new_year.navigation import NewYearNavigation, ViewAliases
from gui.impl.new_year.new_year_bonus_packer import packBonusModelAndTooltipData
from gui.shared import event_dispatcher
from gui.shared.event_dispatcher import hideVehiclePreview
from gui.shared.gui_items.customization.c11n_items import Style
from helpers import dependency
from new_year.ny_constants import NyTabBarFriendGladeView
from new_year.ny_preview import getVehiclePreviewID
from new_year.ny_processor import PiggyBankRewardsProcessor
from ny_common.NYPiggyBankConfig import NYPiggyBankItem
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController, IFriendServiceController
_logger = logging.getLogger(__name__)

class ResourceBoxPresenter(SubModelPresenter):
    __slots__ = ('__piggyBankProgressToken', '__tooltips', '__isInFriendHangar')
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __eventsCache = dependency.descriptor(IEventsCache)
    __nyController = dependency.descriptor(INewYearController)
    __friendsService = dependency.descriptor(IFriendServiceController)

    def __init__(self, viewModel, parentView):
        super(ResourceBoxPresenter, self).__init__(viewModel, parentView)
        self.__piggyBankProgressToken = None
        self.__tooltips = {}
        self.__isInFriendHangar = parentView.getNavigationAlias() == ViewAliases.FRIEND_GLADE_VIEW
        return

    def initialize(self, *args, **kwargs):
        super(ResourceBoxPresenter, self).initialize(*args, **kwargs)
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        self.__updateResourceBoxModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            window = BackportTooltipWindow(self.__tooltips[tooltipId], self.getParentWindow()) if tooltipId is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return super(ResourceBoxPresenter, self).createToolTip(event)

    def finalize(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(ResourceBoxPresenter, self).finalize()

    def update(self):
        self.__updateResourceBoxModel()

    def _getEvents(self):
        events = super(ResourceBoxPresenter, self)._getEvents()
        viewModel = self.getViewModel()
        return events + ((viewModel.onGetReward, self.__onGetReward),
         (viewModel.onStylePreview, self.__onStylePreview),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChange),
         (self.__eventsCache.onSyncCompleted, self.__updateResourceBoxModel))

    def __updateResourceBoxModel(self):
        configItem = self.__config.getItemByIndex(0)
        self.__piggyBankProgressToken = configItem.getDependencies().get('token', {}).keys()[0]
        if not self.__piggyBankProgressToken:
            _logger.error("Couldn't find new year piggy bank progress token")
        with self.getViewModel().transaction() as model:
            hiddenQuests = self.__eventsCache.getHiddenQuests()
            completedQuestsCount = 0
            maxProgressValue = 0
            receivedRewardsCount = 0
            rewards = []
            pointsForAwards = model.getPointsForAwards()
            pointsForAwards.clear()
            tokenCount = self.__itemsCache.items.tokens.getTokenCount(self.__piggyBankProgressToken)
            for configItem in self.__config.getItems():
                conditions = configItem.getDependencies().get('token', {}).values()
                rewardsTokenQuest = None
                if conditions:
                    pointsForAwards.addNumber(conditions[0])
                    maxProgressValue = max(maxProgressValue, conditions[0])
                    rewardTokens = configItem.getRewards().get('tokens', {})
                    if rewardTokens:
                        rewardsTokenQuest = hiddenQuests.get(rewardTokens.keys()[0])
                        ctx = {'tokensCondForReceiveReward': {'currentCount': tokenCount,
                                                        'neededCount': conditions[0],
                                                        'isComplete': rewardsTokenQuest.isCompleted()}}
                        rewards.extend(rewardsTokenQuest.getBonuses(ctx=ctx))
                if rewardsTokenQuest and rewardsTokenQuest.isCompleted():
                    receivedRewardsCount += 1
                if tokenCount >= conditions[0]:
                    completedQuestsCount += 1

            pointsForAwards.invalidate()
            rewardsModel = model.getRewards()
            rewardsModel.clear()
            packBonusModelAndTooltipData(rewards, rewardsModel, new_year_bonus_packer.getChallengeBonusPacker(), self.__tooltips)
            rewardsModel.invalidate()
            model.setMaxProgressValue(maxProgressValue)
            model.setCurrentProgressValue(tokenCount)
            model.setAvailableRewardsCount(completedQuestsCount)
            model.setReceivedRewardsCount(receivedRewardsCount)
        return

    @property
    def __config(self):
        return self.__lobbyContext.getServerSettings().getNewYearPiggyBank()

    @adisp_process
    def __onGetReward(self):
        yield PiggyBankRewardsProcessor().request()

    def __onStylePreview(self, args):
        styleIntCD = int(args.get('intCD'))
        styleItem = self.__itemsCache.items.getItemByCD(styleIntCD)
        if not isinstance(styleItem, Style):
            return

        def _backCallback():
            if self.__nyController.isEnabled():
                hideVehiclePreview(back=False, close=False)
                if self.__isInFriendHangar:
                    NewYearNavigation.switchToFriendView(ViewAliases.FRIEND_GLADE_VIEW, tabName=NyTabBarFriendGladeView.RESOURCES)
                else:
                    NewYearNavigation.switchToView(ViewAliases.FRIENDS_VIEW, force=True)
            else:
                hideVehiclePreview(back=False, close=True)

        if self.__isInFriendHangar:
            self.__friendsService.leaveFriendHangar()
        event_dispatcher.showStylePreview(getVehiclePreviewID(styleItem), styleItem, styleItem.getDescription(), backCallback=_backCallback, showBackBtn=True)

    def __onTokensUpdate(self, tokens):
        if self.__piggyBankProgressToken in tokens:
            self.__updateResourceBoxModel()

    def __onServerSettingsChange(self, diff):
        if PremiumConfigs.PIGGYBANK in diff:
            self.__updateResourceBoxModel()
