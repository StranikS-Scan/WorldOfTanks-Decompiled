# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/weekend_brawl/carousel_filter.py
from account_helpers.AccountSettings import WEEKENDBRAWL_CAROUSEL_FILTER_1, WEEKENDBRAWL_CAROUSEL_FILTER_2
from account_helpers.AccountSettings import WEEKENDBRAWL_CAROUSEL_FILTER_CLIENT_1
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import CarouselFilter

class WeekendBrawlCarouselFilter(CarouselFilter):

    def __init__(self):
        super(WeekendBrawlCarouselFilter, self).__init__()
        self._serverSections = (WEEKENDBRAWL_CAROUSEL_FILTER_1, WEEKENDBRAWL_CAROUSEL_FILTER_2)
        self._clientSections = (WEEKENDBRAWL_CAROUSEL_FILTER_CLIENT_1,)
