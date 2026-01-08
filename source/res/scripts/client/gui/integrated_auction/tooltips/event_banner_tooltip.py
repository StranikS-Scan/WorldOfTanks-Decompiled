# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/integrated_auction/tooltips/event_banner_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.views.lobby.integrated_auction.tooltips.auction_event_banner_tooltip_model import AuctionEventBannerTooltipModel
from gui.impl.lobby.user_missions.hangar_widget.services import IEventsService
from gui.integrated_auction.constants import AUCTION_ENTRY_POINT_NAME
from helpers import dependency
from helpers.time_utils import getServerUTCTime, getTimestampByStrDate

class EventBannerTooltip(ViewImpl):
    __eventService = dependency.descriptor(IEventsService)

    def __init__(self):
        settings = ViewSettings(R.views.mono.integrated_auction.tooltips.auction_event_banner_tooltip())
        settings.model = AuctionEventBannerTooltipModel()
        super(EventBannerTooltip, self).__init__(settings)
        self.__entry = None
        return

    @property
    def viewModel(self):
        return super(EventBannerTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EventBannerTooltip, self)._onLoading(*args, **kwargs)
        self.__entry = self.__eventService.getEntryData(AUCTION_ENTRY_POINT_NAME)
        if self.__entry is not None:
            with self.getViewModel().transaction() as model:
                model.setIsAvailable(self.__getIsAvailable())
                model.setTimerValue(self.__getTimerValue())
        return

    def __getTimerValue(self):
        return self.__entry.endDate - getServerUTCTime() if self.__getIsAvailable() else self.__getAuctionStart() - getServerUTCTime()

    def __getAuctionStart(self):
        auctionStart = self.__entry.data.get('auctionStart')
        return getTimestampByStrDate(auctionStart) if auctionStart else 0

    def __getIsAvailable(self):
        return self.__getAuctionStart() <= getServerUTCTime() < self.__entry.endDate
