# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/basic/tank_carousel.py
from PlayerEvents import g_playerEvents
from account_helpers.settings_core import settings_constants
from BonusCaps import BonusCapsConst
from constants import Configs
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform import getButtonsAssetPath
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.common.filter_contexts import getFilterSetupContexts
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.carousel_data_provider import HangarCarouselDataProvider
from gui.Scaleform.daapi.view.meta.TankCarouselMeta import TankCarouselMeta
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.Scaleform.locale.TANK_CAROUSEL_FILTER import TANK_CAROUSEL_FILTER
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showStorage, showTelecomRentalPage
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from helpers import dependency, server_settings
from skeletons.gui.game_control import IRestoreController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

def _removeFilterByNames(filters, filterNames):
    return tuple((f for f in filters if f not in filterNames))


class TankCarousel(TankCarouselMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    restoreCtrl = dependency.descriptor(IRestoreController)

    def __init__(self):
        super(TankCarousel, self).__init__()
        self._carouselDPCls = HangarCarouselDataProvider

    def hasRoles(self):
        return True

    def getCarouselAlias(self):
        return self.getAlias()

    def setFilter(self, idx):
        self.filter.switch(self._usedFilters[idx])
        self.blinkCounter()
        self.applyFilter()

    def setRowCount(self, value):
        self.as_rowCountS(value)

    def buyRentPromotion(self, intCD):
        ActionsFactory.doAction(ActionsFactory.BUY_VEHICLE, intCD)

    def buySlot(self):
        ActionsFactory.doAction(ActionsFactory.BUY_VEHICLE_SLOT)

    def buyTank(self):
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_TECHTREE)), EVENT_BUS_SCOPE.LOBBY)

    def restoreTank(self):
        showStorage(STORAGE_CONSTANTS.IN_HANGAR, STORAGE_CONSTANTS.VEHICLES_TAB_RESTORE)

    def selectTelecomRentalVehicle(self, intCD):
        showTelecomRentalPage()

    def updateAvailability(self):
        super(TankCarousel, self).updateAvailability()
        self.updateParams()

    def updateParams(self):
        if self._carouselDP:
            self._carouselDP.updateSupplies()

    def updateVehicles(self, vehicles=None, filterCriteria=None):
        super(TankCarousel, self).updateVehicles(vehicles, filterCriteria)
        if vehicles is None and filterCriteria is None:
            self.as_initCarouselFilterS(self._getInitialFilterVO(getFilterSetupContexts(self.itemsCache.items.shop.dailyXPFactor)))
        return

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

    def _getFilters(self):
        return _removeFilterByNames(super(TankCarousel, self)._getFilters(), self._carouselDP.getHiddenDynamicFilters() if self._carouselDP else ())

    def _getFiltersVisible(self):
        return True

    def _getFiltersPopoverAlias(self):
        return VIEW_ALIAS.HANGAR_TANK_CAROUSEL_FILTER_POPOVER

    def _getInitialFilterVO(self, contexts):
        filtersVO = {'isVisible': self._getFiltersVisible(),
         'popoverAlias': self._getFiltersPopoverAlias(),
         'mainBtn': {'value': getButtonsAssetPath('params'),
                     'tooltip': TANK_CAROUSEL_FILTER.TOOLTIP_PARAMS},
         'hotFilters': []}
        if self.filter is not None:
            filters = self.filter.getFilters(self._usedFilters)
            for entry in self._usedFilters:
                filtersVO['hotFilters'].append(self._makeFilterVO(entry, contexts, filters))

        return filtersVO

    def _onCarouselSettingsChange(self, diff):
        if settings_constants.GAME.CAROUSEL_TYPE in diff:
            setting = self.settingsCore.options.getSetting(settings_constants.GAME.CAROUSEL_TYPE)
            self.as_rowCountS(setting.getRowCount())
        if settings_constants.GAME.DOUBLE_CAROUSEL_TYPE in diff:
            setting = self.settingsCore.options.getSetting(settings_constants.GAME.DOUBLE_CAROUSEL_TYPE)
            self.as_setSmallDoubleCarouselS(setting.enableSmallCarousel())
        super(TankCarousel, self)._onCarouselSettingsChange(diff)

    def _onServerSettingChanged(self, diff, skipVehicles=False):
        super(TankCarousel, self)._onServerSettingChanged(diff, skipVehicles=self.__onServerSettingChanged(diff))

    def _updateDynamicFilters(self):
        if self._carouselDP is not None:
            self._carouselDP.updateDynamicFilters()
        self._callPopoverCallback()
        self._usedFilters = self._getFilters()
        self.updateVehicles()
        return

    def __onFittingUpdate(self, *args):
        self.updateParams()

    @server_settings.serverSettingsChangeListener(BonusCapsConst.CONFIG_NAME, Configs.CRYSTAL_REWARDS_CONFIG.value)
    def __onServerSettingChanged(self, diff):
        self._updateDynamicFilters()

    def __onViewLoaded(self, view, *args, **kwargs):
        if view.alias == VIEW_ALIAS.HANGAR_TANK_CAROUSEL_FILTER_POPOVER:
            view.setTankCarousel(self)
