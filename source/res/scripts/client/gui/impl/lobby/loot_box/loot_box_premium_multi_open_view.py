# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_premium_multi_open_view.py
import logging
from adisp import process
from frameworks.wulf import ViewFlags, ViewSettings
from gui import SystemMessages
from gui.impl.auxiliary.rewards_helper import getBackportTooltipData
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport import TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootboxes.components.loot_box_multi_open_renderer_model import LootBoxMultiOpenRendererModel
from gui.impl.gen.view_models.views.lobby.lootboxes.loot_box_premium_multi_open_view_model import LootBoxPremiumMultiOpenViewModel
from gui.impl.lobby.loot_box.loot_box_bonuses_helpers import getFormattedLootboxBonuses, MULTIOPEN_AWARDS_MAX_COUNT
from gui.impl.lobby.loot_box.loot_box_helper import getLootboxRendererModelPresenter, MAX_PREMIUM_BOXES_TO_OPEN, getTooltipContent, fireHideMultiOpenView, showLootBoxSpecialReward, isLootboxValid, LootBoxHideableView, LootBoxShowHideCloseHandler, worldDrawEnabled
from gui.impl.lobby.loot_box.loot_box_sounds import setOverlayHangarGeneral
from gui.impl.pub.lobby_window import LobbyOverlay
from gui.shared import events
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showLootBoxEntry
from gui.shared.events import LootboxesEvent
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from helpers import dependency
from skeletons.gui.game_control import IFestivityController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from uilogging.decorators import simpleLog, loggerEntry, loggerTarget
from uilogging.ny.constants import NY_LOG_ACTIONS, NY_LOG_KEYS
from uilogging.ny.loggers import NYLogger
_logger = logging.getLogger(__name__)

