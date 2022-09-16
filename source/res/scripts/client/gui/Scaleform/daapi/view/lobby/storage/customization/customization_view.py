# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/customization/customization_view.py
import math
from typing import Optional
import nations
from adisp import adisp_process
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs.confirm_customization_item_dialog_meta import ConfirmC11nSellMeta
from gui.Scaleform.daapi.view.lobby.event_boards.event_helpers import LEVELS_RANGE
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import event_dispatcher
from helpers import dependency
from helpers.i18n import makeString as _ms
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import createStorageDefVO, customizationPreview, getAvailableForSellCustomizationCount
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import isCustomizationAvailableForSell
from gui.Scaleform.daapi.view.lobby.customization.shared import getSuitableText, isC11nEnabled
from gui.Scaleform.daapi.view.meta.StorageCategoryCustomizationViewMeta import StorageCategoryCustomizationViewMeta
from gui.shared.formatters import getItemPricesVO
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from gui.shared.utils.functions import makeTooltip
from skeletons.gui.customization import ICustomizationService
from shared_utils import CONST_CONTAINER

class _CustomizationFilterBit(CONST_CONTAINER):
    STYLE = 1
    PAINT = 2
    CAMOUFLAGE = 4
    PROJECTION_DECAL = 8
    EMBLEM = 16
    PERSONAL_NUMBER = 32
    MODIFICATION = 64


_TYPE_BIT_TO_CUSTOMIZATION_TYPE_MAP = {_CustomizationFilterBit.STYLE: (GUI_ITEM_TYPE.STYLE,),
 _CustomizationFilterBit.PAINT: (GUI_ITEM_TYPE.PAINT,),
 _CustomizationFilterBit.CAMOUFLAGE: (GUI_ITEM_TYPE.CAMOUFLAGE,),
 _CustomizationFilterBit.PROJECTION_DECAL: (GUI_ITEM_TYPE.PROJECTION_DECAL,),
 _CustomizationFilterBit.EMBLEM: (GUI_ITEM_TYPE.EMBLEM,),
 _CustomizationFilterBit.PERSONAL_NUMBER: (GUI_ITEM_TYPE.PERSONAL_NUMBER, GUI_ITEM_TYPE.INSCRIPTION),
 _CustomizationFilterBit.MODIFICATION: (GUI_ITEM_TYPE.MODIFICATION,)}
_CUSTOMIZATION_ITEM_TYPES = (GUI_ITEM_TYPE.STYLE,
 GUI_ITEM_TYPE.PAINT,
 GUI_ITEM_TYPE.CAMOUFLAGE,
 GUI_ITEM_TYPE.PROJECTION_DECAL,
 GUI_ITEM_TYPE.EMBLEM,
 GUI_ITEM_TYPE.PERSONAL_NUMBER,
 GUI_ITEM_TYPE.INSCRIPTION,
 GUI_ITEM_TYPE.MODIFICATION)
_TYPE_FILTER_ITEMS = [{'filterValue': _CustomizationFilterBit.STYLE,
  'selected': False,
  'tooltip': makeTooltip(body=backport.text(R.strings.tooltips.customization.storage.filters.style.title())),
  'icon': backport.image(R.images.gui.maps.icons.storage.filters.style())},
 {'filterValue': _CustomizationFilterBit.PAINT,
  'selected': False,
  'tooltip': makeTooltip(body=backport.text(R.strings.tooltips.customization.storage.filters.paints.title())),
  'icon': backport.image(R.images.gui.maps.icons.storage.filters.paints())},
 {'filterValue': _CustomizationFilterBit.CAMOUFLAGE,
  'selected': False,
  'tooltip': makeTooltip(body=backport.text(R.strings.tooltips.customization.storage.filters.camouflage.title())),
  'icon': backport.image(R.images.gui.maps.icons.storage.filters.camouflage())},
 {'filterValue': _CustomizationFilterBit.PROJECTION_DECAL,
  'selected': False,
  'tooltip': makeTooltip(body=backport.text(R.strings.tooltips.customization.storage.filters.decals.title())),
  'icon': backport.image(R.images.gui.maps.icons.storage.filters.decals())},
 {'filterValue': _CustomizationFilterBit.EMBLEM,
  'selected': False,
  'tooltip': makeTooltip(body=backport.text(R.strings.tooltips.customization.storage.filters.emblems.title())),
  'icon': backport.image(R.images.gui.maps.icons.storage.filters.emblems())},
 {'filterValue': _CustomizationFilterBit.PERSONAL_NUMBER,
  'selected': False,
  'tooltip': makeTooltip(body=backport.text(R.strings.tooltips.customization.storage.filters.text.title())),
  'icon': backport.image(R.images.gui.maps.icons.storage.filters.text())},
 {'filterValue': _CustomizationFilterBit.MODIFICATION,
  'selected': False,
  'tooltip': makeTooltip(body=backport.text(R.strings.tooltips.customization.storage.filters.effects.title())),
  'icon': backport.image(R.images.gui.maps.icons.storage.filters.effects())}]
