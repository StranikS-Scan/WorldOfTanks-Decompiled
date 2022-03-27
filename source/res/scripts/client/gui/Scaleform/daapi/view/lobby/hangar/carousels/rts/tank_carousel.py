# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/rts/tank_carousel.py
from gui.rts_battles.rts_constants import RTS_CAROUSEL_FILTER_KEY
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.tank_carousel import TankCarousel
from gui.Scaleform.daapi.view.lobby.hangar.carousels.rts.carousel_data_provider import RTSCarouselDataProvider
from gui.Scaleform.daapi.view.lobby.hangar.carousels.rts.carousel_filter import RTSCarouselFilter

class RTSTankCarousel(TankCarousel):

    def __init__(self):
        super(RTSTankCarousel, self).__init__()
        self._carouselDPCls = RTSCarouselDataProvider
        self._carouselFilterCls = RTSCarouselFilter

    def _populate(self):
        super(RTSTankCarousel, self)._populate()
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded

    def _dispose(self):
        self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        super(RTSTankCarousel, self)._dispose()

    def _getInitialFilterVO(self, contexts):
        filtersVO = super(RTSTankCarousel, self)._getInitialFilterVO(contexts)
        filtersVO.update({'popoverAlias': VIEW_ALIAS.RTS_CAROUSEL_FILTER_POPOVER})
        return filtersVO

    def _getFilters(self):
        parentFilters = super(RTSTankCarousel, self)._getFilters()
        return parentFilters[1:] + (RTS_CAROUSEL_FILTER_KEY,)

    def __onViewLoaded(self, view, *args, **kwargs):
        if view.alias == VIEW_ALIAS.RTS_CAROUSEL_FILTER_POPOVER:
            view.setTankCarousel(self)
