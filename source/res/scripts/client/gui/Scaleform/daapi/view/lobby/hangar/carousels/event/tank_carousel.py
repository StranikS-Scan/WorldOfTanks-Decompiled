# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/event/tank_carousel.py
from CurrentVehicle import g_currentPreviewVehicle
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.tank_carousel import TankCarousel
from gui.Scaleform.daapi.view.lobby.hangar.carousels.event.carousel_data_provider import EventCarouselDataProvider
from gui.Scaleform.daapi.view.lobby.hangar.carousels.event.carousel_filter import EventCarouselFilter

class EventTankCarousel(TankCarousel):

    def __init__(self):
        super(EventTankCarousel, self).__init__()
        self._usedFilters = ()
        self._carouselDPCls = EventCarouselDataProvider
        self._carouselFilterCls = EventCarouselFilter

    def _populate(self):
        super(EventTankCarousel, self)._populate()
        self.as_rowCountS(1)
        g_currentPreviewVehicle.onChanged += self.__onCurrentPreviewVehicleChanged

    def _dispose(self):
        g_currentPreviewVehicle.onChanged -= self.__onCurrentPreviewVehicleChanged
        super(EventTankCarousel, self)._dispose()

    def _getFiltersVisible(self):
        return False

    def _getInitialFilterVO(self, contexts):
        filtersVO = super(EventTankCarousel, self)._getInitialFilterVO(contexts)
        filtersVO['isEvent'] = True
        return filtersVO

    def __onCurrentPreviewVehicleChanged(self):
        if g_currentPreviewVehicle.isPresent() and self._carouselDP is not None:
            filteredIndex = self._carouselDP.findVehicleFilteredIndex(g_currentPreviewVehicle.item)
            if self._carouselDP.pyGetSelectedIdx() != filteredIndex:
                self._carouselDP.selectVehicle(filteredIndex)
                self._carouselDP.refresh()
        return
