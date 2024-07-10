# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/lobby/hangar/qfg_carousel/tank_carousel.py
from fun_random.gui.Scaleform.daapi.view.lobby.hangar.carousel.tank_carousel import FunRandomTankCarousel
from fun_random.gui.Scaleform.daapi.view.lobby.hangar.qfg_carousel.carousel_data_provider import FunRandomQuickFireGunsCarouselDataProvider
from fun_random.gui.Scaleform.daapi.view.lobby.hangar.qfg_carousel.carousel_filter import FunRandomQuickFireGunsCarouselFilter

class FunRandomQuickFireGunsCarousel(FunRandomTankCarousel):

    def __init__(self):
        super(FunRandomQuickFireGunsCarousel, self).__init__()
        self._carouselDPCls = FunRandomQuickFireGunsCarouselDataProvider
        self._carouselFilterCls = FunRandomQuickFireGunsCarouselFilter

    def updateParams(self):
        pass

    def _getFiltersVisible(self):
        return False

    def _getFilters(self):
        pass

    def _updateDynamicFilters(self):
        pass

    def _updateFilter(self):
        pass
