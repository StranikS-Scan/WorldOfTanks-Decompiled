# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/StoreComponent.py
from async import await, async
import nations
from CurrentVehicle import g_currentVehicle
from account_helpers.AccountSettings import AccountSettings
from debug_utils import LOG_ERROR
from gui import GUI_NATIONS, GUI_NATIONS_ORDER_INDEX, getNationIndex
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform import getVehicleTypeAssetPath, getLevelsAssetPath
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.StoreComponentMeta import StoreComponentMeta
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.prb_control.settings import VEHICLE_LEVELS
from gui.shared import events, EVENT_BUS_SCOPE, event_dispatcher as shared_events
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.utils.functions import getViewName, makeTooltip
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.impl.dialogs import dialogs
from helpers import i18n, dependency
from skeletons.gui.game_control import IVehicleComparisonBasket, IRentalsController, IRestoreController, ITradeInController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class StoreComponent(LobbySubView, StoreComponentMeta):
    _DATA_PROVIDER = 'dataProvider'
    itemsCache = dependency.descriptor(IItemsCache)
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)
    rentals = dependency.descriptor(IRentalsController)
    restore = dependency.descriptor(IRestoreController)
    tradeIn = dependency.descriptor(ITradeInController)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, _=None):
        super(StoreComponent, self).__init__()
        self.__nations = []
        self.__filterHash = {}
        self.__invVehicles = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE).values()
        self._table = None
        self._currentTab = None
        self.__subFilter = {'current': None,
         self._DATA_PROVIDER: []}
        return

    def getName(self):
        pass

    def onShowInfo(self, itemCD):
        dataCompactId = int(itemCD)
        item = self.itemsCache.items.getItemByCD(dataCompactId)
        if item is None:
            return LOG_ERROR('There is error while attempting to show vehicle info window: ', str(dataCompactId))
        else:
            if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
                if item.isPreviewAllowed():
                    shared_events.showVehiclePreview(item.intCD, VIEW_ALIAS.LOBBY_STORE)
                else:
                    shared_events.showVehicleInfo(item.intCD)
            else:
                self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.MODULE_INFO_WINDOW, getViewName(VIEW_ALIAS.MODULE_INFO_WINDOW, item.intCD), {'moduleCompactDescr': item.intCD,
                 'isAdditionalInfoShow': i18n.makeString(MENU.MODULEINFO_ADDITIONALINFO)}), EVENT_BUS_SCOPE.LOBBY)
            return

    def onAddVehToCompare(self, itemCD):
        self.comparisonBasket.addVehicle(int(itemCD))

    def onUpgradeModule(self, moduleId):
        self.__upgradeItem(moduleId)

    def requestFilterData(self, filterType):
        self.__updateFilterOptions(filterType)

    def updateFilters(self):
        self.__populateFilters()

    def _populate(self):
        super(StoreComponent, self)._populate()
        self.__initFiltersData()
        g_clientUpdateManager.addCallbacks({'inventory': self.__onInventoryUpdate})
        self.comparisonBasket.onChange += self.__onVehCompareBasketChanged
        self.comparisonBasket.onSwitchChange += self.__onVehCompareBasketSwitchChange
        self.itemsCache.onSyncCompleted += self._update
        self.rentals.onRentChangeNotify += self._onTableUpdate
        self.restore.onRestoreChangeNotify += self._onTableUpdate
        self.__populateFilters()
        self.as_completeInitS()

    def _dispose(self):
        super(StoreComponent, self)._dispose()
        self.__clearTableData()
        while self.__nations:
            self.__nations.pop()

        self.__nations = None
        self._currentTab = None
        self.__filterHash.clear()
        self.__filterHash = None
        self.__invVehicles = None
        self.__clearSubFilter()
        self._table = None
        self.itemsCache.onSyncCompleted -= self._update
        self.rentals.onRentChangeNotify -= self._onTableUpdate
        self.restore.onRestoreChangeNotify -= self._onTableUpdate
        self.comparisonBasket.onChange -= self.__onVehCompareBasketChanged
        self.comparisonBasket.onSwitchChange -= self.__onVehCompareBasketSwitchChange
        g_clientUpdateManager.removeObjectCallbacks(self)
        return

    def _update(self, *args):
        self.as_updateS()
        self.as_setVehicleCompareAvailableS(self.comparisonBasket.isEnabled())

    def _getTabClass(self, tabType):
        raise NotImplementedError

    def _setTableData(self, f, nation, tabType, actionsSelected, itemCD):
        nation = int(nation) if nation >= 0 else None
        if nation is not None:
            nation = getNationIndex(nation)
        self.__clearTableData()
        cls = self._getTabClass(tabType)
        self._currentTab = cls(nation, f, actionsSelected, itemCD)
        self._table.setItemWrapper(self._currentTab.itemWrapper)
        dataProviderValues = self._currentTab.buildItems(self.__invVehicles)
        self._table.setDataProviderValues(dataProviderValues)
        showNoItemsInfo = len(dataProviderValues) == 0
        noItemsInfo = None
        if showNoItemsInfo:
            noItemsInfo = {'message': text_styles.main(MENU.STORE_MENU_NOITEMS)}
        self._table.as_setDataS({'type': self._currentTab.getTableType(),
         'showNoItemsInfo': showNoItemsInfo,
         'noItemsInfo': noItemsInfo})
        self.as_setActionAvailableS(self._currentTab.hasDiscounts())
        if self._currentTab.getScrollIdx():
            self.as_scrollPositionS(self._currentTab.getScrollIdx())
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        self._table = viewPy

    def _onTableUpdate(self, *args):
        nation, itemType, actionsSelected = self.__getCurrentFilter()
        f = AccountSettings.getFilter('%s_%s' % (self.getName(), itemType))
        self.requestTableData(nation, actionsSelected, itemType, f)

    def __initFiltersData(self):
        while self.__nations:
            self.__nations.pop()

        for name in GUI_NATIONS:
            if name in nations.AVAILABLE_NAMES:
                self.__nations.append(name)
                self.__nations.append(nations.INDICES[name])

        self.as_initFiltersDataS(self.__nations, MENU.SHOP_ACTIONS_FILTER_LABEL)

    def _isVehicleRestoreEnabled(self):
        return self.lobbyContext.getServerSettings().isVehicleRestoreEnabled()

    def _isTradeInEnabled(self):
        return self.tradeIn.isEnabled()

    def __populateFilters(self):
        vehicles = [ veh for veh in self.__invVehicles if veh.activeInNationGroup ]
        filterVehicle = None
        if g_currentVehicle.isPresent():
            filterVehicle = g_currentVehicle.item.intCD
        nation, itemType, actionsSelected = self.__getCurrentFilter()
        if not self._isVehicleRestoreEnabled() and itemType == STORE_CONSTANTS.RESTORE_VEHICLE:
            itemType = STORE_CONSTANTS.VEHICLE
        if not self._isTradeInEnabled() and itemType == STORE_CONSTANTS.TRADE_IN_VEHICLE:
            itemType = STORE_CONSTANTS.VEHICLE
        tabType = itemType
        if tabType == STORE_CONSTANTS.RESTORE_VEHICLE:
            tabType = STORE_CONSTANTS.VEHICLE
        elif tabType == STORE_CONSTANTS.TRADE_IN_VEHICLE:
            tabType = STORE_CONSTANTS.VEHICLE
        self.__filterHash = {'language': nation,
         'tabType': tabType,
         'fittingType': itemType,
         'actionsSelected': actionsSelected}
        if itemType in (STORE_CONSTANTS.MODULE, STORE_CONSTANTS.SHELL):
            preservedFilters = AccountSettings.getFilter('%s_%s' % (self.getName(), itemType))
            vehicleCD = preservedFilters['vehicleCD']
            if vehicleCD > 0 or filterVehicle is None:
                filterVehicle = vehicleCD
        self.__subFilter = {'current': filterVehicle,
         self._DATA_PROVIDER: []}
        vehicles.sort(reverse=True)
        for v in vehicles:
            filterElement = {'id': str(v.intCD),
             'nation': GUI_NATIONS_ORDER_INDEX[nations.NAMES[v.nationID]],
             'name': v.userName}
            self.__subFilter[self._DATA_PROVIDER].append(filterElement)

        self.as_setFilterTypeS(self.__filterHash)
        self.as_setSubFilterS(self.__subFilter)
        self.__updateFilterOptions(itemType)
        return

    def __onInventoryUpdate(self, *args):
        self.__invVehicles = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()
        self.__populateFilters()

    @async
    def __upgradeItem(self, moduleId):
        module = self.itemsCache.items.getItemByCD(int(moduleId))
        result, _ = yield await(dialogs.trophyDeviceUpgradeConfirm(module))
        if result:
            ItemsActionsFactory.doAction(ItemsActionsFactory.UPGRADE_MODULE, module, None, None)
        return

    def __updateFilterOptions(self, filterType):
        voClassName, showExtra = self._getTabClass(filterType).getFilterInitData()
        filters = AccountSettings.getFilter('%s_%s' % (self.getName(), filterType))
        data = {'voClassName': voClassName,
         'showExtra': showExtra,
         'voData': filters}
        if filterType in (STORE_CONSTANTS.VEHICLE, STORE_CONSTANTS.RESTORE_VEHICLE, STORE_CONSTANTS.TRADE_IN_VEHICLE):
            vehicleTypes = []
            levels = []
            selectedTypes = filters['selectedTypes']
            selectedLevels = filters['selectedLevels']
            data['voData'].update({'vehicleTypes': vehicleTypes,
             'levels': levels})
            for idx, vehicleType in enumerate(VEHICLE_TYPES_ORDER):
                vehicleTypes.append({'value': getVehicleTypeAssetPath(vehicleType),
                 'tooltip': makeTooltip('#menu:carousel_tank_filter/{}'.format(vehicleType), '#tank_carousel_filter:tooltip/vehicleTypes/body'),
                 'selected': selectedTypes[idx]})

            for level in VEHICLE_LEVELS:
                levels.append({'value': getLevelsAssetPath('level_{}'.format(level)),
                 'selected': selectedLevels[level - 1]})

        self.as_setFilterOptionsS(data)
        self._update()

    def __getCurrentFilter(self):
        nation, itemType, actionsSelected = AccountSettings.getFilter(self.getName() + '_current')
        return (nation if nation < len(GUI_NATIONS) else -1, itemType, actionsSelected)

    def __clearTableData(self):
        if self._table is not None:
            self._table.clearStoreTableDataProvider()
        if self._currentTab is not None:
            self._currentTab.clear()
        return

    def __clearSubFilter(self):
        dataProvider = self.__subFilter[self._DATA_PROVIDER]
        while dataProvider:
            dataProvider.pop().clear()

        self.__subFilter.clear()
        self.__subFilter = None
        return

    def __onVehCompareBasketChanged(self, changedData):
        if self._currentTab.getTableType() == STORE_CONSTANTS.VEHICLE and changedData.isFullChanged:
            self._update()

    def __onVehCompareBasketSwitchChange(self):
        self._update()
