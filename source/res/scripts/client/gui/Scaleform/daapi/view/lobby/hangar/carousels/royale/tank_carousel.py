# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/royale/tank_carousel.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.tank_carousel import TankCarousel
from gui.Scaleform.daapi.view.lobby.hangar.carousels.royale.carousel_data_provider import RoyaleCarouselDataProvider
from gui.Scaleform.daapi.view.lobby.hangar.carousels.royale.carousel_filter import RoyaleCarouselFilter
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController

class RoyaleTankCarousel(TankCarousel):
    battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self):
        super(RoyaleTankCarousel, self).__init__()
        self._carouselDPCls = RoyaleCarouselDataProvider
        self._carouselFilterCls = RoyaleCarouselFilter

    def getCustomParams(self):
        return {'hasBattleRoyleVehicles': self._carouselDP.hasBattleRoyaleVehicles()}

    def _populate(self):
        super(RoyaleTankCarousel, self)._populate()
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded

    def _dispose(self):
        self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        super(RoyaleTankCarousel, self)._dispose()

    def _getInitialFilterVO(self, contexts):
        filtersVO = super(RoyaleTankCarousel, self)._getInitialFilterVO(contexts)
        filtersVO.update({'popoverAlias': VIEW_ALIAS.BATTLEROYALE_CAROUSEL_FILTER_POPOVER})
        return filtersVO

    def _getFilters(self):
        isBattleRoyaleEnabled = self.battleRoyaleController.isEnabled()
        parentFilters = super(RoyaleTankCarousel, self)._getFilters()
        return parentFilters + ('battleRoyale',) if isBattleRoyaleEnabled else parentFilters

    def __onViewLoaded(self, view, *args, **kwargs):
        if view.alias == VIEW_ALIAS.BATTLEROYALE_CAROUSEL_FILTER_POPOVER:
            view.setTankCarousel(self)

    def hasRoles(self):
        return False
