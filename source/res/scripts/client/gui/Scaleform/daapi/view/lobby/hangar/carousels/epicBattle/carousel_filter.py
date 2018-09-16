# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/epicBattle/carousel_filter.py
from account_helpers.AccountSettings import EPICBATTLE_CAROUSEL_FILTER_1, EPICBATTLE_CAROUSEL_FILTER_2
from account_helpers.AccountSettings import EPICBATTLE_CAROUSEL_FILTER_CLIENT_1
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import CarouselFilter

class EpicBattleCarouselFilter(CarouselFilter):

    def __init__(self):
        super(EpicBattleCarouselFilter, self).__init__()
        self._serverSections = (EPICBATTLE_CAROUSEL_FILTER_1, EPICBATTLE_CAROUSEL_FILTER_2)
        self._clientSections = (EPICBATTLE_CAROUSEL_FILTER_CLIENT_1,)
