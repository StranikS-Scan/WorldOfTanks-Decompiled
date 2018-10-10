# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/ranked/carousel_filter.py
from account_helpers.AccountSettings import RANKED_CAROUSEL_FILTER_1, RANKED_CAROUSEL_FILTER_2
from account_helpers.AccountSettings import RANKED_CAROUSEL_FILTER_CLIENT_1
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import CarouselFilter

class RankedCarouselFilter(CarouselFilter):

    def __init__(self):
        super(RankedCarouselFilter, self).__init__()
        self._serverSections = (RANKED_CAROUSEL_FILTER_1, RANKED_CAROUSEL_FILTER_2)
        self._clientSections = (RANKED_CAROUSEL_FILTER_CLIENT_1,)