@loggerTarget(logKey=NY_LOG_KEYS.NY_LOOT_BOX_PREMIUM_OPEN_VIEW, loggerCls=NYLogger)
class LootBoxPremiumMultiOpenView(LootBoxHideableView):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    _festivityController = dependency.descriptor(IFestivityController)

    def __init__(self, lootBoxItem, rewards, boxesToOpen):
        settings = ViewSettings(R.views.lobby.loot_box.views.loot_box_premium_multi_open_view.LootBoxPremiumMultiOpenView(), flags=ViewFlags.VIEW, model=LootBoxPremiumMultiOpenViewModel())
        settings.args = (lootBoxItem, rewards, boxesToOpen)
        super(LootBoxPremiumMultiOpenView, self).__init__(settings)
        self.__items = {}
        self.__boxItem = None
        self.__openedCount = 0
        self.__needToOpen = 0
        self.__isOpenNext = True
        self.__currentRewardsPage = 0
        self.__showHideCloseHandler = LootBoxShowHideCloseHandler()
        self.__tooltipIdx = 0
        return

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            window = BackportTooltipWindow(self.__items[tooltipId], self.getParentWindow()) if tooltipId is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return super(LootBoxPremiumMultiOpenView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        tooltipData = getBackportTooltipData(event, self.__items)
        return getTooltipContent(event, tooltipData)

    @property
    def viewModel(self):
        return super(LootBoxPremiumMultiOpenView, self).getViewModel()

    @loggerEntry
    def _initialize(self, *args, **kwargs):
        super(LootBoxPremiumMultiOpenView, self)._initialize()
        self.__showHideCloseHandler.startListen(self.getParentWindow())
        self.viewModel.onCloseBtnClick += self.__onWindowClose
        if args and len(args) == 3:
            self.__boxItem, rewards, self.__needToOpen = args
            self.__currentRewardsPage = 1
            self.viewModel.onOpenBox += self.__onOpenBox
            self.viewModel.onPauseOpening += self.__onPauseOpening
            self.viewModel.onContinueOpening += self.__onContinueOpening
            self.viewModel.openNextBoxes += self.__openNextBoxes
            self.itemsCache.onSyncCompleted += self.__onCacheResync
            self._festivityController.onStateChanged += self.__onStateChange
            self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
            self.viewModel.showSpecialReward += self.__showSpecialReward
            self.viewModel.onViewShowed += self.__onViewShowed
            g_eventBus.addListener(LootboxesEvent.ON_SHOW_SPECIAL_REWARDS_CLOSED, self.__onSpecialRewardsClosed, scope=EVENT_BUS_SCOPE.LOBBY)
            with self.viewModel.transaction() as model:
                model.setLimitToOpen(MAX_PREMIUM_BOXES_TO_OPEN)
                model.setIsLootboxesEnabled(self.lobbyContext.getServerSettings().isLootBoxesEnabled())
                model.setIsMemoryRiskySystem(self._isMemoryRiskySystem)
            self.__update()
            self.__appendRewards(rewards[0], forceClearPage=True)
            setOverlayHangarGeneral(True)
        else:
            _logger.error('Rewards and boxItem is not specified!')
            self.viewModel.setHardReset(True)

    def _finalize(self):
        if self._isMemoryRiskySystem:
            worldDrawEnabled(True)
        setOverlayHangarGeneral(False)
        self.__showHideCloseHandler.stopListen()
        self.__showHideCloseHandler = None
        self.viewModel.onCloseBtnClick -= self.__onWindowClose
        self.viewModel.onOpenBox -= self.__onOpenBox
        self.viewModel.onPauseOpening -= self.__onPauseOpening
        self.viewModel.onContinueOpening -= self.__onContinueOpening
        self.viewModel.openNextBoxes -= self.__openNextBoxes
        self.viewModel.onViewShowed -= self.__onViewShowed
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        self.viewModel.showSpecialReward -= self.__showSpecialReward
        self._festivityController.onStateChanged -= self.__onStateChange
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        g_eventBus.removeListener(LootboxesEvent.ON_SHOW_SPECIAL_REWARDS_CLOSED, self.__onSpecialRewardsClosed, scope=EVENT_BUS_SCOPE.LOBBY)
        super(LootBoxPremiumMultiOpenView, self)._finalize()
        return

    def __onWindowClose(self, *_):
        if self._isMemoryRiskySystem:
            if not self._isCanClose:
                return
            self._startFade(self.__showEntryAndDestroy, withPause=True)
        else:
            fireHideMultiOpenView()
            self.destroyWindow()

    def __showEntryAndDestroy(self):
        showLootBoxEntry(category=self.__boxItem.getCategory(), lootBoxType=self.__boxItem.getType())
        self.destroyWindow()

    def __onCacheResync(self, *_):
        self.__update()

    @simpleLog(action=NY_LOG_ACTIONS.NY_LOOT_BOX_OPEN_NEXT_BOXES)
    def __openNextBoxes(self, *_):
        self.viewModel.setIsOnPause(False)
        self.__openedCount = 0
        self.__needToOpen = min(LootBoxPremiumMultiOpenViewModel.WINDOW_MAX_BOX_COUNT, self.__boxItem.getInventoryCount())
        self.__onOpenBox(None)
        return

    def __onOpenBox(self, *_):
        if self.__openedCount < self.__needToOpen:
            self.__isOpenNext = True
            self.__validateNextLootBox()

    def __validateNextLootBox(self):
        if self.__isOpenNext and not self.viewModel.getIsOnPause():
            forceClearPage = False
            if len(self.viewModel.getRewards()) >= LootBoxPremiumMultiOpenViewModel.WINDOW_MAX_BOX_COUNT:
                forceClearPage = True
                self.__currentRewardsPage += 1
                self.__tooltipIdx = 0
            self.__openNextBox(forceClearPage)
            self.__isOpenNext = False

    def __setServerError(self):
        self.viewModel.setIsServerError(True)

    def __onPauseOpening(self):
        self.viewModel.setIsOnPause(True)

    def __onContinueOpening(self):
        self.viewModel.setIsOnPause(False)
        self.__validateNextLootBox()

    def __showSpecialReward(self, responseDict):
        self.__onPauseOpening()
        showLootBoxSpecialReward(responseDict, self.getParentWindow())

    def __onViewShowed(self):
        if self._isMemoryRiskySystem:
            g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.REMOVE_HIDE_VIEW), EVENT_BUS_SCOPE.LOBBY)
            self._isCanClose = True
            worldDrawEnabled(False)
            return
        g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.NEED_STOP_ENTRY_VIDEO), EVENT_BUS_SCOPE.LOBBY)

    def __onSpecialRewardsClosed(self, _):
        self.__onContinueOpening()
        self.viewModel.setIsPausedForSpecial(False)

    def __update(self):
        isValidBox = isLootboxValid(self.__boxItem.getType())
        with self.viewModel.transaction() as tx:
            if isValidBox:
                tx.setLeftToOpenCount(self.__needToOpen - self.__openedCount)
                tx.setNeedToOpen(self.__needToOpen)
                tx.setBoxCategory(self.__boxItem.getCategory())
                tx.setBoxesCounter(self.__boxItem.getInventoryCount())
            else:
                tx.setBoxesCounter(0)
                _logger.warning('Lootbox %r is missing on Server!', self.__boxItem)

    @process
    def __openNextBox(self, forceClearPage=False):
        result = yield LootBoxOpenProcessor(self.__boxItem, 1).request()
        if result:
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            if result.success:
                rewardsList = result.auxData
                if not rewardsList:
                    _logger.error('Lootbox is opened, but no rewards has been received.')
                    self.__setServerError()
                else:
                    self.__appendRewards(rewardsList[0], forceClearPage)
            else:
                self.__setServerError()
        else:
            self.__setServerError()

    def __appendRewards(self, rewards, forceClearPage=False):
        self.__openedCount += 1
        with self.getViewModel().transaction() as tx:
            tx.setLeftToOpenCount(self.__needToOpen - self.__openedCount)
            lootboxes = tx.getRewards()
            if forceClearPage:
                lootboxes.clear()
                tx.setCurrentPage(self.__currentRewardsPage)
                lootboxes.invalidate()
            lootboxes.addViewModel(self.__createLootRewardRenderer(rewards, idx=self.__openedCount))
            lootboxes.invalidate()

    def __createLootRewardRenderer(self, lootboxRewards, idx):
        lootboxRewardRenderer = LootBoxMultiOpenRendererModel()
        lootboxRewardRenderer.setIndx(idx)
        rewardsList = lootboxRewardRenderer.getRewards()
        rewardsList.clear()
        bonuses, _ = getFormattedLootboxBonuses(lootboxRewards, MULTIOPEN_AWARDS_MAX_COUNT)
        for reward in bonuses:
            presenter = getLootboxRendererModelPresenter(reward)
            rewardRender = presenter.getModel(reward, self.__tooltipIdx)
            rewardsList.addViewModel(rewardRender)
            self.__items[self.__tooltipIdx] = TooltipData(tooltip=reward.get('tooltip', None), isSpecial=reward.get('isSpecial', False), specialAlias=reward.get('specialAlias', ''), specialArgs=reward.get('specialArgs', None))
            self.__tooltipIdx += 1

        rewardsList.invalidate()
        return lootboxRewardRenderer

    def __onServerSettingChanged(self, diff):
        if 'lootBoxes_config' in diff:
            if not self.lobbyContext.getServerSettings().isLootBoxEnabled(self.__boxItem.getID()):
                self.__onWindowClose()
                return
            self.__update()
        self.viewModel.setIsLootboxesEnabled(self.lobbyContext.getServerSettings().isLootBoxesEnabled())

    def __onStateChange(self):
        if not self._festivityController.isEnabled():
            self.destroyWindow()


class LootBoxPremiumMultiOpenWindow(LobbyOverlay):
    __slots__ = ()

    def __init__(self, lootBoxItem, rewards, boxesToOpen, parent=None):
        super(LootBoxPremiumMultiOpenWindow, self).__init__(content=LootBoxPremiumMultiOpenView(lootBoxItem, rewards, boxesToOpen), decorator=None, parent=parent)
        return