_TABS_SORT_ORDER = dict(((n, idx) for idx, n in enumerate(_CUSTOMIZATION_ITEM_TYPES)))

class _VehiclesFilter(object):
    __slots__ = ('vehicles',)

    def __init__(self, invVehicles):
        self.vehicles = {nation:{level:[] for level in LEVELS_RANGE} for nation in nations.MAP}
        for vehicle in invVehicles:
            vehicleType = vehicle.descriptor.type
            self.vehicles[vehicleType.customizationNationID][vehicle.level].append(vehicle)

    def getVehicles(self, item):
        itemFilter = item.descriptor.filter
        levels = []
        nationsVeh = []
        if itemFilter is not None and itemFilter.include:
            for node in itemFilter.include:
                if node.levels:
                    levels += node.levels
                if node.nations:
                    nationsVeh += node.nations

        levels = levels or LEVELS_RANGE
        nationsVeh = nationsVeh or nations.MAP.keys()
        for nation in nationsVeh:
            for level in levels:
                for vehicle in self.vehicles[nation][level]:
                    yield vehicle

        return


def _getCustomizationCriteria(invVehicles):

    def criteria(item):
        if item.isVehicleBound:
            boundVehicles = item.getBoundVehicles()
            if boundVehicles:
                inventoryVehicles = set((vehicle.intCD for vehicle in invVehicles.getVehicles(item)))
                return not boundVehicles.issubset(inventoryVehicles)
        return all((not item.mayInstall(vehicle) for vehicle in invVehicles.getVehicles(item)))

    return criteria


