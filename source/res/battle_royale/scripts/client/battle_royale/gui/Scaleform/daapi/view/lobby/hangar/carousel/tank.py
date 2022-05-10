# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/hangar/carousel/tank.py
from battle_royale.gui.Scaleform.daapi.view.lobby.hangar.carousel.filter import RoyaleCarouselFilter
from gui.Scaleform import getVehicleTypeAssetPath
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.tank_carousel import TankCarousel
from gui.Scaleform.locale.TANK_CAROUSEL_FILTER import TANK_CAROUSEL_FILTER
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController, IBattleRoyaleRentVehiclesController
from battle_royale.gui.Scaleform.daapi.view.lobby.hangar.carousel.data_provider import RoyaleCarouselDataProvider
_CAROUSEL_FILTERS = ('heavyTank', 'mediumTank', 'lightTank')

class RoyaleTankCarousel(TankCarousel):
    battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __rentVehiclesController = dependency.descriptor(IBattleRoyaleRentVehiclesController)

    def __init__(self):
        super(RoyaleTankCarousel, self).__init__()
        self._carouselDPCls = RoyaleCarouselDataProvider
        self._carouselFilterCls = RoyaleCarouselFilter

    def getCustomParams(self):
        return {'hasBattleRoyleVehicles': self._carouselDP.hasBattleRoyaleVehicles()}

    def _populate(self):
        super(RoyaleTankCarousel, self)._populate()
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded
        self.itemsCache.onSyncCompleted += self.__onCacheResync
        self.__runRentUpdater()

    def _dispose(self):
        self.__rentVehiclesController.unwatchRentVehicles(self.__updateVehicleRentTime)
        self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        super(RoyaleTankCarousel, self)._dispose()

    def _getFiltersVisible(self):
        return False

    def _getInitialFilterVO(self, contexts):
        filtersVO = super(RoyaleTankCarousel, self)._getInitialFilterVO(contexts)
        hotFilters = filtersVO['hotFilters']
        for hotFilter in hotFilters:
            entry = hotFilter['id']
            hotFilter['value'] = getVehicleTypeAssetPath(entry)
            hotFilter['tooltip'] = makeTooltip('#menu:carousel_tank_filter/{}'.format(entry), TANK_CAROUSEL_FILTER.TOOLTIP_VEHICLETYPES_BODY)

        return filtersVO

    def _getFilters(self):
        return _CAROUSEL_FILTERS

    def __onViewLoaded(self, view, *args, **kwargs):
        if view.alias == VIEW_ALIAS.BATTLEROYALE_CAROUSEL_FILTER_POPOVER:
            view.setTankCarousel(self)

    def __runRentUpdater(self):
        self.__rentVehiclesController.watchRentVehicles(self.__updateVehicleRentTime, self._carouselDP.getVehiclesIntCDs())

    def __updateVehicleRentTime(self, _):
        self._carouselDP.updateVehicles()

    def __onCacheResync(self, reason, diff):
        if GUI_ITEM_TYPE.VEHICLE in diff:
            self.__runRentUpdater()

    def hasRoles(self):
        return False
