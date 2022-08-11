# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/cn_loot_boxes/china_loot_boxes_popover.py
from async import async, await
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.cn_loot_boxes.china_loot_boxes_popover_model import ChinaLootBoxesPopoverModel
from gui.impl.lobby.cn_loot_boxes.tooltips.china_loot_box_infotype import ChinaLootBoxTooltip
from gui.impl.pub import PopOverViewImpl
from gui.shared.event_dispatcher import showCNLootBoxOpenErrorWindow, showCNLootBoxOpenWindow, showCNLootBoxesWelcomeScreen
from gui.shared.gui_items.loot_box import ChinaLootBoxes
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils import decorators
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency
from helpers.time_utils import ONE_MINUTE, ONE_SECOND, getServerUTCTime
from skeletons.gui.game_control import ICNLootBoxesController, IEntitlementsController
_LOOT_BOX_COUNTER_ENTITLEMENT = 'loot_box_counter'

class ChinaLootBoxesPopover(PopOverViewImpl):
    __slots__ = ('__popoverNotifier', '__hasBuyableBoxes', '__statisticsInUpdating')
    __cnLootBoxes = dependency.descriptor(ICNLootBoxesController)
    __entitlements = dependency.descriptor(IEntitlementsController)

    def __init__(self):
        super(ChinaLootBoxesPopover, self).__init__(ViewSettings(R.views.lobby.cn_loot_boxes.ChinaLootBoxPopoverView(), ViewFlags.VIEW, ChinaLootBoxesPopoverModel()))
        self.__popoverNotifier = SimpleNotifier(self.__getTimeToBuyStatusUpdate, self.__buyStatusUpdated)
        self.__hasBuyableBoxes = False
        self.__statisticsInUpdating = False

    @property
    def viewModel(self):
        return super(ChinaLootBoxesPopover, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return ChinaLootBoxTooltip(boxType=ChinaLootBoxes.PREMIUM) if contentID == R.views.lobby.cn_loot_boxes.tooltips.ChinaLootBoxInfoType() else super(ChinaLootBoxesPopover, self).createToolTipContent(event, contentID)

    def _initialize(self, *args, **kwargs):
        super(ChinaLootBoxesPopover, self)._initialize()
        self.viewModel.onOpenBtnClick += self.__onOpenBtnClick
        self.viewModel.onBuyBtnClick += self.__onBuyBtnClick
        self.viewModel.onAboutBtnClick += self.__onAboutBtnClick
        self.__cnLootBoxes.onAvailabilityChange += self.__onAvailabilityChange
        self.__cnLootBoxes.onBoxesCountChange += self.__onBoxesCountChange
        self.__cnLootBoxes.onStatusChange += self.__onEventStatusChange
        self.__entitlements.onCacheUpdated += self.__onEntitlementsCacheUpdated

    def _onLoading(self, *args, **kwargs):
        super(ChinaLootBoxesPopover, self)._onLoading(*args, **kwargs)
        self.__initializeLootBoxes()

    def _finalize(self):
        self.__statisticsInUpdating = False
        self.__popoverNotifier.stopNotification()
        self.__entitlements.onCacheUpdated -= self.__onEntitlementsCacheUpdated
        self.__cnLootBoxes.onBoxesCountChange -= self.__onBoxesCountChange
        self.__cnLootBoxes.onAvailabilityChange -= self.__onAvailabilityChange
        self.__cnLootBoxes.onStatusChange -= self.__onEventStatusChange
        self.viewModel.onOpenBtnClick -= self.__onOpenBtnClick
        self.viewModel.onBuyBtnClick -= self.__onBuyBtnClick
        self.viewModel.onAboutBtnClick -= self.__onAboutBtnClick
        super(ChinaLootBoxesPopover, self)._finalize()

    def __initializeLootBoxes(self):
        self.__buyStatusUpdated()
        if self.__cnLootBoxes.getDayLimit() <= self.__cnLootBoxes.getDayInfoStatistics() and self.__cnLootBoxes.isLootBoxesAvailable():
            self.__popoverNotifier.startNotification()
        self.viewModel.setMaxBoxesAvailableToBuy(self.__cnLootBoxes.getDayLimit())
        self.__updateBoxesCount()
        if not self.__entitlements.isCacheInited():
            self.__updateStatistics()

    @decorators.process('updating')
    def __onOpenBtnClick(self):
        lootBox = self.__cnLootBoxes.getStoreInfo().get(ChinaLootBoxes.PREMIUM, None)
        if self.__cnLootBoxes.isLootBoxesAvailable() and lootBox is not None and lootBox.getInventoryCount() > 0:
            result = yield LootBoxOpenProcessor(lootBox, 1).request()
            self.destroyWindow()
            if result and result.success and result.auxData is not None:
                showCNLootBoxOpenWindow(lootBox.getType(), rewards=result.auxData)
            else:
                showCNLootBoxOpenErrorWindow()
        elif not self.__cnLootBoxes.isLootBoxesAvailable():
            SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.lootboxes.open.server_error.DISABLED()), priority=NotificationPriorityLevel.MEDIUM, type=SystemMessages.SM_TYPE.Error)
        return

    def __onBuyBtnClick(self):
        self.destroyWindow()
        self.__cnLootBoxes.openExternalShopPage()

    def __onAboutBtnClick(self):
        self.destroyWindow()
        showCNLootBoxesWelcomeScreen()

    def __updateBoxesCount(self):
        availableToBuyBoxes = self.__cnLootBoxes.getDayLimit() - self.__cnLootBoxes.getDayInfoStatistics()
        self.__hasBuyableBoxes = availableToBuyBoxes > 0
        lb = self.__cnLootBoxes.getStoreInfo().get(ChinaLootBoxes.PREMIUM, None)
        lootBoxCount = lb.getInventoryCount() if lb is not None else 0
        with self.viewModel.transaction() as tx:
            tx.setCount(lootBoxCount)
            tx.setIsOpenAvailable(lootBoxCount > 0 and self.__cnLootBoxes.isLootBoxesAvailable())
            tx.setIsBuyAvailable(self.__cnLootBoxes.isBuyAvailable())
            tx.setBoxesAvailableToBuy(availableToBuyBoxes)
            tx.setEventExpireTime(self.__getEventExpireTime())
            tx.setMainRewardBoxesLeft(self.__cnLootBoxes.boxCountToGuaranteedBonus)
            tx.setGuaranteedLimit(self.__cnLootBoxes.getGuaranteedBonusLimit(ChinaLootBoxes.PREMIUM))
        return

    def __onAvailabilityChange(self, *_):
        if self.__cnLootBoxes.isLootBoxesAvailable():
            self.__popoverNotifier.startNotification()
        else:
            self.__popoverNotifier.stopNotification()
        self.__initializeLootBoxes()

    def __onBoxesCountChange(self, *_):
        self.__updateBoxesCount()

    def __getTimeToBuyStatusUpdate(self):
        dayTimeLeft = self.__cnLootBoxes.getTimeLeftToResetPurchase() + ONE_SECOND
        return dayTimeLeft % ONE_MINUTE or ONE_MINUTE

    def __buyStatusUpdated(self):
        isLootBoxesAvailable = self.__cnLootBoxes.isLootBoxesAvailable()
        availableToBuyBoxes = self.__cnLootBoxes.getDayLimit() - self.__cnLootBoxes.getDayInfoStatistics()
        dayTimeLeft = self.__cnLootBoxes.getTimeLeftToResetPurchase()
        _, finish = self.__cnLootBoxes.getEventActiveTime()
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
            tx.setIsBuyAvailable(self.__cnLootBoxes.isBuyAvailable())
            tx.setBoxesAvailableToBuy(availableToBuyBoxes)
            hasBuyableBoxes = availableToBuyBoxes > 0
            if isLastEventDay or hasBuyableBoxes:
                self.__popoverNotifier.stopNotification()
            if hasBuyableBoxes != self.__hasBuyableBoxes:
                self.__updateBoxesCount()

    def __getEventExpireTime(self):
        _, finish = self.__cnLootBoxes.getEventActiveTime()
        return finish - getServerUTCTime()

    @async
    def __updateStatistics(self):
        self.__statisticsInUpdating = True
        result = yield await(self.__entitlements.forceUpdateCache([_LOOT_BOX_COUNTER_ENTITLEMENT]))
        if self.__statisticsInUpdating and result:
            self.__onEntitlementsCacheUpdated()
        self.__statisticsInUpdating = False

    def __onEventStatusChange(self):
        if not self.__cnLootBoxes.isActive():
            self.destroyWindow()

    def __onEntitlementsCacheUpdated(self):
        self.__buyStatusUpdated()
        self.__updateBoxesCount()
