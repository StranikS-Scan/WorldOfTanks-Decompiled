# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/basic/tank_carousel.py
import BigWorld
from PlayerEvents import g_playerEvents
from account_helpers.settings_core import settings_constants
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform import getButtonsAssetPath
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.common.filter_contexts import getFilterSetupContexts, FilterSetupContext
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.carousel_data_provider import HangarCarouselDataProvider
from gui.Scaleform.daapi.view.meta.TankCarouselMeta import TankCarouselMeta
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.Scaleform.locale.TANK_CAROUSEL_FILTER import TANK_CAROUSEL_FILTER
from gui.shop import showBuyGoldForSlot
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showStorage, showVehicleRentalPage, showTelecomRentalPage, showNewYearVehiclesView
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from helpers.i18n import makeString as _ms
from items.components.ny_constants import VEH_BRANCH_EXTRA_SLOT_TOKEN
from new_year.ny_constants import SyncDataKeys, NY_FILTER
from new_year.vehicle_branch import EMPTY_VEH_INV_ID
from ny_common.settings import NYVehBranchConsts, NY_CONFIG_NAME
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IRestoreController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController

class TankCarousel(TankCarouselMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    restoreCtrl = dependency.descriptor(IRestoreController)
    nyController = dependency.descriptor(INewYearController)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(TankCarousel, self).__init__()
        self._carouselDPCls = HangarCarouselDataProvider
        self._lastVehicleBranch = set()
        self._vehBranchEnabled = False

    def setRowCount(self, value):
        self.as_rowCountS(value)

    def buyTank(self):
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_TECHTREE)), EVENT_BUS_SCOPE.LOBBY)

    def restoreTank(self):
        showStorage(STORAGE_CONSTANTS.IN_HANGAR, STORAGE_CONSTANTS.VEHICLES_TAB_RESTORE)

    def buySlot(self):
        self.__buySlot()

    def newYearVehicles(self):
        showNewYearVehiclesView()

    def buyRentPromotion(self, intCD):
        ActionsFactory.doAction(ActionsFactory.BUY_VEHICLE, intCD)

    def selectWotPlusVehicle(self, intCD):
        telecomRentals = BigWorld.player().telecomRentals
        hasTelecomRentalsActive = telecomRentals.isActive()
        hasAvailableRent = telecomRentals.getAvailableRentCount() > 0
        isRentalEnabled = self.lobbyContext.getServerSettings().isTelecomRentalsEnabled()
        if isRentalEnabled and hasTelecomRentalsActive and hasAvailableRent:
            showTelecomRentalPage()
        else:
            showVehicleRentalPage()

    def updateHotFilters(self):
        self.as_setCarouselFilterS({'hotFilters': [ self.filter.get(key) for key in self._usedFilters ]})

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

    def resetFilters(self):
        super(TankCarousel, self).resetFilters()
        self.updateHotFilters()

    def setFilter(self, idx):
        self.filter.switch(self._usedFilters[idx])
        self.blinkCounter()
        self.applyFilter()

    def hasRoles(self):
        return True

    def _populate(self):
        super(TankCarousel, self)._populate()
        g_playerEvents.onBattleResultsReceived += self.__onFittingUpdate
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsUpdate
        self.__settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.restoreCtrl.onRestoreChangeNotify += self.__onFittingUpdate
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded
        self.nyController.onDataUpdated += self.__onVehicleBranchUpdated
        self.nyController.onStateChanged += self.__onVehicleBranchStateChanged
        self._vehBranchEnabled = self.nyController.isVehicleBranchEnabled()
        g_clientUpdateManager.addCallbacks({'stats.credits': self.__onFittingUpdate,
         'stats.gold': self.__onFittingUpdate,
         'stats.vehicleSellsLeft': self.__onFittingUpdate,
         'stats.slots': self.__onFittingUpdate,
         'goodies': self.__onFittingUpdate,
         'tokens': self.__onTokensUpdate})
        setting = self.settingsCore.options.getSetting(settings_constants.GAME.CAROUSEL_TYPE)
        self.as_rowCountS(setting.getRowCount())
        setting = self.settingsCore.options.getSetting(settings_constants.GAME.DOUBLE_CAROUSEL_TYPE)
        self.as_setSmallDoubleCarouselS(setting.enableSmallCarousel())
        self.as_initCarouselFilterS(self._getInitialFilterVO(getFilterSetupContexts(self.itemsCache.items.shop.dailyXPFactor)))
        self._lastVehicleBranch = set(self.itemsCache.items.festivity.getVehicleBranch())

    def _dispose(self):
        g_playerEvents.onBattleResultsReceived -= self.__onFittingUpdate
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsUpdate
        self.__settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.restoreCtrl.onRestoreChangeNotify -= self.__onFittingUpdate
        self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        self.nyController.onDataUpdated -= self.__onVehicleBranchUpdated
        self.nyController.onStateChanged -= self.__onVehicleBranchStateChanged
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
                if entry == NY_FILTER and not self._vehBranchEnabled:
                    continue
                filterCtx = contexts.get(entry, FilterSetupContext())
                filtersVO['hotFilters'].append({'id': entry,
                 'value': getButtonsAssetPath(filterCtx.asset or entry),
                 'selected': filters[entry],
                 'enabled': True,
                 'tooltip': makeTooltip('#tank_carousel_filter:tooltip/{}/header'.format(entry), _ms('#tank_carousel_filter:tooltip/{}/body'.format(entry), **filterCtx.ctx))})

        return filtersVO

    def __buySlot(self):
        price = self.itemsCache.items.shop.getVehicleSlotsPrice(self.itemsCache.items.stats.vehicleSlots)
        availableMoney = self.itemsCache.items.stats.money
        if price and availableMoney.gold < price:
            showBuyGoldForSlot(price)
        else:
            ActionsFactory.doAction(ActionsFactory.BUY_VEHICLE_SLOT)

    def __onFittingUpdate(self, *args):
        self.updateParams()

    def __onSettingsChanged(self, diff):
        if settings_constants.NewYearStorageKeys.NY_VEHICLES_LEVEL_UP_ENTRY in diff:
            self._carouselDP.updateVehicleBranch()

    def __onServerSettingsUpdate(self, diff):
        if NY_CONFIG_NAME in diff and NYVehBranchConsts.CONFIG_NAME in diff[NY_CONFIG_NAME]:
            self.__updateNewYearVehicles(self._lastVehicleBranch - {EMPTY_VEH_INV_ID})
        self.updateParams()

    def __onViewLoaded(self, view, *args, **kwargs):
        if view.alias == VIEW_ALIAS.TANK_CAROUSEL_FILTER_POPOVER:
            view.setTankCarousel(self)

    def __updateNewYearVehicles(self, vehInvIDs):
        vehicles = self.itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.SPECIFIC_BY_INV_ID(vehInvIDs))
        if self._carouselDP and vehicles:
            self._carouselDP.updateVehicles(vehicles.keys())

    def __onVehicleBranchStateChanged(self):
        branchEnabled = self.nyController.isVehicleBranchEnabled()
        if branchEnabled == self._vehBranchEnabled:
            return
        self._vehBranchEnabled = branchEnabled
        self.filter.newYearReset()
        if self._carouselDP:
            self._carouselDP.updateVehicleBranch()
            self.__updateNewYearVehicles(self._lastVehicleBranch - {EMPTY_VEH_INV_ID})
        self.as_initCarouselFilterS(self._getInitialFilterVO(getFilterSetupContexts(self.itemsCache.items.shop.dailyXPFactor)))
        self.applyFilter()

    def __onTokensUpdate(self, diff):
        if VEH_BRANCH_EXTRA_SLOT_TOKEN in diff:
            self._carouselDP.updateVehicleBranch()

    def __onVehicleBranchUpdated(self, keys):
        if (SyncDataKeys.VEHICLE_BRANCH in keys or SyncDataKeys.VEHICLE_BONUS_CHOICES in keys) and self._carouselDP:
            self._carouselDP.filter.update({}, save=False)
            self._carouselDP.updateVehicleBranch()
            currentBranch = set(self.itemsCache.items.festivity.getVehicleBranch())
            diffInvIDs = (currentBranch ^ self._lastVehicleBranch) - {EMPTY_VEH_INV_ID}
            if SyncDataKeys.VEHICLE_BONUS_CHOICES in keys:
                diffInvIDs.update(self.nyController.getVehicleBranch().getVehiclesWithBonusChoice())
            self._lastVehicleBranch = currentBranch
            self.__updateNewYearVehicles(diffInvIDs)
        elif SyncDataKeys.LEVEL in keys:
            self._carouselDP.updateVehicleBranch()
