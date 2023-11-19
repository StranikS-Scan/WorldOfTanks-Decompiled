# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_lootboxes/scripts/client/event_lootboxes/gui/impl/lobby/event_lootboxes/popover.py
from PlayerEvents import g_playerEvents
from event_lootboxes.gui.impl.gen.view_models.views.lobby.event_lootboxes.popover_model import PopoverModel
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags
from tooltips.loot_box_tooltip import EventLootBoxTooltip
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.impl.pub import PopOverViewImpl
from event_lootboxes.gui.shared.event_dispatcher import showEventLootBoxOpenErrorWindow, showEventLootBoxOpenWindow, showEventLootBoxesWelcomeScreen
from gui.shared.gui_items.loot_box import EVENT_LOOT_BOXES_CATEGORY, EventLootBoxes
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils import decorators
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency
from helpers.time_utils import ONE_MINUTE, ONE_SECOND, getServerUTCTime
from skeletons.gui.game_control import IEntitlementsController, IEventLootBoxesController
from wg_async import wg_async, wg_await
_LOOT_BOX_COUNTER_ENTITLEMENT = 'loot_box_counter'

class EventLootBoxesPopover(PopOverViewImpl):
    __slots__ = ('__popoverNotifier', '__hasBuyableBoxes', '__statisticsInUpdating')
    __eventLootBoxes = dependency.descriptor(IEventLootBoxesController)
    __entitlements = dependency.descriptor(IEntitlementsController)

    def __init__(self):
        super(EventLootBoxesPopover, self).__init__(ViewSettings(R.views.event_lootboxes.lobby.event_lootboxes.PopoverView(), ViewFlags.VIEW, PopoverModel()))
        self.__popoverNotifier = SimpleNotifier(self.__getTimeToBuyStatusUpdate, self.__buyStatusUpdated)
        self.__hasBuyableBoxes = False
        self.__statisticsInUpdating = False

    @property
    def viewModel(self):
        return super(EventLootBoxesPopover, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return EventLootBoxTooltip(boxType=EventLootBoxes.PREMIUM) if contentID == R.views.event_lootboxes.lobby.event_lootboxes.tooltips.LootBoxesTooltip() else super(EventLootBoxesPopover, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        return ((g_playerEvents.onDisconnected, self.__onDisconnected),
         (self.viewModel.onOpenBtnClick, self.__onOpenBtnClick),
         (self.viewModel.onBuyBtnClick, self.__onBuyBtnClick),
         (self.viewModel.onAboutBtnClick, self.__onAboutBtnClick),
         (self.__eventLootBoxes.onAvailabilityChange, self.__onAvailabilityChange),
         (self.__eventLootBoxes.onBoxesCountChange, self.__onBoxesCountChange),
         (self.__eventLootBoxes.onStatusChange, self.__onEventStatusChange),
         (self.__entitlements.onCacheUpdated, self.__onEntitlementsCacheUpdated))

    def _onLoading(self, *args, **kwargs):
        super(EventLootBoxesPopover, self)._onLoading(*args, **kwargs)
        self.__initializeLootBoxes()

    def _finalize(self):
        self.__statisticsInUpdating = False
        self.__popoverNotifier.stopNotification()
        super(EventLootBoxesPopover, self)._finalize()

    def __initializeLootBoxes(self):
        self.__buyStatusUpdated()
        if self.__eventLootBoxes.getDayLimit() <= self.__eventLootBoxes.getDayInfoStatistics() and self.__eventLootBoxes.isLootBoxesAvailable():
            self.__popoverNotifier.startNotification()
        self.viewModel.setMaxBoxesAvailableToBuy(self.__eventLootBoxes.getDayLimit())
        self.__updateBoxesCount()
        if not self.__entitlements.isCacheInited():
            self.__updateStatistics()

    @decorators.adisp_process('updating')
    def __onOpenBtnClick(self):
        lootBox = self.__eventLootBoxes.getStoreInfo(EVENT_LOOT_BOXES_CATEGORY).get(EventLootBoxes.PREMIUM, None)
        if self.__eventLootBoxes.isLootBoxesAvailable() and lootBox is not None and lootBox.getInventoryCount() > 0:
            result = yield LootBoxOpenProcessor(lootBox, 1).request()
            self.destroyWindow()
            if result and result.success and result.auxData is not None:
                showEventLootBoxOpenWindow(lootBox.getType(), rewards=result.auxData)
            else:
                showEventLootBoxOpenErrorWindow()
        elif not self.__eventLootBoxes.isLootBoxesAvailable():
            SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.lootboxes.open.server_error.DISABLED()), priority=NotificationPriorityLevel.MEDIUM, type=SystemMessages.SM_TYPE.Error)
        return

    def __onBuyBtnClick(self):
        self.destroyWindow()
        self.__eventLootBoxes.openShop()

    def __onAboutBtnClick(self):
        self.destroyWindow()
        showEventLootBoxesWelcomeScreen()

    def __updateBoxesCount(self):
        availableToBuyBoxes = self.__eventLootBoxes.getDayLimit() - self.__eventLootBoxes.getDayInfoStatistics()
        self.__hasBuyableBoxes = availableToBuyBoxes > 0
        lb = self.__eventLootBoxes.getStoreInfo(EVENT_LOOT_BOXES_CATEGORY).get(EventLootBoxes.PREMIUM, None)
        lootBoxCount = lb.getInventoryCount() if lb is not None else 0
        with self.viewModel.transaction() as tx:
            tx.setCount(lootBoxCount)
            tx.setIsOpenAvailable(lootBoxCount > 0 and self.__eventLootBoxes.isLootBoxesAvailable())
            tx.setIsBuyAvailable(self.__eventLootBoxes.isBuyAvailable())
            tx.setBoxesAvailableToBuy(availableToBuyBoxes)
            tx.setEventExpireTime(self.__getEventExpireTime())
            tx.setMainRewardBoxesLeft(self.__eventLootBoxes.boxCountToGuaranteedBonus)
            tx.setGuaranteedLimit(self.__eventLootBoxes.getGuaranteedBonusLimit(EventLootBoxes.PREMIUM))
        return

    def __onAvailabilityChange(self, *_):
        if self.__eventLootBoxes.isLootBoxesAvailable():
            self.__popoverNotifier.startNotification()
        else:
            self.__popoverNotifier.stopNotification()
        self.__initializeLootBoxes()

    def __onBoxesCountChange(self, *_):
        self.__updateBoxesCount()

    def __getTimeToBuyStatusUpdate(self):
        dayTimeLeft = self.__eventLootBoxes.getTimeLeftToResetPurchase() + ONE_SECOND
        return dayTimeLeft % ONE_MINUTE or ONE_MINUTE

    def __buyStatusUpdated(self):
        isLootBoxesAvailable = self.__eventLootBoxes.isLootBoxesAvailable()
        availableToBuyBoxes = self.__eventLootBoxes.getDayLimit() - self.__eventLootBoxes.getDayInfoStatistics()
        dayTimeLeft = self.__eventLootBoxes.getTimeLeftToResetPurchase()
        _, finish = self.__eventLootBoxes.getEventActiveTime()
        isLastEventDay = finish - getServerUTCTime() <= dayTimeLeft
        hasErrors = not (self.__entitlements.isCacheInited() and isLootBoxesAvailable)
        if availableToBuyBoxes and not hasErrors:
            buyingEnableTime = 0
        elif not hasErrors:
            buyingEnableTime = dayTimeLeft
        else:
            buyingEnableTime = dayTimeLeft if dayTimeLeft > ONE_MINUTE else 0
        with self.viewModel.transaction() as tx:
            tx.setIsLootBoxesAvailable(isLootBoxesAvailable)
            tx.setIsLastEventDay(isLastEventDay)
            tx.setHasErrors(hasErrors)
            tx.setBuyingEnableTime(buyingEnableTime)
            tx.setIsBuyAvailable(self.__eventLootBoxes.isBuyAvailable())
            tx.setBoxesAvailableToBuy(availableToBuyBoxes)
            tx.setUseExternalShop(self.__eventLootBoxes.useExternalShop())
            hasBuyableBoxes = availableToBuyBoxes > 0
            if isLastEventDay or hasBuyableBoxes:
                self.__popoverNotifier.stopNotification()
            if hasBuyableBoxes != self.__hasBuyableBoxes:
                self.__updateBoxesCount()

    def __getEventExpireTime(self):
        _, finish = self.__eventLootBoxes.getEventActiveTime()
        return finish - getServerUTCTime()

    @wg_async
    def __updateStatistics(self):
        self.__statisticsInUpdating = True
        result = yield wg_await(self.__entitlements.forceUpdateCache([_LOOT_BOX_COUNTER_ENTITLEMENT]))
        if self.__statisticsInUpdating and result:
            self.__onEntitlementsCacheUpdated()
        self.__statisticsInUpdating = False

    def __onEventStatusChange(self):
        if self.__eventLootBoxes.isActive():
            self.__buyStatusUpdated()
            self.__updateBoxesCount()
        else:
            self.destroyWindow()

    def __onEntitlementsCacheUpdated(self):
        self.__buyStatusUpdated()
        self.__updateBoxesCount()

    def __onDisconnected(self):
        self.destroyWindow()
