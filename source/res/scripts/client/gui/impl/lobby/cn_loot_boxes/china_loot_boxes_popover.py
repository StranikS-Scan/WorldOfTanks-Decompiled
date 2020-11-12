# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/cn_loot_boxes/china_loot_boxes_popover.py
from async import async, await
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.cn_loot_boxes.china_loot_boxes_popover_model import ChinaLootBoxesPopoverModel
from gui.impl.gen.view_models.views.lobby.cn_loot_boxes.china_loot_boxes_popover_renderer_model import ChinaLootBoxesPopoverRendererModel
from gui.impl.lobby.cn_loot_boxes.tooltips.china_loot_box_infotype import ChinaLootBoxTooltip
from gui.impl.pub import PopOverViewImpl
from gui.shared.event_dispatcher import showCNLootBoxOpenWindow, showCNLootBoxStorageWindow, showCNLootBoxOpenErrorWindow
from gui.shared.gui_items.loot_box import GUI_ORDER
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency
from helpers.time_utils import getServerUTCTime, ONE_MINUTE, ONE_SECOND
from skeletons.gui.game_control import ICNLootBoxesController, IEntitlementsController
from gui.shared.utils import decorators
_LOOT_BOX_COUNTER_ENTITLEMENT = 'loot_box_counter'

