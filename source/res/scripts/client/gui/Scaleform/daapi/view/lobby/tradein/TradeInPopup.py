# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/tradein/TradeInPopup.py
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleBasicVO
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import packHeaderColumnData
from gui.Scaleform.daapi.view.meta.TradeInPopupMeta import TradeInPopupMeta
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.events import VehicleBuyEvent
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.functions import makeTooltip
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.game_control import ITradeInController
from gui.shared.tooltips.formatters import packItemActionTooltipData
from skeletons.gui.shared import IItemsCache

class TradeInPopup(TradeInPopupMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    tradeIn = dependency.descriptor(ITradeInController)

    def __init__(self, ctx=None):
        super(TradeInPopup, self).__init__(ctx)
        data = ctx['data']
        self.__tradeInDP = None
        self.__tradeInVehCD = int(data.tradeIn)
        self.__tradeOffVehCD = int(data.tradeOff)
        return

    def _populate(self):
        super(TradeInPopup, self)._populate()
        self.__tradeInDP = _TradeInDataProvider()
        self.__tradeInDP.setFlashObject(self.as_getDPS())
        self.__fillDP()
        self.itemsCache.onSyncCompleted += self.__onResync
        self.__initControls()

    def _dispose(self):
        self.itemsCache.onSyncCompleted -= self.__onResync
        self.__tradeInDP.fini()
        self.__tradeInDP = None
        super(TradeInPopup, self)._dispose()
        return

    def __initControls(self):
        headers = [packHeaderColumnData('nationID', 49, 40, tooltip=DIALOGS.TRADEINPOPOVER_SORTING_NATION, icon=RES_ICONS.MAPS_ICONS_FILTERS_NATIONS_ALL, enabled=True),
         packHeaderColumnData('typeIndex', 45, 40, tooltip=DIALOGS.TRADEINPOPOVER_SORTING_VEHTYPE, icon=RES_ICONS.MAPS_ICONS_FILTERS_TANKS_ALL, enabled=True),
         packHeaderColumnData('level', 45, 40, tooltip=DIALOGS.TRADEINPOPOVER_SORTING_VEHLVL, icon=RES_ICONS.MAPS_ICONS_BUTTONS_TAB_SORT_BUTTON_LEVEL_6_8, enabled=True),
         packHeaderColumnData('shortUserName', 148, 40, label=DIALOGS.TRADEINPOPOVER_SORTING_VEHNAME_HEADER, tooltip=DIALOGS.TRADEINPOPOVER_SORTING_VEHNAME, enabled=True, verticalTextAlign='center'),
         packHeaderColumnData('price', 95, 40, label=DIALOGS.TRADEINPOPOVER_SORTING_SAVING_FORMATTED, tooltip=DIALOGS.TRADEINPOPOVER_SORTING_SAVING, enabled=True, verticalTextAlign='center')]
        self.as_setInitDataS({'title': DIALOGS.TRADEINPOPOVER_TITLE,
         'description': DIALOGS.TRADEINPOPOVER_DESCR,
         'defaultSortField': 'price',
         'defaultSortDirection': 'descending',
         'tableHeaders': headers})

    def onWindowClose(self):
        self.destroy()

    def onSelectVehicle(self, vehicle):
        self.fireEvent(VehicleBuyEvent(VehicleBuyEvent.VEHICLE_SELECTED, vehicle))
        self.onWindowClose()

    def __onResync(self, reason, diff):
        if reason == CACHE_SYNC_REASON.SHOP_RESYNC or GUI_ITEM_TYPE.VEHICLE in diff:
            self.__tradeInDP.clear()
            self.__fillDP()

    def __fillDP(self):
        tradeInVehicle = self.itemsCache.items.getItemByCD(self.__tradeInVehCD)
        self.__tradeInDP.setSelectedID(self.__tradeOffVehCD)
        self.__tradeInDP.buildList(self.tradeIn.getTradeOffVehicles(tradeInVehicle.level))
        self.__tradeInDP.refresh()


class _TradeInDataProvider(SortableDAAPIDataProvider):

    def __init__(self):
        super(_TradeInDataProvider, self).__init__()
        self.__list = []
        self.__mapping = {}
        self.__selectedID = None
        return

    @property
    def collection(self):
        return self.__list

    def emptyItem(self):
        return None

    def clear(self):
        self.__list = []
        self.__mapping.clear()
        self.__selectedID = None
        return

    def fini(self):
        self.clear()
        self.destroy()

    def getSelectedIdx(self):
        return self.__mapping[self.__selectedID] if self.__selectedID in self.__mapping else -1

    def setSelectedID(self, selId):
        self.__selectedID = selId

    def buildList(self, changedVehsCDs):
        for idx, (vehCD, veh) in enumerate(changedVehsCDs.iteritems()):
            self.__list.append(self.__makeVO(veh))
            self.__mapping[vehCD] = idx

    def pyGetSelectedIdx(self):
        return self.getSelectedIdx()

    def pySortOn(self, fields, order):
        super(_TradeInDataProvider, self).pySortOn(fields, order)
        self.__rebuildMapping()
        self.refresh()

    def __rebuildMapping(self):
        self.__mapping = dict(map(lambda (idx, item): (item['intCD'], idx), enumerate(self.sortedCollection)))

    def __makeVO(self, vehicle):
        vehicleVO = makeVehicleBasicVO(vehicle)
        if vehicleVO is None:
            return
        else:
            vehicleVO['price'] = vehicle.tradeOffPrice.getSignValue(Currency.GOLD)
            vehicleVO['actionPrice'] = self._getItemPriceActionData(vehicle)
            vState, vStateLvl = vehicle.getState()
            if vState in (Vehicle.VEHICLE_STATE.DAMAGED,
             Vehicle.VEHICLE_STATE.EXPLODED,
             Vehicle.VEHICLE_STATE.DESTROYED,
             Vehicle.VEHICLE_STATE.BATTLE,
             Vehicle.VEHICLE_STATE.IN_PREBATTLE,
             Vehicle.VEHICLE_STATE.LOCKED):
                vehicleVO['isReadyToFight'] = False
                vehicleVO['enabled'] = False
                vehicleVO['tooltip'] = makeTooltip('#tooltips:tradeInVehicleStatus/%s/header' % vState, '#tooltips:tradeInVehicleStatus/%s/body' % vState)
            return vehicleVO

    def _getItemPriceActionData(self, vehicle):
        return packItemActionTooltipData(vehicle) if vehicle.buyPrices.itemPrice.isActionPrice() else None
