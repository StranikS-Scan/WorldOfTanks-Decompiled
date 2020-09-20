# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/bob/tank_carousel.py
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.tank_carousel import TankCarousel
from gui.Scaleform.daapi.view.lobby.hangar.carousels.bob.carousel_data_provider import BobCarouselDataProvider
from gui.Scaleform.daapi.view.lobby.hangar.carousels.bob.carousel_filter import BobCarouselFilter

class BobTankCarousel(TankCarousel):

    def __init__(self):
        super(BobTankCarousel, self).__init__()
        self._carouselDPCls = BobCarouselDataProvider
        self._carouselFilterCls = BobCarouselFilter
