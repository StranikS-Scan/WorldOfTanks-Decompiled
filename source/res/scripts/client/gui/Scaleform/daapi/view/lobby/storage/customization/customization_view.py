# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/customization/customization_view.py
import nations
from gui.Scaleform.daapi.view.lobby.event_boards.event_helpers import LEVELS_RANGE
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.locale.RES_SHOP import RES_SHOP
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared import event_dispatcher
from helpers import dependency
from helpers.i18n import makeString as _ms
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import createStorageDefVO, customizationPreview
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import customizationAvailableForSell
from gui.Scaleform.daapi.view.lobby.customization.shared import getSuitableText, isC11nEnabled
from gui.Scaleform.locale.STORAGE import STORAGE
from gui.Scaleform.daapi.view.meta.StorageCategoryCustomizationViewMeta import StorageCategoryCustomizationViewMeta
from gui.shared.formatters import getItemPricesVO
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from skeletons.gui.customization import ICustomizationService
_TABS_SORT_ORDER = dict(((n, idx) for idx, n in enumerate((GUI_ITEM_TYPE.STYLE, GUI_ITEM_TYPE.CAMOUFLAGE))))

class _VehiclesFilter(object):
    __slots__ = ('vehicles',)

    def __init__(self, invVehicles):
        self.vehicles = {nation:{level:[] for level in LEVELS_RANGE} for nation in nations.MAP}
        for vehicle in invVehicles:
            self.vehicles[vehicle.nationID][vehicle.level].append(vehicle)

    def getVehicles(self, item):
        itemFilter = item.descriptor.filter
        levels = LEVELS_RANGE
        nationsVeh = nations.MAP.keys()
        if itemFilter is not None and itemFilter.include:
            includeFilter = itemFilter.include[0]
            levels = includeFilter.levels if includeFilter.levels else levels
            nationsVeh = includeFilter.nations if includeFilter.nations else nationsVeh
        for nation in nationsVeh:
            for level in levels:
                for vehicle in self.vehicles[nation][level]:
                    yield vehicle

        return


def _getCustomizationCriteria(invVehicles):

    def criteria(item):
        for vehicle in invVehicles.getVehicles(item):
            if item.mayInstall(vehicle):
                return False

        return True

    return criteria


class StorageCategoryCustomizationView(StorageCategoryCustomizationViewMeta):

    @dependency.replace_none_kwargs(c11nService=ICustomizationService)
    def navigateToCustomization(self, c11nService=None):
        if isC11nEnabled():
            c11nService.showCustomization()
        else:
            event_dispatcher.showHangar()

    def sellItem(self, itemId):
        customizationPreview(int(itemId))

    def _populate(self):
        super(StorageCategoryCustomizationView, self)._populate()
        self._itemsCache.onSyncCompleted += self.__onCacheResync

    def _dispose(self):
        super(StorageCategoryCustomizationView, self)._dispose()
        self._itemsCache.onSyncCompleted -= self.__onCacheResync

    def _getItemTypeID(self):
        return (GUI_ITEM_TYPE.STYLE, GUI_ITEM_TYPE.CAMOUFLAGE)

    def _buildItems(self):
        super(StorageCategoryCustomizationView, self)._buildItems()
        self.as_showDummyScreenS(len(self._dataProvider.collection) == 0)

    def _getRequestCriteria(self, invVehicles):
        criteria = REQ_CRITERIA.INVENTORY
        criteria |= REQ_CRITERIA.TYPE_CRITERIA((GUI_ITEM_TYPE.STYLE, GUI_ITEM_TYPE.CAMOUFLAGE), _getCustomizationCriteria(_VehiclesFilter(invVehicles)))
        return criteria

    def _getInvVehicleCriteria(self):
        return REQ_CRITERIA.INVENTORY ^ REQ_CRITERIA.VEHICLE.EVENT_BATTLE | ~REQ_CRITERIA.VEHICLE.EXPIRED_RENT

    def _getVO(self, item):
        priceVO = getItemPricesVO(item.getSellPrice())[0]
        title = item.userName
        tooltipKey = TOOLTIPS.getItemBoxTooltip(item.itemTypeName)
        if tooltipKey:
            title = _ms(tooltipKey, group=item.userType, value=item.userName)
        if item.itemTypeID == GUI_ITEM_TYPE.STYLE:
            icon = RES_SHOP.MAPS_SHOP_CUSTOMIZATION_180X135_STYLE
        else:
            icon = RES_SHOP.MAPS_SHOP_CUSTOMIZATION_180X135_CAMO
        vo = createStorageDefVO(item.intCD, title, ' '.join([_ms(STORAGE.CUSTOMIZATIONSUITABLE_LABEL), getSuitableText(item)]), item.inventoryCount, priceVO if customizationAvailableForSell(item) else None, icon, 'altimage', contextMenuId=CONTEXT_MENU_HANDLER_TYPE.STORAGE_CUSTOMZIZATION_ITEM)
        return vo

    def __onCacheResync(self, *args):
        self._buildItems()

    def _getComparator(self):

        def _comparator(a, b):
            return cmp(_TABS_SORT_ORDER[a.itemTypeID], _TABS_SORT_ORDER[b.itemTypeID]) or cmp(a.userName, b.userName)

        return _comparator
