# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/royale/tank_carousel.py
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.tank_carousel import TankCarousel
from gui.Scaleform.daapi.view.lobby.hangar.carousels.royale.carousel_data_provider import RoyaleCarouselDataProvider
from gui.Scaleform.daapi.view.lobby.hangar.carousels.royale.carousel_filter import RoyaleCarouselFilter

class RoyaleTankCarousel(TankCarousel):

    def __init__(self):
        super(RoyaleTankCarousel, self).__init__()
        self._carouselDPCls = RoyaleCarouselDataProvider
        self._carouselFilterCls = RoyaleCarouselFilter

    def _getFilters(self):
        isBattleRoyaleEnabled = self.battleRoyaleController.isEnabled()
        parentFilters = super(RoyaleTankCarousel, self)._getFilters()
        return parentFilters + ('battleRoyale',) if isBattleRoyaleEnabled else parentFilters
