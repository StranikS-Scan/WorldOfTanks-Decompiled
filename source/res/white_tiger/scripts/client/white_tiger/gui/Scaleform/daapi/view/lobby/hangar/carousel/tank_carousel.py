# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/lobby/hangar/carousel/tank_carousel.py
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.tank_carousel import TankCarousel
from white_tiger.gui.Scaleform.daapi.view.lobby.hangar.carousel.data_provider import WhiteTigerCarouselDataProvider
from white_tiger.gui.Scaleform.daapi.view.lobby.hangar.carousel.filter import WhiteTigerCarouselFilter

class WhiteTigerTankCarousel(TankCarousel):

    def __init__(self):
        super(WhiteTigerTankCarousel, self).__init__()
        self._carouselDPCls = WhiteTigerCarouselDataProvider
        self._carouselFilterCls = WhiteTigerCarouselFilter

    def hasRoles(self):
        return False

    def hasCustomization(self):
        return False

    def _getFiltersVisible(self):
        return False
