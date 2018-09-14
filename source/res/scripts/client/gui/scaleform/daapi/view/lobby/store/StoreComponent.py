# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/StoreComponent.py
import nations
from CurrentVehicle import g_currentVehicle
from account_helpers.AccountSettings import AccountSettings
from debug_utils import LOG_ERROR
from gui import GUI_NATIONS, GUI_NATIONS_ORDER_INDEX, getNationIndex
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.StoreComponentMeta import StoreComponentMeta
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.game_control import g_instance, getVehicleComparisonBasketCtrl
from gui.shared import events, EVENT_BUS_SCOPE, g_itemsCache, event_dispatcher as shared_events
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.functions import getViewName
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import i18n

class StoreComponent(LobbySubView, StoreComponentMeta):
    _DATA_PROVIDER = 'dataProvider'

    def __init__(self, _=None):
        super(StoreComponent, self).__init__()
        self.__nations = []
        self.__filterHash = {}
        self.__invVehicles = g_itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()
        self._table = None
        self._currentTab = None
        self.__subFilter = {'current': None,
         self._DATA_PROVIDER: []}
        return

    def getName(self):
        """
        Get component name
        :return: <str>
        """
        pass

    def onShowInfo(self, itemCD):
        dataCompactId = int(itemCD)
        item = g_itemsCache.items.getItemByCD(dataCompactId)
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
        getVehicleComparisonBasketCtrl().addVehicle(int(itemCD))

    def requestFilterData(self, filterType):
        """
        Set full filters data to Flash by filterType
        :param filterType: <str> tab ID
        """
        self.__updateFilterOptions(filterType)

    def _populate(self):
        """
        Prepare and set init data into Flash
        Subscribe on account updates
        """
        super(StoreComponent, self)._populate()
        self.__setNations()
        g_clientUpdateManager.addCallbacks({'inventory': self.__onInventoryUpdate})
        comparisonBasket = getVehicleComparisonBasketCtrl()
        comparisonBasket.onChange += self.__onVehCompareBasketChanged
        comparisonBasket.onSwitchChange += self.__onVehCompareBasketSwitchChange
        g_itemsCache.onSyncCompleted += self._update
        g_instance.rentals.onRentChangeNotify += self._onTableUpdate
        g_instance.restore.onRestoreChangeNotify += self._onTableUpdate
        self.__populateFilters()

    def _dispose(self):
        """
        Clear attrs and subscriptions
        """
        super(StoreComponent, self)._dispose()
        self.__clearTableData()
        while len(self.__nations):
            self.__nations.pop()

        self.__nations = None
        self._currentTab = None
        self.__filterHash.clear()
        self.__filterHash = None
        self.__invVehicles = None
        self.__clearSubFilter()
        self._table = None
        g_itemsCache.onSyncCompleted -= self._update
        g_instance.rentals.onRentChangeNotify -= self._onTableUpdate
        g_instance.restore.onRestoreChangeNotify -= self._onTableUpdate
        comparisonBasket = getVehicleComparisonBasketCtrl()
        comparisonBasket.onChange -= self.__onVehCompareBasketChanged
        comparisonBasket.onSwitchChange -= self.__onVehCompareBasketSwitchChange
        g_clientUpdateManager.removeObjectCallbacks(self)
        return

    def _onInventoryUpdate(self, *args):
        self.__invVehicles = g_itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()

    def _update(self, *args):
        self.as_updateS()
        self.as_setVehicleCompareAvailableS(getVehicleComparisonBasketCtrl().isEnabled())

    def _getTabClass(self, type):
        """
        Get component tab class by type
        :param type: <str> tab ID
        :return:<StoreItemsTab>
        """
        raise NotImplementedError

    def _setTableData(self, filter, nation, type):
        """
        Prepare and set data for selected tab, set dataProvider itemWrapper and values
        set account credits and gold into Flash
        :param type: <str> tab ID
        :param nation: <int> gui nation
        :param filter: <obj> filter data
        """
        nation = int(nation) if nation >= 0 else None
        if nation is not None:
            nation = getNationIndex(nation)
        self.__clearTableData()
        cls = self._getTabClass(type)
        self._currentTab = cls(nation, filter)
        self._table.setItemWrapper(self._currentTab.itemWrapper)
        dataProviderValues = self._currentTab.buildItems(self.__invVehicles)
        self._table.setDataProviderValues(dataProviderValues)
        showNoItemsInfo = len(dataProviderValues) == 0
        noItemsInfo = None
        if showNoItemsInfo:
            noItemsInfo = {'message': text_styles.main(MENU.STORE_MENU_NOITEMS)}
        self._table.as_setDataS({'gold': g_itemsCache.items.stats.gold,
         'credits': g_itemsCache.items.stats.credits,
         'type': self._currentTab.getTableType(),
         'showNoItemsInfo': showNoItemsInfo,
         'noItemsInfo': noItemsInfo})
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        """
        Set table component after register
        :param viewPy: <StoreTable>
        :param alias: <str>
        """
        self._table = viewPy

    def _onTableUpdate(self, *args):
        """
        Request table data after update
        :param args:
        """
        nation, itemType = self.__getCurrentFilter()
        filter = AccountSettings.getFilter('%s_%s' % (self.getName(), itemType))
        self.requestTableData(nation, itemType, filter)

    def __setNations(self):
        """
        Set nations into Flash
        """
        while len(self.__nations):
            self.__nations.pop()

        for name in GUI_NATIONS:
            if name in nations.AVAILABLE_NAMES:
                self.__nations.append(name)
                self.__nations.append(nations.INDICES[name])

        self.as_setNationsS(self.__nations)

    def _isVehicleRestoreEnabled(self):
        return g_lobbyContext.getServerSettings().isVehicleRestoreEnabled()

    def __populateFilters(self):
        """
        Set filters and subfilters init data into Flash,
        call flash update and finalize populate
        """
        vehicles = self.__invVehicles
        filterVehicle = None
        if g_currentVehicle.isPresent():
            filterVehicle = g_currentVehicle.item.intCD
        nation, itemType = self.__getCurrentFilter()
        if not self._isVehicleRestoreEnabled() and itemType == STORE_CONSTANTS.RESTORE_VEHICLE:
            itemType = STORE_CONSTANTS.VEHICLE
        tabType = itemType
        if tabType == STORE_CONSTANTS.RESTORE_VEHICLE:
            tabType = STORE_CONSTANTS.VEHICLE
        self.__filterHash = {'language': nation,
         'type': tabType}
        if itemType in (STORE_CONSTANTS.MODULE, STORE_CONSTANTS.SHELL):
            preservedFilters = AccountSettings.getFilter('%s_%s' % (self.getName(), itemType))
            vehicleCD = preservedFilters['vehicleCD']
            if vehicleCD > 0 or filterVehicle is None:
                filterVehicle = vehicleCD
        self.__subFilter = {'current': filterVehicle,
         self._DATA_PROVIDER: [],
         'vehicleObtainingTypes': self._getObtainingVehicleSubFilterData()}
        vehicles.sort(reverse=True)
        for v in vehicles:
            filterElement = {'id': str(v.intCD),
             'nation': GUI_NATIONS_ORDER_INDEX[nations.NAMES[v.nationID]],
             'name': v.userName}
            self.__subFilter[self._DATA_PROVIDER].append(filterElement)

        self.as_setFilterTypeS(self.__filterHash)
        self.as_setSubFilterS(self.__subFilter)
        self.__updateFilterOptions(itemType)
        self.as_completeInitS()
        return

    def _getObtainingVehicleSubFilterData(self):
        return None

    def __onInventoryUpdate(self, *args):
        """
        Update inventory vehicles
        :param args:
        """
        self.__invVehicles = g_itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()

    def __updateFilterOptions(self, filterType):
        """
        Gets vo class name and filter data from AccountSettings by filterType
        set this data into Flash and call _update
        :param filterType: <str> tab ID
        """
        voClassName, showExtra = self._getTabClass(filterType).getFilterInitData()
        self.as_setFilterOptionsS({'voClassName': voClassName,
         'showExtra': showExtra,
         'voData': AccountSettings.getFilter('%s_%s' % (self.getName(), filterType))})
        self._update()

    def __getCurrentFilter(self):
        """
        Get current tab filters from AccountSettings
        :return tuple(nation:<int>, itemType:<str>)
        """
        nation, itemType = AccountSettings.getFilter(self.getName() + '_current')
        return (nation if nation < len(GUI_NATIONS) else -1, itemType)

    def __clearTableData(self):
        """
        Clear table data
        """
        if self._table is not None:
            self._table.clearStoreTableDataProvider()
        if self._currentTab is not None:
            self._currentTab.clear()
        return

    def __clearSubFilter(self):
        """
        Clear filters and subfilters fields
        """
        dataProvider = self.__subFilter[self._DATA_PROVIDER]
        while dataProvider:
            dataProvider.pop().clear()

        self.__subFilter.clear()
        self.__subFilter = None
        return

    def __onVehCompareBasketChanged(self, changedData):
        """
        gui.game_control.VehComparisonBasket.onChange event handler
        :param changedData: instance of gui.game_control.veh_comparison_basket._ChangedData
        """
        if self._currentTab.getTableType() == STORE_CONSTANTS.VEHICLE and changedData.isFullChanged:
            self._update()

    def __onVehCompareBasketSwitchChange(self):
        """
        gui.game_control.VehComparisonBasket.onSwitchChange event handler
        """
        self._update()
