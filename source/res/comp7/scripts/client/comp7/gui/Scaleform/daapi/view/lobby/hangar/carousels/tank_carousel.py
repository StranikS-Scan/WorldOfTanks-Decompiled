# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/hangar/carousels/tank_carousel.py
from comp7.gui.Scaleform.daapi.view.lobby.hangar.carousels.carousel_data_provider import Comp7CarouselDataProvider
from comp7.gui.Scaleform.daapi.view.lobby.hangar.carousels.carousel_filter import Comp7CarouselFilter
from gui.Scaleform.daapi.view.lobby.hangar.carousels import BattlePassTankCarousel

class Comp7TankCarousel(BattlePassTankCarousel):

    def __init__(self):
        super(Comp7TankCarousel, self).__init__()
        self._carouselDPCls = Comp7CarouselDataProvider
        self._carouselFilterCls = Comp7CarouselFilter

    def _getInitialFilterVO(self, contexts):
        filtersVO = super(Comp7TankCarousel, self)._getInitialFilterVO(contexts)
        filtersVO['isComp7'] = True
        return filtersVO

    def _getFilters(self):
        return super(Comp7TankCarousel, self)._getFilters() + ('comp7',)
