# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/StoreComponent.py
from CurrentVehicle import g_currentVehicle
from account_helpers.AccountSettings import AccountSettings
from debug_utils import LOG_ERROR
from gui import GUI_NATIONS, GUI_NATIONS_ORDER_INDEX, getNationIndex
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.locale.MENU import MENU
from gui.game_control import g_instance
from gui.shared import events, EVENT_BUS_SCOPE, g_itemsCache, event_dispatcher as shared_events
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.functions import getViewName
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.Scaleform.daapi.view.meta.StoreComponentMeta import StoreComponentMeta
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from helpers import i18n
import nations

class StoreComponent(LobbySubView, StoreComponentMeta):
    _DATA_PROVIDER = 'dataProvider'

    def __init__(self, _=None):
        super(StoreComponent, self).__init__()
        self.__nations = []
        self.__filterHash = {}
        self.__invVehicles = g_itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()
        self._table = None
        self._currentTab = None
        self._tableType = None
        self.__subFilter = {'current': None,
         self._DATA_PROVIDER: []}
        return

    def getName(self):
        pass

    def onCloseButtonClick(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def onShowInfo(self, data):
        dataCompactId = int(data.id)
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
                self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.MODULE_INFO_WINDOW, getViewName(VIEW_ALIAS.MODULE_INFO_WINDOW, item.intCD), {'moduleCompactDescr': str(item.intCD),
                 'isAdditionalInfoShow': i18n.makeString(MENU.MODULEINFO_ADDITIONALINFO)}), EVENT_BUS_SCOPE.LOBBY)
            return

    def requestFilterData(self, filterType):
        self._updateFilterOptions(filterType)

    def _populate(self):
        super(StoreComponent, self)._populate()
        self.__filterHash = {'language': -1,
         'type': ''}
        self.__setNations()
        g_clientUpdateManager.addCallbacks({'inventory': self._onInventoryUpdate})
        g_itemsCache.onSyncCompleted += self._update
        g_instance.rentals.onRentChangeNotify += self._onTableUpdate
        self.__filterHash = self.__listToNationFilterData(self._getCurrentFilter())
        self._populateFilters(True)

    def _dispose(self):
        super(StoreComponent, self)._dispose()
        self._clearTableData()
        while len(self.__nations):
            self.__nations.pop()

        self.__nations = None
        self._tableType = None
        self._currentTab = None
        self.__filterHash.clear()
        self.__filterHash = None
        self.__invVehicles = None
        self.__clearSubFilter()
        g_itemsCache.onSyncCompleted -= self._update
        g_instance.rentals.onRentChangeNotify -= self._onTableUpdate
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._table = None
        return

    def _onInventoryUpdate(self, *args):
        self.__invVehicles = g_itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()

    def _update(self, *args):
        pass

    def __setNations(self):
        while len(self.__nations):
            self.__nations.pop()

        for name in GUI_NATIONS:
            if name in nations.AVAILABLE_NAMES:
                self.__nations.append(name)
                self.__nations.append(nations.INDICES[name])

        self.as_setNationsS(self.__nations)

    def _getTab(self, type, nation, filter):
        return None

    def _setTableData(self, filter, nation, type):
        nation = int(nation) if nation >= 0 else None
        if nation is not None:
            nation = getNationIndex(nation)
        filter = list(filter)
        self._clearTableData()
        self._tableType = type
        self._currentTab = self._getTab(self._tableType, nation, filter)
        self._table.setItemWrapper(self._currentTab.itemWrapper)
        self._table.setDataProviderValues(self._currentTab.buildItems(self.__invVehicles))
        self._table.as_setGoldS(g_itemsCache.items.stats.gold)
        self._table.as_setCreditsS(g_itemsCache.items.stats.credits)
        self._table.as_setTableTypeS(self._tableType)
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        self._table = viewPy

    def _populateFilters(self, init=False):
        vehicles = self.__invVehicles
        filterVehicle = None
        if g_currentVehicle.isPresent():
            filterVehicle = g_currentVehicle.item.intCD
        filter = self._getCurrentFilter()
        if filter[1] in (STORE_CONSTANTS.MODULE, STORE_CONSTANTS.SHELL):
            filter = list(AccountSettings.getFilter(self.getName() + '_' + filter[1]))
            typeSize = int(filter.pop(0))
            filterVehicle = filter[typeSize + 1]
        self.__clearSubFilter()
        self.__subFilter = {'current': str(filterVehicle),
         self._DATA_PROVIDER: []}
        vehicles.sort(reverse=True)
        for v in vehicles:
            filterElement = {'id': str(v.intCD),
             'nation': GUI_NATIONS_ORDER_INDEX[nations.NAMES[v.nationID]],
             'name': v.userName}
            self.__subFilter[self._DATA_PROVIDER].append(filterElement)

        if init:
            lang, itemType = self._getCurrentFilter()
            self.__filterHash.update({'language': lang,
             'type': itemType})
            self.as_setFilterTypeS(self.__filterHash)
        self.as_setSubFilterS(self.__subFilter)
        if init:
            self._updateFilterOptions(self.__filterHash['type'])
            self.as_completeInitS()
        return

    def _onTableUpdate(self, *args):
        params = self._getCurrentFilter()
        filter = AccountSettings.getFilter(self.getName() + '_' + params[1])
        self.requestTableData(params[0], params[1], filter)

    def _updateFilterOptions(self, filterType):
        mf = AccountSettings.getFilter(self.getName() + '_' + filterType)
        self.as_setFilterOptionsS(mf)
        self._update()

    def _getCurrentFilter(self):
        outcomeFilter = list(AccountSettings.getFilter(self.getName() + '_current'))
        return [outcomeFilter[0] if outcomeFilter[0] < len(GUI_NATIONS) else -1, outcomeFilter[1]]

    def _clearTableData(self):
        if self._table is not None:
            self._table.clearStoreTableDataProvider()
        if self._currentTab is not None:
            self._currentTab.clear()
        return

    def __listToNationFilterData(self, dataList):
        return {'language': dataList[0],
         'type': dataList[1]}

    def __clearSubFilter(self):
        dataProvider = self.__subFilter[self._DATA_PROVIDER]
        while dataProvider:
            dataProvider.pop().clear()

        self.__subFilter.clear()
        self.__subFilter = None
        return
