# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/basic/tank_carousel.py
from PlayerEvents import g_playerEvents
from account_helpers.settings_core import settings_constants
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform import getButtonsAssetPath
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.common.filter_contexts import getFilterSetupContexts
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.carousel_data_provider import HangarCarouselDataProvider
from gui.Scaleform.daapi.view.meta.TankCarouselMeta import TankCarouselMeta
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.Scaleform.locale.TANK_CAROUSEL_FILTER import TANK_CAROUSEL_FILTER
from gui.shared.event_dispatcher import showStorage, showTelecomRentalPage, showVehicleTechTreeView
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from helpers import dependency
from skeletons.gui.game_control import IRestoreController, IEarlyAccessController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class TankCarousel(TankCarouselMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    restoreCtrl = dependency.descriptor(IRestoreController)
    __earlyAccessCtrl = dependency.descriptor(IEarlyAccessController)

    def __init__(self):
        super(TankCarousel, self).__init__()
        self._carouselDPCls = HangarCarouselDataProvider

    def setRowCount(self, value):
        self.as_rowCountS(value)

    def buyTank(self):
        showVehicleTechTreeView()

    def restoreTank(self):
        showStorage(STORAGE_CONSTANTS.IN_HANGAR, STORAGE_CONSTANTS.VEHICLES_TAB_RESTORE)

    def buySlot(self):
        self.__buySlot()

    def buyRentPromotion(self, intCD):
        ActionsFactory.doAction(ActionsFactory.BUY_VEHICLE, intCD)

    def selectTelecomRentalVehicle(self, intCD):
        showTelecomRentalPage()

    def getCarouselAlias(self):
        return self.getAlias()

    def updateParams(self):
        if self._carouselDP:
            self._carouselDP.updateSupplies()

    def updateVehicles(self, vehicles=None, filterCriteria=None):
        super(TankCarousel, self).updateVehicles(vehicles, filterCriteria)
        if vehicles is None and filterCriteria is None:
            self.as_initCarouselFilterS(self._getInitialFilterVO(getFilterSetupContexts(self.itemsCache.items.shop.dailyXPFactor)))
        return

    def updateAviability(self):
        super(TankCarousel, self).updateAviability()
        self.updateParams()

    def setFilter(self, idx):
        self.filter.switch(self._usedFilters[idx])
        self.blinkCounter()
        self.applyFilter()

    def getCustomParams(self):
        popupFilters = super(TankCarousel, self).getCustomParams()
        if self.__earlyAccessCtrl.isEnabled() and self.__earlyAccessCtrl.isPostProgressionQueueSelected() and not self.__earlyAccessCtrl.isFilterDisabledInQueue():
            popupFilters.update({'early_access': True})
        return popupFilters

    def hasRoles(self):
        return True

    def _populate(self):
        super(TankCarousel, self)._populate()
        g_playerEvents.onBattleResultsReceived += self.__onFittingUpdate
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onFittingUpdate
        self.restoreCtrl.onRestoreChangeNotify += self.__onFittingUpdate
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded
        g_clientUpdateManager.addCallbacks({'stats.credits': self.__onFittingUpdate,
         'stats.gold': self.__onFittingUpdate,
         'stats.vehicleSellsLeft': self.__onFittingUpdate,
         'stats.slots': self.__onFittingUpdate,
         'goodies': self.__onFittingUpdate})
        setting = self.settingsCore.options.getSetting(settings_constants.GAME.CAROUSEL_TYPE)
        self.as_rowCountS(setting.getRowCount())
        setting = self.settingsCore.options.getSetting(settings_constants.GAME.DOUBLE_CAROUSEL_TYPE)
        self.as_setSmallDoubleCarouselS(setting.enableSmallCarousel())
        self.as_initCarouselFilterS(self._getInitialFilterVO(getFilterSetupContexts(self.itemsCache.items.shop.dailyXPFactor)))

    def _dispose(self):
        g_playerEvents.onBattleResultsReceived -= self.__onFittingUpdate
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onFittingUpdate
        self.restoreCtrl.onRestoreChangeNotify -= self.__onFittingUpdate
        self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(TankCarousel, self)._dispose()

    def _onCarouselSettingsChange(self, diff):
        if settings_constants.GAME.CAROUSEL_TYPE in diff:
            setting = self.settingsCore.options.getSetting(settings_constants.GAME.CAROUSEL_TYPE)
            self.as_rowCountS(setting.getRowCount())
        if settings_constants.GAME.DOUBLE_CAROUSEL_TYPE in diff:
            setting = self.settingsCore.options.getSetting(settings_constants.GAME.DOUBLE_CAROUSEL_TYPE)
            self.as_setSmallDoubleCarouselS(setting.enableSmallCarousel())
        super(TankCarousel, self)._onCarouselSettingsChange(diff)

    def _getFiltersVisible(self):
        return True

    def _getInitialFilterVO(self, contexts):
        filtersVO = {'mainBtn': {'value': getButtonsAssetPath('params'),
                     'tooltip': TANK_CAROUSEL_FILTER.TOOLTIP_PARAMS},
         'hotFilters': [],
         'isVisible': self._getFiltersVisible(),
         'isFrontline': False}
        if self.filter is not None:
            filters = self.filter.getFilters(self._usedFilters)
            for entry in self._usedFilters:
                filtersVO['hotFilters'].append(self._makeFilterVO(entry, contexts, filters))

        return filtersVO

    def __buySlot(self):
        ActionsFactory.doAction(ActionsFactory.BUY_VEHICLE_SLOT)

    def __onFittingUpdate(self, *args):
        self.updateParams()

    def __onViewLoaded(self, view, *args, **kwargs):
        if view.alias == VIEW_ALIAS.TANK_CAROUSEL_FILTER_POPOVER:
            view.setTankCarousel(self)
