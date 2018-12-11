# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_multi_open_view.py
import logging
from frameworks.wulf import ViewFlags, WindowFlags
from gui import SystemMessages
from gui.impl.backport_tooltip import BackportTooltipWindow, TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.loot_box_multi_open_view_model import LootBoxMultiOpenViewModel
from gui.impl.gen.view_models.views.loot_box_view.loot_box_multi_open_renderer_model import LootBoxMultiOpenRendererModel
from gui.impl.lobby.loot_box.loot_box_helper import getLootboxRendererModelPresenter, MAX_BOXES_TO_OPEN, getRewardTooltipContent, fireHideMultiOpenView, getLootboxBonuses, showLootBoxSpecialReward, LootBoxShowHideCloseHandler
from gui.impl.pub import LobbyWindow
from gui.impl.pub import ViewImpl
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import LootboxesEvent
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from gui.shared.utils import decorators
from helpers import dependency
from skeletons.gui.game_control import IFestivityController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

class LootBoxMultiOpenView(ViewImpl):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    _festivityController = dependency.descriptor(IFestivityController)
    __slots__ = ('__rewards', '__boxItem', '__items', '__showHideCloseHandler')

    def __init__(self, *args, **kwargs):
        super(LootBoxMultiOpenView, self).__init__(R.views.lootBoxMultiOpenView, ViewFlags.VIEW, LootBoxMultiOpenViewModel, *args, **kwargs)
        self.__items = {}
        self.__rewards = []
        self.__boxItem = None
        self.__showHideCloseHandler = LootBoxShowHideCloseHandler()
        return

    def createToolTip(self, event):
        if event.contentID == R.views.backportTooltipContent:
            tooltipId = event.getArgument('tooltipId')
            window = BackportTooltipWindow(self.__items[tooltipId], self.getParentWindow()) if tooltipId is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return super(LootBoxMultiOpenView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        return getRewardTooltipContent(event)

    @property
    def viewModel(self):
        return super(LootBoxMultiOpenView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(LootBoxMultiOpenView, self)._initialize()
        self.__showHideCloseHandler.startListen(self.getParentWindow())
        self.viewModel.onCloseBtnClick += self.__onWindowClose
        if args and len(args) == 2:
            self.__boxItem = args[0]
            self.__rewards = args[1]
            self.viewModel.onOpenBoxBtnClick += self.__onOpenBox
            self.viewModel.onReadyToRestart += self.__onReadyToRestart
            self.itemsCache.onSyncCompleted += self.__onCacheResync
            self._festivityController.onStateChanged += self.__onStateChange
            self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
            self.viewModel.showSpecialReward += self.__showSpecialReward
            g_eventBus.addListener(LootboxesEvent.ON_SHOW_SPECIAL_REWARDS_CLOSED, self.__onSpecialRewardsClosed, scope=EVENT_BUS_SCOPE.LOBBY)
            self.viewModel.setLimitToOpen(MAX_BOXES_TO_OPEN)
            self.viewModel.setIsOpenBoxBtnEnabled(self.lobbyContext.getServerSettings().isLootBoxesEnabled())
            self.__update()
            self.__setRewards()
        else:
            _logger.error('Rewards and boxItem is not specified!')
            self.viewModel.setHardReset(True)

    def _finalize(self):
        self.__showHideCloseHandler.stopListen()
        self.__showHideCloseHandler = None
        self.viewModel.onCloseBtnClick -= self.__onWindowClose
        self.viewModel.onOpenBoxBtnClick -= self.__onOpenBox
        self.viewModel.onReadyToRestart -= self.__onReadyToRestart
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        self.viewModel.showSpecialReward -= self.__showSpecialReward
        self._festivityController.onStateChanged -= self.__onStateChange
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        g_eventBus.removeListener(LootboxesEvent.ON_SHOW_SPECIAL_REWARDS_CLOSED, self.__onSpecialRewardsClosed, scope=EVENT_BUS_SCOPE.LOBBY)
        super(LootBoxMultiOpenView, self)._finalize()
        return

    def __onWindowClose(self, *_):
        fireHideMultiOpenView()
        self.destroyWindow()

    def __onCacheResync(self, *_):
        self.__update()

    @decorators.process('updating')
    def __onOpenBox(self, params):
        count = params.get('count', 1)
        result = yield LootBoxOpenProcessor(self.__boxItem, count).request()
        if result:
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            if result.success:
                self.__rewards = result.auxData
                self.viewModel.setRestart(True)

    def __showSpecialReward(self, responseDict):
        showLootBoxSpecialReward(responseDict)

    def __onSpecialRewardsClosed(self, _):
        self.viewModel.setIsCanNext(True)

    def __onReadyToRestart(self, *_):
        self.__update()
        self.__setRewards()
        self.viewModel.setRestart(False)

    def __update(self):
        isValidBox = False
        boxes = self.itemsCache.items.tokens.getLootBoxes().values()
        for box in boxes:
            if box == self.__boxItem:
                isValidBox = True
                break

        with self.viewModel.transaction() as tx:
            if isValidBox:
                tx.setOpenedCount(len(self.__rewards))
                tx.setLootboxType(self.__boxItem.getType())
                tx.setBoxCategory(self.__boxItem.getCategory())
                tx.setIsFreeBox(self.__boxItem.isFree())
                tx.setBoxesCounter(self.__boxItem.getInventoryCount())
            else:
                tx.setBoxesCounter(0)
                _logger.warning('Lootbox %r is missing on Server!', self.__boxItem)

    def __setRewards(self):
        with self.getViewModel().transaction() as tx:
            lootboxes = tx.getRewards()
            lootboxes.clear()
            tooltipIdx = 0
            for idx, lootboxRewards in enumerate(self.__rewards):
                lootboxRewardRenderer = LootBoxMultiOpenRendererModel()
                lootboxRewardRenderer.setIndx(idx + 1)
                rewardsList = lootboxRewardRenderer.getRewards()
                rewardsList.clear()
                bonuses, _ = getLootboxBonuses(lootboxRewards, size='small')
                for reward in bonuses:
                    presenter = getLootboxRendererModelPresenter(reward)
                    rewardRender = presenter.getModel(reward, tooltipIdx, isSmall=True)
                    rewardsList.addViewModel(rewardRender)
                    self.__items[tooltipIdx] = TooltipData(tooltip=reward.get('tooltip', None), isSpecial=reward.get('isSpecial', False), specialAlias=reward.get('specialAlias', ''), specialArgs=reward.get('specialArgs', None))
                    tooltipIdx += 1

                rewardsList.invalidate()
                lootboxes.addViewModel(lootboxRewardRenderer)

            lootboxes.invalidate()
        return

    def __onServerSettingChanged(self, diff):
        if 'lootBoxes_config' in diff:
            self.__update()
        self.viewModel.setIsOpenBoxBtnEnabled(self.lobbyContext.getServerSettings().isLootBoxesEnabled())

    def __onStateChange(self):
        if not self._festivityController.isEnabled():
            self.destroyWindow()


class LootBoxMultiOpenWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(LootBoxMultiOpenWindow, self).__init__(content=LootBoxMultiOpenView(*args, **kwargs), wndFlags=WindowFlags.OVERLAY, decorator=None, parent=None)
        return
