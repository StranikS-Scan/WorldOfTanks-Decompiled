# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/seniority_awards/seniority_awards_multi_open_view.py
import logging
from constants import SENIORITY_AWARDS_CONFIG
from frameworks.wulf import ViewFlags, WindowFlags
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.hangar.seniority_awards import getSeniorityAwardsBoxesCount
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport import TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.seniority_awards.seniority_awards_multi_open_renderer_model import SeniorityAwardsMultiOpenRendererModel
from gui.impl.gen.view_models.views.lobby.seniority_awards.seniority_awards_multi_open_view_model import SeniorityAwardsMultiOpenViewModel
from gui.impl.auxiliary.rewards_helper import getProgressiveRewardBonuses
from gui.impl.lobby.seniority_awards.seniority_awards_helper import getLootboxRendererModelPresenter, MAX_BOXES_TO_OPEN, getRewardTooltipContent
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from gui.shared.utils import decorators
from helpers import dependency
from skeletons.gui.game_control import IFestivityController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class SeniorityAwardsMultiOpenView(ViewImpl):
    __COUNT_OPEN_AWARDS = 5
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    _festivityController = dependency.descriptor(IFestivityController)
    __slots__ = ('__boxItem', '__items', '__tooltipIdx', '__exitEvent', '__wasSkipped')

    def __init__(self, *args, **kwargs):
        super(SeniorityAwardsMultiOpenView, self).__init__(R.views.lobby.seniority_awards.seniority_awards_multi_open_view.SeniorityAwardsMultiOpenView(), ViewFlags.VIEW, SeniorityAwardsMultiOpenViewModel, *args, **kwargs)
        self.__exitEvent = None
        self.__items = {}
        self.__tooltipIdx = 0
        self.__boxItem = None
        return

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            window = BackportTooltipWindow(self.__items[tooltipId], self.getParentWindow()) if tooltipId is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return super(SeniorityAwardsMultiOpenView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        return getRewardTooltipContent(event)

    @property
    def viewModel(self):
        return super(SeniorityAwardsMultiOpenView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(SeniorityAwardsMultiOpenView, self)._initialize()
        self.viewModel.onCloseBtnClick += self.__onWindowClose
        self.__boxItem = self.__getSeniorityLootBox()
        self.viewModel.onOpenBoxBtnClick += self.__onOpenNextBoxesBtnClick
        self.itemsCache.onSyncCompleted += self.__onCacheResync
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.viewModel.setLimitToOpen(MAX_BOXES_TO_OPEN)
        self.viewModel.setIsOpenBoxBtnEnabled(self.lobbyContext.getServerSettings().isLootBoxesEnabled())
        self.__openBoxes()

    def _finalize(self):
        self.viewModel.onCloseBtnClick -= self.__onWindowClose
        self.viewModel.onOpenBoxBtnClick -= self.__onOpenNextBoxesBtnClick
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        super(SeniorityAwardsMultiOpenView, self)._finalize()

    def __getSeniorityLootBox(self):
        boxes = self.itemsCache.items.tokens.getLootBoxes()
        for box in boxes.values():
            if box.getType() == 'seniorityAwards':
                return box

        return None

    def __onWindowClose(self, *_):
        if self.__exitEvent is not None:
            g_eventBus.handleEvent(self.__exitEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        else:
            self.destroyWindow()
        return

    def __onCacheResync(self, *_):
        self.__update()

    def __onOpenNextBoxesBtnClick(self):
        self.__openBoxes()

    def __update(self):
        countBoxes = getSeniorityAwardsBoxesCount()
        serverSettings = self.lobbyContext.getServerSettings()
        self.viewModel.setIsOpenBoxBtnEnabled(serverSettings.isLootBoxesEnabled() and countBoxes > 0)
        self.viewModel.setBoxesCounter(countBoxes)

    @decorators.process('updating')
    def __openBoxes(self):
        boxes = self.itemsCache.items.tokens.getLootBoxes().values()
        isValid = False
        for box in boxes:
            if box == self.__boxItem:
                isValid = True
                break

        if isValid:
            countBoxes = getSeniorityAwardsBoxesCount()
            openCount = countBoxes if countBoxes < self.__COUNT_OPEN_AWARDS else self.__COUNT_OPEN_AWARDS
            result = yield LootBoxOpenProcessor(self.__boxItem, openCount).request()
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            if result.success:
                lootBoxList = result.auxData
                if not lootBoxList:
                    _logger.error('Lootbox is opened, but no rewards has been received.')
                    self.__setServerError()
                else:
                    self.__appendRewards(lootBoxList)
            else:
                self.__setServerError()

    def __setServerError(self):
        self.viewModel.setIsServerError(True)

    def __appendRewards(self, rewards):
        with self.viewModel.transaction() as tx:
            lootboxes = tx.getRewards()
            lootboxes.clear()
            idx = 0
            self.__items = {}
            for box in rewards:
                idx += 1
                lootboxes.addViewModel(self.__createLootRewardRenderer(box, idx))

            lootboxes.invalidate()

    def __createLootRewardRenderer(self, lootboxRewards, idx):
        lootboxRewardRenderer = SeniorityAwardsMultiOpenRendererModel()
        lootboxRewardRenderer.setIndx(idx)
        rewardsList = lootboxRewardRenderer.getRewards()
        rewardsList.clear()
        bonuses, _ = getProgressiveRewardBonuses(lootboxRewards, packBlueprints=True)
        for reward in bonuses:
            self.__tooltipIdx += 1
            presenter = getLootboxRendererModelPresenter(reward)
            rewardRender = presenter.getModel(reward, self.__tooltipIdx)
            rewardsList.addViewModel(rewardRender)
            self.__items[self.__tooltipIdx] = TooltipData(tooltip=reward.get('tooltip', None), isSpecial=reward.get('isSpecial', False), specialAlias=reward.get('specialAlias', ''), specialArgs=reward.get('specialArgs', None))

        rewardsList.invalidate()
        return lootboxRewardRenderer

    def __onServerSettingChanged(self, diff):
        configs = {'lootBoxes_config', SENIORITY_AWARDS_CONFIG}
        if configs.intersection(diff):
            self.__update()


class SeniorityAwardsMultiOpenWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(SeniorityAwardsMultiOpenWindow, self).__init__(content=SeniorityAwardsMultiOpenView(*args, **kwargs), wndFlags=WindowFlags.OVERLAY, decorator=None, parent=None)
        return
