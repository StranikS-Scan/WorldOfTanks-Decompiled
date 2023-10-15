# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/lobby/hangar/carousel/tank_carousel.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.common.filter_contexts import getFilterSetupContexts, FilterSetupContext
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.tank_carousel import TankCarousel
from halloween.gui.Scaleform.daapi.view.lobby.hangar.carousel.carousel_filter import HW22CarouselFilter
_HW22_CAROUSEL_FILTERS = ('favorite', 'event', 'elite', 'premium')

class HW22TankCarousel(TankCarousel):

    def __init__(self):
        super(HW22TankCarousel, self).__init__()
        self._carouselFilterCls = HW22CarouselFilter
        self._eventFilterSetupContext = {'event': FilterSetupContext(asset='hw23_event_toggle')}

    def updateVehicles(self, vehicles=None, filterCriteria=None):
        super(HW22TankCarousel, self).updateVehicles(vehicles, filterCriteria)
        filterSetupContexts = getFilterSetupContexts(1)
        filterSetupContexts.update(self._eventFilterSetupContext)
        if vehicles is None and filterCriteria is None:
            self.as_initCarouselFilterS(self._getInitialFilterVO(filterSetupContexts))
        return

    def _populate(self):
        super(HW22TankCarousel, self)._populate()
        filterSetupContexts = getFilterSetupContexts(1)
        filterSetupContexts.update(self._eventFilterSetupContext)
        self.as_initCarouselFilterS(self._getInitialFilterVO(filterSetupContexts))
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded

    def _dispose(self):
        self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        super(HW22TankCarousel, self)._dispose()

    def _getInitialFilterVO(self, contexts):
        filtersVO = super(HW22TankCarousel, self)._getInitialFilterVO(contexts)
        filtersVO.update({'popoverAlias': VIEW_ALIAS.HW22_CAROUSEL_FILTER_POPOVER})
        return filtersVO

    def _getFilters(self):
        return _HW22_CAROUSEL_FILTERS

    def __onViewLoaded(self, view, *args, **kwargs):
        if view.alias == VIEW_ALIAS.HW22_CAROUSEL_FILTER_POPOVER:
            view.setTankCarousel(self)
