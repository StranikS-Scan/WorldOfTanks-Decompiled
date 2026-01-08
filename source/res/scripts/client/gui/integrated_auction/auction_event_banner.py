# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/integrated_auction/auction_event_banner.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import INTEGRATED_AUCTION_FIRST_APPEARANCE_TIMESTAMP, INTEGRATED_AUCTION_INTRO_CLICK_TIMESTAMP
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getIntegratedAuctionUrl
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.constants.event_banner_state import EventBannerState
from gui.impl.lobby.user_missions.hangar_widget.event_banners.base_event_banner import BaseEventBanner
from gui.impl.lobby.user_missions.hangar_widget.event_banners.event_banners_container import EventBannersContainer
from gui.impl.lobby.user_missions.hangar_widget.services import IEventsService
from gui.integrated_auction.constants import AUCTION_ENTRY_POINT_NAME
from gui.integrated_auction.tooltips.event_banner_tooltip import EventBannerTooltip
from gui.shared.event_dispatcher import showShop
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from helpers import dependency
from helpers.time_utils import getServerUTCTime, getTimestampByStrDate

@dependency.replace_none_kwargs(eventService=IEventsService)
def isAuctionEventBannerAvailable(eventService=None):
    auctionEntry = eventService.getEntryData(AUCTION_ENTRY_POINT_NAME)
    return auctionEntry.isValidDateForCreation() if auctionEntry is not None else False


class IntegratedAuctionEventBanner(Notifiable, BaseEventBanner):
    NAME = AUCTION_ENTRY_POINT_NAME
    __eventsService = dependency.descriptor(IEventsService)

    def __init__(self):
        super(IntegratedAuctionEventBanner, self).__init__()
        self.__entry = None
        self.__state = EventBannerState.IN_PROGRESS
        self.__timerValue = 0
        self.__playAppearAnim = False
        self.addNotificator(SimpleNotifier(self.__getTimeToUpdate, self.__onUpdate))
        return

    @property
    def bannerState(self):
        return self.__state

    @property
    def borderColor(self):
        pass

    @property
    def timerValue(self):
        return self.__timerValue if self.__state == EventBannerState.INACTIVE else 0

    @property
    def playAppearAnim(self):
        return self.__playAppearAnim

    @property
    def timerText(self):
        return str(backport.text(R.strings.hangar_event_banners.event.IntegratedAuctionEntryPont.timer.inactive())) if self.__state == EventBannerState.INACTIVE else ''

    def createToolTipContent(self, event):
        return EventBannerTooltip()

    def onClick(self):
        showShop(getIntegratedAuctionUrl())
        if self.__state == EventBannerState.INTRO:
            AccountSettings.setSettings(INTEGRATED_AUCTION_INTRO_CLICK_TIMESTAMP, self.__auctionStart())

    def onAppearAnimationPlayed(self):
        if self.__entry is not None:
            AccountSettings.setSettings(INTEGRATED_AUCTION_FIRST_APPEARANCE_TIMESTAMP, self.__entry.startDate)
        return

    def prepare(self):
        self.__state, _ = self.__getState()
        self.__playAppearAnim = False
        self.startNotification()
        savedAppearTime = AccountSettings.getSettings(INTEGRATED_AUCTION_FIRST_APPEARANCE_TIMESTAMP)
        if self.__entry is not None:
            self.__playAppearAnim = savedAppearTime < self.__entry.startDate
        return

    def onDisappear(self):
        if not self._isVisible:
            return
        super(IntegratedAuctionEventBanner, self).onDisappear()
        self.stopNotification()

    def __auctionStart(self):
        start = self.__entry.data.get('auctionStart')
        return getTimestampByStrDate(start) if start else 0

    def __timeRemaining(self):
        self.__entry = self.__eventsService.getEntryData(self.NAME)
        return self.__entry.endDate - getServerUTCTime()

    def __getState(self):
        self.__entry = self.__eventsService.getEntryData(self.NAME)
        if self.__entry is None or not self.__entry.isValidDateForCreation:
            return (EventBannerState.INACTIVE, -1)
        elif self.__auctionStart():
            self.__timerValue = self.__entry.startDate < getServerUTCTime() < self.__auctionStart() and self.__auctionStart() - getServerUTCTime()
            return (EventBannerState.INACTIVE, self.__timerValue)
        else:
            savedClickTime = AccountSettings.getSettings(INTEGRATED_AUCTION_INTRO_CLICK_TIMESTAMP)
            return (EventBannerState.INTRO, self.__timeRemaining()) if savedClickTime < self.__auctionStart() else (EventBannerState.IN_PROGRESS, self.__timeRemaining())

    def __onUpdate(self, *_):
        if isAuctionEventBannerAvailable():
            EventBannersContainer().onBannerUpdate(self)
        else:
            self.__eventsService.updateEntries()

    def __getTimeToUpdate(self):
        _, timeUntilUpdate = self.__getState()
        return max(timeUntilUpdate, 0)
