# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_confirm_reroll_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl import backport
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_confirm_reroll_view_model import WtEventConfirmRerollViewModel
from gui.impl.gen.view_models.views.lobby.wt_event.reward_model import RewardModel
from gui.impl.pub import ViewImpl, WindowImpl
from gui.Scaleform.Waiting import Waiting
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.wt_event.wt_event_helpers import getLootBoxRewardTooltipData, fillStatsModel
from helpers import dependency
from skeletons.gui.game_control import IGameEventController, IWalletController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import IEventLootBoxesController
from skeletons.gui.shared import IItemsCache

class WtEventConfirmRerollView(ViewImpl):
    __slots__ = ('__parView', '__lootBoxType', '__tooltipItems', '__price')
    __gameEventController = dependency.descriptor(IGameEventController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __lootBoxesController = dependency.descriptor(IEventLootBoxesController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __wallet = dependency.descriptor(IWalletController)

    def __init__(self, layoutID, parView=None, lootBoxType=None, price=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.OVERLAY_VIEW
        settings.model = WtEventConfirmRerollViewModel()
        self.__parView = parView
        self.__lootBoxType = lootBoxType
        self.__price = price
        self.__tooltipItems = {}
        super(WtEventConfirmRerollView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WtEventConfirmRerollView, self).getViewModel()

    def createToolTip(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId in ('random', 'collection', 'gold', 'vehicles'):
            boxId = self.__lootBoxType
            tooltipData = getLootBoxRewardTooltipData(tooltipId, boxId, gameEventController=self.__gameEventController)
            window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow(), event=event)
            window.load()
            return window
        return super(WtEventConfirmRerollView, self).createToolTip(event)

    @replaceNoneKwargsModel
    def __fillRewards(self, model=None):
        rewards = self.__gameEventController.getLootBoxRewards(self.__lootBoxType)
        for reward in sorted(rewards, reverse=self.__lootBoxType in ('wt_hunter', 'wt_boss')):
            rewardModel = RewardModel()
            if reward.startswith('gold'):
                continue
            else:
                rewardModel.setType(reward)
            model.rewards.addViewModel(rewardModel)

    def _initialize(self, *args, **kwargs):
        super(WtEventConfirmRerollView, self)._initialize(*args, **kwargs)
        self.viewModel.onReopen += self.__onReopen
        self.__itemsCache.onSyncCompleted += self.__updateStats
        self.__wallet.onWalletStatusChanged += self.__updateStats

    def _finalize(self):
        self.__parView.setHasChildOverlay(False)
        super(WtEventConfirmRerollView, self)._finalize()
        self.viewModel.onReopen -= self.__onReopen
        self.__itemsCache.onSyncCompleted -= self.__updateStats
        self.__wallet.onWalletStatusChanged -= self.__updateStats
        self.__parView = None
        self.__lootBoxType = None
        return

    def _onLoaded(self, *args, **kwargs):
        super(WtEventConfirmRerollView, self)._onLoaded(self, *args, **kwargs)
        Waiting.hide('loadPage')

    def _onLoading(self, *args, **kwargs):
        Waiting.show('loadPage')
        self.__parView.setHasChildOverlay(True)
        super(WtEventConfirmRerollView, self)._onLoading()
        with self.getViewModel().transaction() as model:
            if self.__lootBoxType == 'wt_special':
                model.setTitle(backport.text(R.strings.wt_event.confirmReroll.titleWTSpecial()))
            if self.__lootBoxType == 'wt_boss':
                model.setTitle(backport.text(R.strings.wt_event.confirmReroll.titleWTBoss()))
            if self.__lootBoxType == 'wt_hunter':
                model.setTitle(backport.text(R.strings.wt_event.confirmReroll.titleWTHunter()))
            model.setDescription(backport.text(R.strings.wt_event.confirmReroll.description()))
            model.setWarningText(backport.text(R.strings.wt_event.confirmReroll.WTCollectionWarning()))
            model.setBoxId(self.__lootBoxType)
            if self.__price is not None:
                model.setCurrency(self.__price[0])
                model.setReopeningPrice(self.__price[1])
            self.__fillRewards(model=model)
            self.__updateStats(model=model)
        return

    def __onReopen(self):
        self.__parView.onOverlayReopenButton()
        self.destroy()

    @replaceNoneKwargsModel
    def __updateStats(self, *args, **kwargs):
        model = kwargs.get('model')
        if model is not None:
            fillStatsModel(model.stats)
        return


class WtEventConfirmRerollWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None, lootBoxType=None, price=None):
        super(WtEventConfirmRerollWindow, self).__init__(WindowFlags.WINDOW, content=WtEventConfirmRerollView(R.views.lobby.wt_event.WtEventConfirmRerollView(), parView=parent.content, lootBoxType=lootBoxType, price=price), parent=parent)
