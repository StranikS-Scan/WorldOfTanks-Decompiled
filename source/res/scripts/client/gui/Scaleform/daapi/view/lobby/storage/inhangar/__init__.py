# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inhangar/__init__.py
import BigWorld
import nations
from account_helpers.AccountSettings import AccountSettings
from gui import GUI_NATIONS_ORDER_INDEX
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_data_provider import CarouselDataProvider
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import CarouselFilter
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import EventCriteriesGroup
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import BasicCriteriesGroup
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import createStorageDefVO, getBoosterType
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_SHOP import RES_SHOP
from gui.Scaleform.locale.STORAGE import STORAGE
from gui.shared.formatters import getItemPricesVO, text_styles, icons
from gui.shared.gui_items.Vehicle import getTypeUserName, getVehicleStateIcon, Vehicle, VEHICLE_TYPES_ORDER_INDICES
from gui.shared.money import Currency
from helpers import int2roman
from helpers.i18n import makeString as _ms

class StorageCarouselFilter(CarouselFilter):

    def __init__(self, criteries=None):
        super(StorageCarouselFilter, self).__init__()
        self._criteriesGroups = (EventCriteriesGroup(), BasicCriteriesGroup()) + (criteries or tuple())

    def load(self):
        defaultFilters = AccountSettings.getFilterDefaults(self._serverSections)
        for section in self._clientSections:
            defaultFilters.update(AccountSettings.getFilterDefault(section))

        self._filters = defaultFilters
        self.update(defaultFilters, save=False)

    def save(self):
        pass


class StorageCarouselDataProvider(CarouselDataProvider):

    def __init__(self, carouselFilter, itemsCache, currentVehicle):
        super(StorageCarouselDataProvider, self).__init__(carouselFilter, itemsCache, currentVehicle)
        self._baseCriteria = self.filter.criteria

    def buildList(self):
        self.clear()
        self.applyFilter()

    def applyFilter(self):
        self._buildVehicleItems()
        super(StorageCarouselDataProvider, self).applyFilter()

    def _filterByIndices(self):
        self._vehicleItems = [ self._vehicleItems[ndx] for ndx in self._filteredIndices ]
        self.refresh()

    def _buildVehicle(self, item):
        name = _getVehicleName(vehicle=item)
        description = _getVehicleDescription(vehicle=item)
        stateIcon, stateText = _getVehicleInfo(vehicle=item)
        vo = createStorageDefVO(item.intCD, name, description, item.inventoryCount, getItemPricesVO(item.getSellPrice())[0], item.getShopIcon(STORE_CONSTANTS.ICON_SIZE_SMALL), item.getShopIcon(), RES_SHOP.getVehicleIcon(STORE_CONSTANTS.ICON_SIZE_SMALL, 'empty_tank'), itemType=getBoosterType(item), nationFlagIcon=RES_SHOP.getNationFlagIcon(nations.NAMES[item.nationID]), infoImgSrc=stateIcon, infoText=stateText, contextMenuId=CONTEXT_MENU_HANDLER_TYPE.STORAGE_VEHICLES_REGULAR_ITEM)
        return vo

    def _getVehicleStats(self, vehicle):
        return {}

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        return (not vehicle.isInInventory,
         not vehicle.isEvent,
         GUI_NATIONS_ORDER_INDEX[vehicle.nationName],
         VEHICLE_TYPES_ORDER_INDICES[vehicle.type],
         vehicle.level,
         tuple(vehicle.buyPrices.itemPrice.price.iterallitems(byWeight=True)),
         vehicle.userName)


def _getVehicleName(vehicle):
    return ' '.join((getTypeUserName(vehicle.type, False), text_styles.neutral(int2roman(vehicle.level)), vehicle.shortUserName))


def _getVehicleDescription(vehicle):
    return ' '.join((_ms(STORAGE.CARD_VEHICLE_HOVER_MAXADDITIONALPRICELABEL), BigWorld.wg_getIntegralFormat(_calculateVehicleMaxAdditionalPrice(vehicle)), icons.credits()))


def _getVehicleInfo(vehicle):
    vState, vStateLvl = vehicle.getState()
    if vState not in Vehicle.CAN_SELL_STATES:
        infoTextStyle = text_styles.vehicleStatusCriticalText if vStateLvl == Vehicle.VEHICLE_STATE_LEVEL.CRITICAL else text_styles.vehicleStatusInfoText
        stateText = infoTextStyle(_ms(MENU.tankcarousel_vehiclestates(vState)))
        stateIcon = getVehicleStateIcon(vState)
        return (stateIcon, stateText)
    else:
        return (None, None)


def _calculateVehicleMaxAdditionalPrice(vehicle):
    items = list(vehicle.equipment.regularConsumables) + vehicle.optDevices + vehicle.shells
    return sum((item.getSellPrice().price.get(Currency.CREDITS, 0) * getattr(item, 'count', 1) for item in items if item is not None))
