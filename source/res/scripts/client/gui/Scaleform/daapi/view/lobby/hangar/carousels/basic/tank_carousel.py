# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/basic/tank_carousel.py
from CurrentVehicle import g_currentVehicle
from gui import SystemMessages
from gui.game_control import g_instance as g_gameCtrl
from gui.shared import events, EVENT_BUS_SCOPE, g_itemsCache
from gui.shared.formatters import text_styles
from gui.shared.gui_items.processors.vehicle import VehicleSlotBuyer
from gui.shared.utils import decorators
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.Scaleform import getButtonsAssetPath
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.carousel_filter import CarouselFilter
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.carousel_data_provider import CarouselDataProvider
from gui.Scaleform.daapi.view.meta.TankCarouselMeta import TankCarouselMeta
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.STORE_TYPES import STORE_TYPES
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from helpers import i18n
_CAROUSEL_FILTERS = ('bonus', 'favorite')

class TankCarousel(TankCarouselMeta):

    def __init__(self):
        super(TankCarousel, self).__init__()
        self._usedFilters = _CAROUSEL_FILTERS
        self._carouselDPConfig = {'carouselFilter': None,
         'itemsCache': None,
         'currentVehicle': None}
        self._carouselDPCls = CarouselDataProvider
        self._carouselFilterCls = CarouselFilter
        self._carouselDP = None
        self._itemsCache = None
        return

    def selectVehicle(self, idx):
        """ This method is called from flash when user clicks on carousel item.
        """
        self._carouselDP.selectVehicle(idx)

    def buyTank(self):
        """ Open store with the shop tab and 'vehicle' component set
        """
        ctx = {'tabId': STORE_TYPES.SHOP,
         'component': STORE_CONSTANTS.VEHICLE}
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_STORE, ctx=ctx), EVENT_BUS_SCOPE.LOBBY)

    def buySlot(self):
        self.__buySlot()

    def updateParams(self):
        """ This method is called from Hangar in order to update
        the stats of last two items (free slots, slot price)
        """
        self._carouselDP.updateSupplies()

    def resetFilters(self):
        self.filter.reset()
        self.as_setCarouselFilterS({'hotFilters': [ self.filter.get(key) for key in self._usedFilters ]})
        self.applyFilter()

    def setFilter(self, idx):
        self.filter.switch(self._usedFilters[idx])
        self.blinkCounter()
        self.applyFilter()

    def getTotalVehiclesCount(self):
        return self._carouselDP.getTotalVehiclesCount()

    def getCurrentVehiclesCount(self):
        return self._carouselDP.getCurrentVehiclesCount()

    def hasRentedVehicles(self):
        return self._carouselDP.hasRentedVehicles()

    def hasEventVehicles(self):
        return self._carouselDP.hasEventVehicles()

    def blinkCounter(self):
        self.as_blinkCounterS()

    def applyFilter(self):
        self._carouselDP.applyFilter()
        if not self.filter.isDefault():
            currentVehiclesCount = self._carouselDP.getCurrentVehiclesCount()
            totalVehiclesCount = self._carouselDP.getTotalVehiclesCount()
            if currentVehiclesCount == 0:
                style = text_styles.error
                drawAttention = True
            else:
                style = text_styles.stats
                drawAttention = False
            self.as_showCounterS('{} / {}'.format(style(currentVehiclesCount), text_styles.main(totalVehiclesCount)), drawAttention)
        else:
            self.as_hideCounterS()

    def updateVehicles(self, vehicles=None, filterCriteria=None):
        if vehicles is None and filterCriteria is None:
            self.as_initCarouselFilterS(self._getInitialFilterVO())
        self._carouselDP.updateVehicles(vehicles, filterCriteria)
        self.applyFilter()
        return

    @property
    def filter(self):
        if self._carouselDP is not None:
            return self._carouselDP.filter
        else:
            return
            return

    def _populate(self):
        super(TankCarousel, self)._populate()
        g_gameCtrl.rentals.onRentChangeNotify += self.__updateRent
        g_gameCtrl.igr.onIgrTypeChanged += self.__updateIgrType
        g_gameCtrl.clanLock.onClanLockUpdate += self.__updateClanLocks
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded
        self._itemsCache = g_itemsCache
        self._carouselDPConfig.update({'carouselFilter': self._carouselFilterCls(),
         'itemsCache': self._itemsCache,
         'currentVehicle': g_currentVehicle})
        self._carouselDP = self._carouselDPCls(**self._carouselDPConfig)
        self._carouselDP.setEnvironment(self.app)
        self._carouselDP.setFlashObject(self.as_getDataProviderS())
        self._carouselDP.buildList()
        self.as_initCarouselFilterS(self._getInitialFilterVO())
        self.applyFilter()

    def _dispose(self):
        g_gameCtrl.rentals.onRentChangeNotify -= self.__updateRent
        g_gameCtrl.igr.onIgrTypeChanged -= self.__updateIgrType
        g_gameCtrl.clanLock.onClanLockUpdate -= self.__updateClanLocks
        self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        self._itemsCache = None
        self._carouselDP.fini()
        self._carouselDP = None
        self._carouselDPConfig.clear()
        super(TankCarousel, self)._dispose()
        return

    def _getInitialFilterVO(self):
        filters = self.filter.getFilters(self._usedFilters)
        xpRateStr = 'x{}'.format(self._itemsCache.items.shop.dailyXPFactor)
        return {'counterCloseTooltip': makeTooltip('#tooltips:tanksFilter/counter/close/header', '#tooltips:tanksFilter/counter/close/body'),
         'mainBtn': {'value': getButtonsAssetPath('params'),
                     'tooltip': makeTooltip('#tank_carousel_filter:carousel/params/header', '#tank_carousel_filter:carousel/params/body')},
         'hotFilters': [{'value': getButtonsAssetPath('bonus_{}'.format(xpRateStr)),
                         'selected': filters['bonus'],
                         'tooltip': makeTooltip('#tank_carousel_filter:carousel/bonus/header', i18n.makeString('#tank_carousel_filter:carousel/bonus/body', bonus=xpRateStr))}, {'value': getButtonsAssetPath('favorite'),
                         'selected': filters['favorite'],
                         'tooltip': makeTooltip('#tank_carousel_filter:carousel/favorite/header', '#tank_carousel_filter:carousel/favorite/body')}]}

    @decorators.process('buySlot')
    def __buySlot(self):
        result = yield VehicleSlotBuyer().request()
        if result.userMsg:
            SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def __updateRent(self, vehicles):
        self.updateVehicles(vehicles)

    def __updateIgrType(self, roomType, xpFactor):
        self.updateVehicles(filterCriteria=REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR)

    def __updateClanLocks(self, vehicles, isFull):
        if isFull:
            self.updateVehicles()
        else:
            self.updateVehicles(vehicles)

    def __onViewLoaded(self, view):
        if view is not None and view.settings is not None:
            if view.settings.alias == VIEW_ALIAS.TANK_CAROUSEL_FILTER_POPOVER:
                view.setTankCarousel(self)
        return
