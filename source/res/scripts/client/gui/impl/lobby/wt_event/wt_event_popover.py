# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_popover.py
from PlayerEvents import g_playerEvents
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_popover_model import WtEventPopoverModel, BoxTypeEnum
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags
import logging
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_portal_model import PortalType
from gui.impl.lobby.wt_event.tooltips.wt_event_popover_tooltip_view import WtEventPopoverTooltipView
from gui.impl.lobby.wt_event.tooltips.wt_guaranteed_reward_tooltip_view import WtGuaranteedRewardTooltipView
from gui.impl.pub import PopOverViewImpl
from gui.periodic_battles.models import PrimeTimeStatus
from gui.shared.event_dispatcher import showEventPortalWindow
from gui.shared.gui_items.loot_box import EVENT_LOOT_BOXES_CATEGORY, EventLootBoxes, WTPortalStatus
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency
from helpers.time_utils import ONE_MINUTE, ONE_SECOND, getServerUTCTime
from skeletons.gui.game_control import IEntitlementsController, IWTLootBoxesController, IEventBattlesController
from wg_async import wg_async, wg_await
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
_LOOT_BOX_COUNTER_ENTITLEMENT = 'loot_box_counter'
_logger = logging.getLogger(__name__)
_PortalTypesForBoxes = {BoxTypeEnum.WTHUNTER.value: PortalType.HUNTER,
 BoxTypeEnum.WTBOSS.value: PortalType.BOSS}

