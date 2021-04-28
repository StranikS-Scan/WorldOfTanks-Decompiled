# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/weekend_brawl/tank_carousel.py
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.tank_carousel import TankCarousel
from gui.Scaleform.daapi.view.lobby.hangar.carousels.weekend_brawl.carousel_data_provider import WeekendBrawlCarouselDataProvider
from gui.Scaleform.daapi.view.lobby.hangar.carousels.weekend_brawl.carousel_filter import WeekendBrawlCarouselFilter

class WeekendBrawlTankCarousel(TankCarousel):

    def __init__(self):
        super(WeekendBrawlTankCarousel, self).__init__()
        self._carouselDPCls = WeekendBrawlCarouselDataProvider
        self._carouselFilterCls = WeekendBrawlCarouselFilter