class ChinaLootBoxesPopover(PopOverViewImpl):
    __slots__ = ('__popoverNotificator', '__hasBuyableBoxes', '__statisticsInUpdating')
    __cnLootBoxesCtrl = dependency.descriptor(ICNLootBoxesController)
    __entitlementsController = dependency.descriptor(IEntitlementsController)

    def __init__(self):
        super(ChinaLootBoxesPopover, self).__init__(ViewSettings(R.views.lobby.cn_loot_boxes.china_loot_boxes_popover.ChinaLootBoxesPopover(), ViewFlags.VIEW, ChinaLootBoxesPopoverModel()))
        self.__popoverNotificator = SimpleNotifier(self.__getTimeToBuyStatusUpdate, self.__buyStatusUpdated)
        self.__hasBuyableBoxes = False
        self.__statisticsInUpdating = False

    @property
    def viewModel(self):
        return super(ChinaLootBoxesPopover, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.cn_loot_boxes.tooltips.ChinaLootBoxInfoType():
            boxType = event.getArgument('type')
            return ChinaLootBoxTooltip(boxType=boxType)
        return super(ChinaLootBoxesPopover, self).createToolTipContent(event, contentID)

    def _initialize(self, *args, **kwargs):
        super(ChinaLootBoxesPopover, self)._initialize()
        self.viewModel.onOpenBtnClick += self.__onOpenBtnClick
        self.viewModel.onBuyBtnClick += self.__onBuyBtnClick
        self.viewModel.onAboutBtnClick += self.__onAboutBtnClick
        self.__cnLootBoxesCtrl.onAvailabilityChange += self.__onAvailabilityChange
        self.__cnLootBoxesCtrl.onBoxesCountChange += self.__onBoxesCountChange
        self.__cnLootBoxesCtrl.onStatusChange += self.__onEventStatusChange

    def _onLoading(self, *args, **kwargs):
        super(ChinaLootBoxesPopover, self)._onLoading(*args, **kwargs)
        self.__initializeLootBoxes()

    def _finalize(self):
        self.__statisticsInUpdating = False
        self.__popoverNotificator.stopNotification()
        self.__cnLootBoxesCtrl.onBoxesCountChange -= self.__onBoxesCountChange
        self.__cnLootBoxesCtrl.onAvailabilityChange -= self.__onAvailabilityChange
        self.__cnLootBoxesCtrl.onStatusChange -= self.__onEventStatusChange
        self.viewModel.onOpenBtnClick -= self.__onOpenBtnClick
        self.viewModel.onBuyBtnClick -= self.__onBuyBtnClick
        self.viewModel.onAboutBtnClick -= self.__onAboutBtnClick
        super(ChinaLootBoxesPopover, self)._finalize()

    def __initializeLootBoxes(self):
        self.__buyStatusUpdated()
        if self.__cnLootBoxesCtrl.getDayLimit() <= self.__cnLootBoxesCtrl.getDayInfoStatistics() and self.__cnLootBoxesCtrl.isLootBoxesAvailable():
            self.__popoverNotificator.startNotification()
        self.viewModel.setMaxBoxesAvailableToBuy(self.__cnLootBoxesCtrl.getDayLimit())
        self.viewModel.getEntryList().reserve(len(GUI_ORDER))
        self.__updateBoxesCount()
        if not self.__entitlementsController.isCacheInited():
            self.__updateStatistics()

    def __addLootBox(self, lootBoxType, lootBoxCount, entryList):
        lootBoxSlot = ChinaLootBoxesPopoverRendererModel()
        availableToBuyBoxes = self.__cnLootBoxesCtrl.getDayLimit() - self.__cnLootBoxesCtrl.getDayInfoStatistics()
        self.__hasBuyableBoxes = availableToBuyBoxes > 0
        with lootBoxSlot.transaction() as tx:
            tx.setLootBoxType(lootBoxType)
            tx.setCount(lootBoxCount)
            tx.setIsOpenBtnEnabled(lootBoxCount > 0 and self.__cnLootBoxesCtrl.isLootBoxesAvailable())
            tx.setIsBuyBtnEnabled(self.__cnLootBoxesCtrl.isBuyAvailable())
        entryList.addViewModel(lootBoxSlot)

    @decorators.process('updating')
    def __onOpenBtnClick(self, args):
        lootBox = self.__cnLootBoxesCtrl.getStoreInfo().get(args.get('type', None), None)
        if self.__cnLootBoxesCtrl.isLootBoxesAvailable() and lootBox is not None and lootBox.getInventoryCount() > 0:
            result = yield LootBoxOpenProcessor(lootBox, 1).request()
            self.destroyWindow()
            if result and result.success and result.auxData is not None:
                showCNLootBoxOpenWindow(lootBox.getType(), rewards=result.auxData)
            else:
                showCNLootBoxOpenErrorWindow()
        elif not self.__cnLootBoxesCtrl.isLootBoxesAvailable():
            SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.lootboxes.open.server_error.DISABLED()), priority=NotificationPriorityLevel.MEDIUM, type=SystemMessages.SM_TYPE.Error)
        return

    def __onBuyBtnClick(self, _):
        self.destroyWindow()
        self.__cnLootBoxesCtrl.openShopPage()

    def __onAboutBtnClick(self):
        self.destroyWindow()
        showCNLootBoxStorageWindow()

    def __updateBoxesCount(self):
        entryList = self.viewModel.getEntryList()
        entryList.clear()
        entryList.invalidate()
        for lootBoxType in GUI_ORDER:
            lb = self.__cnLootBoxesCtrl.getStoreInfo().get(lootBoxType, None)
            self.__addLootBox(lootBoxType, lb.getInventoryCount() if lb is not None else 0, entryList)

        entryList.invalidate()
        return

    def __onAvailabilityChange(self, *_):
        self.viewModel.setIsDisabled(not self.__cnLootBoxesCtrl.isLootBoxesAvailable())
        if self.__cnLootBoxesCtrl.isLootBoxesAvailable():
            self.__popoverNotificator.startNotification()
        else:
            self.__popoverNotificator.stopNotification()

    def __onBoxesCountChange(self, _):
        self.__updateBoxesCount()

    def __getTimeToBuyStatusUpdate(self):
        dayTimeLeft = self.__cnLootBoxesCtrl.getTimeLeftToResetPurchase() + ONE_SECOND
        return dayTimeLeft % ONE_MINUTE or ONE_MINUTE

    def __buyStatusUpdated(self):
        with self.viewModel.transaction() as model:
            model.setIsDisabled(not self.__cnLootBoxesCtrl.isLootBoxesAvailable())
            availableToBuyBoxes = self.__cnLootBoxesCtrl.getDayLimit() - self.__cnLootBoxesCtrl.getDayInfoStatistics()
            model.setBoxesAvailableToBuy(availableToBuyBoxes)
            model.setIsEntitlementCacheInited(self.__entitlementsController.isCacheInited())
            currentUTCTime = getServerUTCTime()
            dayTimeLeft = self.__cnLootBoxesCtrl.getTimeLeftToResetPurchase()
            model.setBuyingEnableMinutes(0 if dayTimeLeft <= ONE_MINUTE else -1 * dayTimeLeft // ONE_MINUTE * -1)
            _, finish = self.__cnLootBoxesCtrl.getEventActiveTime()
            isLastEventDay = finish - currentUTCTime <= dayTimeLeft
            model.setIsLastEventDay(isLastEventDay)
            hasBuyableBoxes = availableToBuyBoxes > 0
            if isLastEventDay or hasBuyableBoxes:
                self.__popoverNotificator.stopNotification()
            if hasBuyableBoxes != self.__hasBuyableBoxes:
                self.__updateBoxesCount()

    @async
    def __updateStatistics(self):
        self.__statisticsInUpdating = True
        result = yield await(self.__entitlementsController.forceUpdateCache([_LOOT_BOX_COUNTER_ENTITLEMENT]))
        if self.__statisticsInUpdating and result:
            self.__buyStatusUpdated()
            self.__updateBoxesCount()
        self.__statisticsInUpdating = False

    def __onEventStatusChange(self):
        if not self.__cnLootBoxesCtrl.isActive():
            self.destroyWindow()