class WTEventLootBoxesPopover(PopOverViewImpl):
    __slots__ = ('__popoverNotifier', '__hasBuyableBoxes', '__statisticsInUpdating')
    __lootBoxesCtrl = dependency.descriptor(IWTLootBoxesController)
    __entitlements = dependency.descriptor(IEntitlementsController)
    __eventBattlesController = dependency.descriptor(IEventBattlesController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.wt_event.WTEventPopoverView(), flags=ViewFlags.VIEW, model=WtEventPopoverModel(), args=args, kwargs=kwargs)
        self.__popoverNotifier = SimpleNotifier(self.__getTimeToBuyStatusUpdate, self.__buyStatusUpdated)
        self.__hasBuyableBoxes = False
        self.__statisticsInUpdating = False
        super(WTEventLootBoxesPopover, self).__init__(settings)

    def getPortalStatus(self, boxType):
        boxType = EventLootBoxes.WT_HUNTER if boxType == BoxTypeEnum.WTHUNTER else EventLootBoxes.WT_BOSS
        isLootboxAvailable = self.__lootBoxesCtrl.isLootBoxesAvailable()
        if not isLootboxAvailable:
            return WTPortalStatus.ERROR
        eventPlayableEndTime = self.__eventBattlesController.getEndTime()
        eventNotPlayable = eventPlayableEndTime < getServerUTCTime()
        if eventNotPlayable:
            return WTPortalStatus.EVENT_ENDED
        if boxType == BoxTypeEnum.WTHUNTER.value:
            status, _, _ = self.__eventBattlesController.getPrimeTimeStatus()
            isPrimeTime = status == PrimeTimeStatus.AVAILABLE
            if not isPrimeTime:
                return WTPortalStatus.NO_PRIME_TIME
            hasUnopenedLootBoxes = self.__lootBoxesCtrl.getLootBoxesCountByTypeForUI(boxType)
            if hasUnopenedLootBoxes:
                return WTPortalStatus.UNOPENED_LOOTBOXES
            return WTPortalStatus.NO_UNOPENED_LOOTBOXES
        if boxType == BoxTypeEnum.WTBOSS.value:
            isBuyAvailable = self.__lootBoxesCtrl.isBuyAvailable()
            hasUnopenedLootBoxes = self.__lootBoxesCtrl.getLootBoxesCountByTypeForUI(boxType)
            if not isBuyAvailable and not hasUnopenedLootBoxes:
                return WTPortalStatus.ALL_CLOSED
            if not isBuyAvailable and hasUnopenedLootBoxes:
                return WTPortalStatus.ONLY_PORTAL_OPEN
            if isBuyAvailable and hasUnopenedLootBoxes:
                return WTPortalStatus.ALL_OPEN
            if isBuyAvailable and not hasUnopenedLootBoxes:
                return WTPortalStatus.ONLY_SHOP_OPEN

    @property
    def viewModel(self):
        return super(WTEventLootBoxesPopover, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.wt_event.tooltips.WtEventPopoverTooltipView():
            return WtEventPopoverTooltipView(self.__getLootboxType().value)
        return WtGuaranteedRewardTooltipView() if contentID == R.views.lobby.wt_event.tooltips.WtGuaranteedRewardTooltipView() else super(WTEventLootBoxesPopover, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        return ((g_playerEvents.onDisconnected, self.__onDisconnected),
         (self.viewModel.onOpenBtnClick, self.__onOpenBtnClick),
         (self.viewModel.onBuyBtnClick, self.__onBuyBtnClick),
         (self.viewModel.onEventBtnClick, self.__onEventBtnClick),
         (self.__lootBoxesCtrl.onAvailabilityChange, self.__onAvailabilityChange),
         (self.__lootBoxesCtrl.onBoxesCountChange, self.__onBoxesCountChange),
         (self.__lootBoxesCtrl.onStatusChange, self.__onEventStatusChange),
         (self.__entitlements.onCacheUpdated, self.__onEntitlementsCacheUpdated))

    def _onLoading(self, *args, **kwargs):
        super(WTEventLootBoxesPopover, self)._onLoading(*args, **kwargs)
        isHunterLootBox = kwargs.get('isHunterLootBox')
        if isHunterLootBox is None:
            _logger.error('Incorrect type of the lootBox to show the tooltip')
            return
        else:
            self.__eventBattlesController.getLootBoxAreaSoundMgr().popover()
            with self.viewModel.transaction() as model:
                if isHunterLootBox:
                    model.setBoxType(BoxTypeEnum.WTHUNTER)
                else:
                    model.setBoxType(BoxTypeEnum.WTBOSS)
            self.__initializeLootBoxes()
            return

    def _finalize(self):
        self.__statisticsInUpdating = False
        self.__popoverNotifier.stopNotification()
        super(WTEventLootBoxesPopover, self)._finalize()

    def __initializeLootBoxes(self):
        self.__buyStatusUpdated()
        if self.__lootBoxesCtrl.getDayLimit() <= self.__lootBoxesCtrl.getDayInfoStatistics() and self.__lootBoxesCtrl.isLootBoxesAvailable():
            self.__popoverNotifier.startNotification()
        self.viewModel.setMaxBoxesAvailableToBuy(self.__lootBoxesCtrl.getDayLimit())
        self.__updateBoxesCount()
        if not self.__entitlements.isCacheInited():
            self.__updateStatistics()
        self.viewModel.setWtPortalStatus(self.getPortalStatus(self.__getLootboxType()))

    def __onOpenBtnClick(self):
        lootBox = self.__lootBoxesCtrl.getStoreInfo(EVENT_LOOT_BOXES_CATEGORY).get(self.__getLootboxType().value, None)
        if self.__lootBoxesCtrl.isLootBoxesAvailable() and lootBox is not None and lootBox.getInventoryCount() > 0:
            self.__goToLootboxPortal(self.__getLootboxType())
            self.destroyWindow()
        elif not self.__lootBoxesCtrl.isLootBoxesAvailable():
            SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.lootboxes.open.server_error.DISABLED()), priority=NotificationPriorityLevel.MEDIUM, type=SystemMessages.SM_TYPE.Error)
        return

    def __onBuyBtnClick(self):
        self.destroyWindow()
        self.__lootBoxesCtrl.openShop()

    def __onEventBtnClick(self):
        self.destroyWindow()
        self.__eventBattlesController.doSelectEventPrb()
        selectorUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.EVENT)

    def __updateBoxesCount(self):
        availableToBuyBoxes = self.__lootBoxesCtrl.getDayLimit() - self.__lootBoxesCtrl.getDayInfoStatistics()
        self.__hasBuyableBoxes = availableToBuyBoxes > 0
        lootBoxType = self.__getLootboxType()
        lootBoxCount = self.__lootBoxesCtrl.getLootBoxesCountByTypeForUI(lootBoxType.value)
        _, timeToStart, _ = self.__eventBattlesController.getPrimeTimeStatus()
        guaranteed, left, isIgnored = self.__lootBoxesCtrl.getLootBoxLimitsInfo(lootBoxType.value)
        with self.viewModel.transaction() as tx:
            tx.setCount(lootBoxCount)
            tx.setIsOpenAvailable(lootBoxCount > 0 and self.__lootBoxesCtrl.isLootBoxesAvailable())
            tx.setIsBuyAvailable(self.__lootBoxesCtrl.isBuyAvailable())
            tx.setBoxesAvailableToBuy(availableToBuyBoxes)
            tx.setEventExpireTime(self.__getEventExpireTime())
            tx.setMainRewardBoxesLeft(left)
            tx.setGuaranteedLimit(guaranteed)
            tx.setWtPortalStatus(self.getPortalStatus(lootBoxType))
            tx.setCeaseFireEndTime(timeToStart)
            if lootBoxType.value == BoxTypeEnum.WTBOSS.value:
                tx.setIsGuaranteedAwardIgnored(isIgnored)

    def __onAvailabilityChange(self, *_):
        if self.__lootBoxesCtrl.isLootBoxesAvailable():
            self.__popoverNotifier.startNotification()
        else:
            self.__popoverNotifier.stopNotification()
        self.__initializeLootBoxes()

    def __onBoxesCountChange(self, *_):
        self.__updateBoxesCount()

    def __getTimeToBuyStatusUpdate(self):
        dayTimeLeft = self.__lootBoxesCtrl.getTimeLeftToResetPurchase() + ONE_SECOND
        return dayTimeLeft % ONE_MINUTE or ONE_MINUTE

    def __buyStatusUpdated(self):
        isLootBoxesAvailable = self.__lootBoxesCtrl.isLootBoxesAvailable()
        availableToBuyBoxes = self.__lootBoxesCtrl.getDayLimit() - self.__lootBoxesCtrl.getDayInfoStatistics()
        dayTimeLeft = self.__lootBoxesCtrl.getTimeLeftToResetPurchase()
        finish = self.__eventBattlesController.getEndTime()
        isLastEventDay = finish - getServerUTCTime() <= dayTimeLeft
        hasErrors = not (self.__entitlements.isCacheInited() and isLootBoxesAvailable)
        if availableToBuyBoxes and not hasErrors:
            buyingEnableTime = 0
        elif not hasErrors:
            buyingEnableTime = dayTimeLeft
        else:
            buyingEnableTime = dayTimeLeft if dayTimeLeft > ONE_MINUTE else 0
        with self.viewModel.transaction() as tx:
            tx.setIsLastEventDay(isLastEventDay)
            tx.setHasErrors(hasErrors)
            tx.setBuyingEnableTime(buyingEnableTime)
            tx.setIsBuyAvailable(self.__lootBoxesCtrl.isBuyAvailable())
            tx.setBoxesAvailableToBuy(availableToBuyBoxes)
            tx.setUseExternalShop(self.__lootBoxesCtrl.useExternalShop())
            hasBuyableBoxes = availableToBuyBoxes > 0
            if isLastEventDay or hasBuyableBoxes:
                self.__popoverNotifier.stopNotification()
            if hasBuyableBoxes != self.__hasBuyableBoxes:
                self.__updateBoxesCount()

    def __getEventExpireTime(self):
        endDate = self.__eventBattlesController.getSeasonEndTime()
        return endDate - getServerUTCTime()

    @wg_async
    def __updateStatistics(self):
        self.__statisticsInUpdating = True
        result = yield wg_await(self.__entitlements.forceUpdateCache([_LOOT_BOX_COUNTER_ENTITLEMENT]))
        if self.__statisticsInUpdating and result:
            self.__onEntitlementsCacheUpdated()
        self.__statisticsInUpdating = False

    def __onEventStatusChange(self):
        if self.__lootBoxesCtrl.isActive():
            self.__buyStatusUpdated()
            self.__updateBoxesCount()
        else:
            self.destroyWindow()

    def __onEntitlementsCacheUpdated(self):
        self.__buyStatusUpdated()
        self.__updateBoxesCount()

    def __onDisconnected(self):
        self.destroyWindow()

    def __goToLootboxPortal(self, lootboxType):
        if lootboxType is None:
            return
        else:
            portalType = PortalType(_PortalTypesForBoxes[lootboxType.value])
            if self.__canOpenPortal(portalType):
                showEventPortalWindow(portalType=portalType)
            return

    def __canOpenPortal(self, portalType):
        return portalType in PortalType

    def __getLootboxType(self):
        return self.viewModel.getBoxType()
