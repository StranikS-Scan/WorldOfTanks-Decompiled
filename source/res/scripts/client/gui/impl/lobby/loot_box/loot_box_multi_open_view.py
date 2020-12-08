# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_multi_open_view.py
import logging
from frameworks.wulf import ViewFlags, ViewSettings
from gui import SystemMessages
from gui.impl.auxiliary.rewards_helper import getBackportTooltipData
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.lootboxes.loot_box_multi_open_view_model import LootBoxMultiOpenViewModel
from gui.impl.lobby.loot_box.loot_box_bonuses_helpers import packBonusGroups, RewardsGroup, getLootBoxBonusPacker, isBattleBooster, isConsumable, isCrewBook, getItemsFilter
from gui.impl.lobby.loot_box.loot_box_helper import getTooltipContent, fireHideMultiOpenView, isLootboxValid, LootBoxHideableView, worldDrawEnabled
from gui.impl.lobby.loot_box.loot_box_sounds import setOverlayHangarGeneral
from gui.impl.pub.lobby_window import LobbyOverlay
from gui.server_events.bonuses import getMergedBonusesFromDicts
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events
from gui.shared import g_eventBus
from gui.shared.event_dispatcher import showLootBoxEntry
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from gui.shared.utils import decorators
from helpers import dependency
from items.components.ny_constants import CurrentNYConstants
from skeletons.gui.game_control import IFestivityController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from uilogging.decorators import simpleLog, loggerEntry, loggerTarget
from uilogging.ny.constants import NY_LOG_ACTIONS, NY_LOG_KEYS
from uilogging.ny.loggers import NYLogger
_logger = logging.getLogger(__name__)

@loggerTarget(logKey=NY_LOG_KEYS.NY_LOOT_BOX_OPEN_VIEW, loggerCls=NYLogger)
class LootBoxMultiOpenView(LootBoxHideableView):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    _festivityController = dependency.descriptor(IFestivityController)

    def __init__(self, lootBoxItem, rewards, countToOpen):
        settings = ViewSettings(R.views.lobby.new_year.LootBoxMultiOpenView(), flags=ViewFlags.VIEW, model=LootBoxMultiOpenViewModel())
        super(LootBoxMultiOpenView, self).__init__(settings)
        self.__boxItem = lootBoxItem
        self.__tooltips = {}
        self.__rewards = rewards
        self.__countToOpen = countToOpen

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId is None:
                return
            window = BackportTooltipWindow(self.__tooltips[tooltipId], self.getParentWindow())
            window.load()
            return window
        else:
            return super(LootBoxMultiOpenView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        tooltipData = getBackportTooltipData(event, self.__tooltips)
        return getTooltipContent(event, tooltipData)

    @property
    def viewModel(self):
        return super(LootBoxMultiOpenView, self).getViewModel()

    def _onLoaded(self, *args, **kwargs):
        super(LootBoxMultiOpenView, self)._onLoaded(*args, **kwargs)
        self.getParentWindow().bringToFront()

    @loggerEntry
    def _initialize(self):
        super(LootBoxMultiOpenView, self)._initialize()
        self.viewModel.onCloseBtnClick += self.__onWindowClose
        self.viewModel.onOpenBox += self.__onOpenBox
        self.itemsCache.onSyncCompleted += self.__onCacheResync
        self._festivityController.onStateChanged += self.__onStateChange
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.viewModel.setLimitToOpen(self.__countToOpen)
        self.viewModel.setIsLootboxesEnabled(self.lobbyContext.getServerSettings().isLootBoxesEnabled())
        self.__update()
        self.__setRewards()
        self.__validateOpening()
        if self._isMemoryRiskySystem:
            g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.REMOVE_HIDE_VIEW), EVENT_BUS_SCOPE.LOBBY)
            self._isCanClose = True
            worldDrawEnabled(False)

    def _finalize(self):
        if self._isMemoryRiskySystem:
            worldDrawEnabled(True)
        setOverlayHangarGeneral(False)
        self.viewModel.onCloseBtnClick -= self.__onWindowClose
        self.viewModel.onOpenBox -= self.__onOpenBox
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        self._festivityController.onStateChanged -= self.__onStateChange
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        super(LootBoxMultiOpenView, self)._finalize()

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
    @decorators.process('updating')
    def __onOpenBox(self, params):
        self.__countToOpen = params.get('count', 1)
        result = yield LootBoxOpenProcessor(self.__boxItem, self.__countToOpen).request()
        if result:
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            if result.success:
                self.__rewards = result.auxData
                self.__update()
                self.__setRewards()
                self.__validateOpening()

    def __update(self):
        isValidBox = isLootboxValid(self.__boxItem.getType())
        with self.viewModel.transaction() as tx:
            if isValidBox:
                tx.setOpenedCount(len(self.__rewards))
                tx.setLootboxType(self.__boxItem.getType())
                tx.setBoxesCounter(self.__boxItem.getInventoryCount())
            else:
                tx.setBoxesCounter(0)
                _logger.warning('Lootbox %r is missing on Server!', self.__boxItem)

    def __setRewards(self):
        with self.getViewModel().transaction() as tx:
            bonuses = getMergedBonusesFromDicts(self.__rewards)
            packBonusGroups(bonuses=bonuses, groupModelsList=tx.rewardRows, groupsLayout=self.__getGroupsLayout(), packer=getLootBoxBonusPacker(), tooltipsData=self.__tooltips)
        setOverlayHangarGeneral(True)

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

    def __validateOpening(self):
        if len(self.__rewards) < self.__countToOpen:
            self.viewModel.setIsServerError(True)

    @staticmethod
    def __getGroupsLayout():
        groupNamesRes = R.strings.lootboxes.rewardGroups
        layout = (RewardsGroup(name=groupNamesRes.toys(), bonusTypes=(CurrentNYConstants.TOYS,), bonuses={}, filterFuncs=None),
         RewardsGroup(name=groupNamesRes.consumables(), bonusTypes=('items',), bonuses={}, filterFuncs=(getItemsFilter((isConsumable,)),)),
         RewardsGroup(name=groupNamesRes.crewBooksAndBattleBoosters(), bonusTypes=('items',), bonuses={}, filterFuncs=(getItemsFilter((isBattleBooster, isCrewBook)),)),
         RewardsGroup(name=groupNamesRes.other(), bonusTypes=(), bonuses={}, filterFuncs=None))
        return layout


class LootBoxMultiOpenWindow(LobbyOverlay):
    __slots__ = ()

    def __init__(self, lootBoxItem, rewards, countToOpen, parent=None):
        super(LootBoxMultiOpenWindow, self).__init__(content=LootBoxMultiOpenView(lootBoxItem, rewards, countToOpen), parent=parent)