class StorageCategoryCustomizationView(StorageCategoryCustomizationViewMeta):
    _service = dependency.descriptor(ICustomizationService)
    filterItems = _TYPE_FILTER_ITEMS

    @dependency.replace_none_kwargs(c11nService=ICustomizationService)
    def navigateToCustomization(self, c11nService=None):
        if isC11nEnabled():
            c11nService.showCustomization()
        else:
            event_dispatcher.showHangar()

    @adisp_process
    def sellCustomizationItem(self, itemCD, vehicleCD=None):
        item = self._itemsCache.items.getItemByCD(int(itemCD))
        vehicleCD = int(vehicleCD) if vehicleCD is not None and not math.isnan(vehicleCD) else None
        vehicle = self._itemsCache.items.getItemByCD(vehicleCD) if vehicleCD is not None else None
        inventoryCount = getAvailableForSellCustomizationCount(item, vehicleCD)
        yield DialogsInterface.showDialog(ConfirmC11nSellMeta(item.intCD, inventoryCount, self.__sellItem, vehicle=vehicle))
        return

    def __sellItem(self, itemCD, count, vehicle):
        item = self._itemsCache.items.getItemByCD(itemCD)
        self._service.sellItem(item, count, vehicle=vehicle)

    def previewItem(self, itemCD, vehicleCD):
        vehicleCD = int(vehicleCD) if vehicleCD is not None and not math.isnan(vehicleCD) else None
        customizationPreview(itemCD=int(itemCD), vehicleCD=vehicleCD)
        return

    def scrolledToBottom(self):
        pass

    def _getClientSectionKey(self):
        pass

    def _getFilteredCriteria(self):
        criteria = super(StorageCategoryCustomizationView, self)._getFilteredCriteria()
        typeIds = []
        for bit in _TYPE_BIT_TO_CUSTOMIZATION_TYPE_MAP.iterkeys():
            if self._filterMask & bit:
                typeIds += _TYPE_BIT_TO_CUSTOMIZATION_TYPE_MAP[bit]

        if typeIds:
            criteria |= REQ_CRITERIA.ITEM_TYPES(*typeIds)
        return criteria

    def _getItemTypeID(self):
        return _CUSTOMIZATION_ITEM_TYPES

    def _getRequestCriteria(self, invVehicles):
        criteria = REQ_CRITERIA.CUSTOMIZATION.FULL_INVENTORY
        if invVehicles:
            criteria |= REQ_CRITERIA.CUSTOM(_getCustomizationCriteria(_VehiclesFilter(invVehicles)))
        return criteria

    def _getInvVehicleCriteria(self):
        criteria = REQ_CRITERIA.INVENTORY
        criteria |= ~REQ_CRITERIA.VEHICLE.IS_OUTFIT_LOCKED
        criteria |= ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE
        criteria |= ~REQ_CRITERIA.VEHICLE.MAPS_TRAINING
        return criteria

    def _getVoList(self):
        totalItems = self._getItemList()
        filterCriteria = self._getFilteredCriteria()
        dataProviderVoItemsList = []
        self._currentCount = 0
        self._totalCount = 0
        for item in sorted(totalItems.itervalues(), cmp=self._getComparator()):
            itemVoList = self._getVoListForItem(item)
            self._totalCount += self._calcItemsCount(itemVoList)
            if filterCriteria(item):
                dataProviderVoItemsList += itemVoList

        self._currentCount = self._calcItemsCount(dataProviderVoItemsList)
        return dataProviderVoItemsList

    def _calcItemsCount(self, itemList):
        return sum(((item['count'] if not item['isRentable'] else 1) for item in itemList))

    def _getVoListForItem(self, item):
        if not item.isVehicleBound:
            voList = [self._getVO(item)]
        else:
            voList = []
            if item.boundInventoryCount() > 0:
                inventoryVehicles = [ vehicle.intCD for vehicle in _VehiclesFilter(self._invVehicles).getVehicles(item) ]
                vehicleDiff = item.getBoundVehicles().difference(inventoryVehicles)
                voList = [ self._getVO(item, vehicle) for vehicle in vehicleDiff if item.boundInventoryCount(vehicle) ]
            if item.inventoryCount > 0:
                voList.append(self._getVO(item))
        return voList

    def _getVO(self, item, vehicleCD=None):
        priceVO = getItemPricesVO(item.getSellPrice())[0]
        title = item.userName
        tooltipKey = TOOLTIPS.getItemBoxTooltip(item.itemTypeName)
        if tooltipKey:
            title = _ms(tooltipKey, group=item.userType, value=item.userName)
        if item.itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL:
            formfactor = item.formfactor
        else:
            formfactor = ''
        icon = item.icon
        levelIcon = ''
        customizationSuitableText = backport.text(R.strings.storage.customizationSuitable.label())
        if vehicleCD is None:
            if not item.descriptor.filter or not item.descriptor.filter.include:
                customizationSuitableText = backport.text(R.strings.storage.customizationSuitableForAll.label())
            else:
                customizationSuitableText += getSuitableText(item)
            count = item.inventoryCount
            vehicle = None
        else:
            vehicle = self._itemsCache.items.getItemByCD(vehicleCD)
            customizationSuitableText += vehicle.shortUserName
            count = item.boundInventoryCount(vehicleCD)
        if item.isProgressive:
            if item.isProgressionRewindEnabled:
                levelIcon = backport.image(R.images.gui.maps.icons.customization.progression_rewind())
                level = item.getProgressionLevel(vehicle)
                if level > 0:
                    icon = item.iconUrlByProgressionLevel(level)
            else:
                level = item.getProgressionLevel(vehicle)
                if level > 0:
                    if item.itemTypeID == GUI_ITEM_TYPE.STYLE:
                        levelIconPath = R.images.gui.maps.icons.customization.progression_styles.icons
                    else:
                        levelIconPath = R.images.gui.maps.icons.customization.progression_icons
                    levelIcon = backport.image(levelIconPath.dyn('level_{}'.format(level))())
                    if item.itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL:
                        icon = item.previewIconUrlByProgressionLevel(level)
                    else:
                        icon = item.iconUrlByProgressionLevel(level)
        isAvailableForSell = isCustomizationAvailableForSell(item, vehicleCD)
        isPreviewAvailable = item.itemTypeID == GUI_ITEM_TYPE.STYLE
        vo = createStorageDefVO(itemID=item.intCD, title=title, description=customizationSuitableText, count=count, price=priceVO if isAvailableForSell else None, image=icon, imageAlt='altimage', contextMenuId=CONTEXT_MENU_HANDLER_TYPE.STORAGE_CUSTOMZIZATION_ITEM, enabled=isAvailableForSell)
        vo.update({'previewAvailable': isPreviewAvailable,
         'previewTooltip': backport.text(R.strings.storage.stylePreview.tooltip()),
         'progressiveLevelIcon': levelIcon,
         'formfactor': formfactor,
         'vehicleCD': vehicleCD,
         'isWideImage': item.isWide(),
         'isRentable': item.isRentable})
        return vo

    def _getComparator(self):

        def _comparator(a, b):
            return cmp(_TABS_SORT_ORDER[a.itemTypeID], _TABS_SORT_ORDER[b.itemTypeID]) or cmp(a.userName, b.userName)

        return _comparator
