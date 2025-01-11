# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/bob/carousel_filter.py
from account_helpers.AccountSettings import BOB_CAROUSEL_FILTER_1, BOB_CAROUSEL_FILTER_2
from account_helpers.AccountSettings import BOB_CAROUSEL_FILTER_CLIENT_1
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import CarouselFilter

class BobCarouselFilter(CarouselFilter):

    def __init__(self):
        super(BobCarouselFilter, self).__init__()
        self._serverSections = (BOB_CAROUSEL_FILTER_1, BOB_CAROUSEL_FILTER_2)
        self._clientSections = (BOB_CAROUSEL_FILTER_CLIENT_1,)
