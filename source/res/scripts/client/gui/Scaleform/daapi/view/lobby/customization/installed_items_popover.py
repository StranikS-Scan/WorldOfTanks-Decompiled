# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/installed_items_popover.py
from collections import namedtuple
from gui.Scaleform.daapi.view.lobby.customization.shared import TYPES_ORDER
from gui.Scaleform.daapi.view.meta.CustomizationItemsPopoverMeta import CustomizationItemsPopoverMeta
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.shared.formatters import text_styles, getItemPricesVO
from helpers import dependency
from helpers.i18n import makeString as _ms
from items.components.c11n_constants import SeasonType
from skeletons.gui.customization import ICustomizationService
from CurrentVehicle import g_currentVehicle
from gui.customization.shared import isServiceItem, isOutfitVisuallyEmpty
_PopoverHeadersVO = namedtuple('_PopoverHeadersVO', ('title', 'checkBoxText', 'counterText', 'currentSeasonImage'))
_RegionId = namedtuple('_RegionId', ('areaId', 'slotType', 'regionIdx'))
_DisplayedItemsVO = namedtuple('_DisplayedItemsVO', ('id', 'icon', 'userName', 'numItems', 'isHistoric', 'price', 'isApplied', 'isWide', 'itemsList'))

class InstalledItemsPopover(CustomizationItemsPopoverMeta):
    service = dependency.descriptor(ICustomizationService)

    def __init__(self, ctx=None):
        super(InstalledItemsPopover, self).__init__()
        self._isNonHistoric = False

    def onWindowClose(self):
        self.destroy()

    def remove(self, intCD, itemsList):
        for item in itemsList:
            self.__ctx.removeItemFromRegion(self.__ctx.currentSeason, item.areaId, item.slotType, item.regionIdx)

    def removeAll(self):

        def nonHistoricRemoveFilter(item):
            return not item.isHistorical()

        self.__ctx.removeItemsFromOutfit(self.__ctx.currentOutfit, nonHistoricRemoveFilter if self._isNonHistoric else None)
        return

    def showOnlyNonHistoric(self, value):
        self._isNonHistoric = value
        self.__update()

    def _populate(self):
        super(InstalledItemsPopover, self)._populate()
        self.__ctx = self.service.getCtx()
        self.__ctx.onCacheResync += self.__update
        self.__ctx.onCustomizationSeasonChanged += self.__update
        self.__ctx.onCustomizationItemInstalled += self.__update
        self.__ctx.onCustomizationItemsRemoved += self.__update
        self.__ctx.onChangesCanceled += self.__update
        self._assignedDP = InstalledItemsPopoverDataProvider(self.__ctx)
        self._assignedDP.setFlashObject(self.as_getDPS())
        self.__update()

    def _dispose(self):
        self.__ctx.onChangesCanceled -= self.__update
        self.__ctx.onCustomizationItemsRemoved -= self.__update
        self.__ctx.onCustomizationItemInstalled -= self.__update
        self.__ctx.onCustomizationSeasonChanged -= self.__update
        self.__ctx.onCacheResync -= self.__update
        self.__ctx = None
        super(InstalledItemsPopover, self)._dispose()
        return

    def __setHeader(self):
        nonHistoricItemsCount = sum((int(not it.isHistorical()) for it in self.__ctx.currentOutfit.items()))
        checkBoxText = '{}'.format(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_ITEMSPOPOVER_HISTORICCHECKBOX_ITEMS))
        counterText = text_styles.vehicleStatusSimpleText('({})'.format(nonHistoricItemsCount))
        currentSeasonImage = ''
        seasonLabel = ''
        if self.__ctx.currentSeason == SeasonType.SUMMER:
            currentSeasonImage = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_ITEMS_POPOVER_SUMMER_BACK_LIST
            seasonLabel = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_MAPTYPE_SUMMER
        elif self.__ctx.currentSeason == SeasonType.DESERT:
            currentSeasonImage = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_ITEMS_POPOVER_DESERT_BACK_LIST
            seasonLabel = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_MAPTYPE_DESERT
        elif self.__ctx.currentSeason == SeasonType.WINTER:
            currentSeasonImage = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_ITEMS_POPOVER_WINTER_BACK_LIST
            seasonLabel = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_MAPTYPE_WINTER
        isClear = False
        clearMessage = ''
        if self._isNonHistoric and nonHistoricItemsCount == 0:
            isClear = True
            clearMessage = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_ITEMSPOPOVER_CLEAR_NONHISTORICMASSAGE
        elif isOutfitVisuallyEmpty(self.__ctx.currentOutfit):
            isClear = True
            clearMessage = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_ITEMSPOPOVER_CLEAR_MASSAGE
        title = text_styles.highTitle(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_ITEMSPOPOVER_TITLE_ITEMS, mapType=_ms(seasonLabel)))
        self.as_showClearMessageS(isClear, text_styles.main(clearMessage))
        self.as_setHeaderDataS(_PopoverHeadersVO(title, checkBoxText, counterText, currentSeasonImage)._asdict())

    def __update(self):
        self._assignedDP.rebuildList(self._isNonHistoric)
        self.__setHeader()


class _ItemGroupDescription(object):
    __slots__ = ('item', 'numItems', 'regionIdList', 'slotType', 'isFromInventory')

    def __init__(self, item, numItems, regionIdList, slotType, isFromInventory):
        self.item = item
        self.numItems = numItems
        self.regionIdList = regionIdList
        self.slotType = slotType
        self.isFromInventory = isFromInventory


class InstalledItemsPopoverDataProvider(SortableDAAPIDataProvider):
    service = dependency.descriptor(ICustomizationService)

    def __init__(self, ctx):
        super(InstalledItemsPopoverDataProvider, self).__init__()
        self._list = []
        self.__ctx = ctx

    @property
    def collection(self):
        return self._list

    def emptyItem(self):
        return None

    def clear(self):
        self._list = []

    def fini(self):
        self.__ctx = None
        self.clear()
        self._dispose()
        return

    def buildList(self, isNonHistoric):
        self.clear()
        hasCustomDefaultCamouflage = g_currentVehicle.item.descriptor.type.hasCustomDefaultCamouflage
        purchaseItems = [ it for it in self.__ctx.getPurchaseItems() if not it.isDismantling and it.group == self.__ctx.currentSeason ]
        purchaseItemsGroups = {}
        for it in purchaseItems:
            if not isNonHistoric or not it.item.isHistorical():
                key = (it.item.intCD, it.isFromInventory)
                if key not in purchaseItemsGroups:
                    purchaseItemsGroups[key] = _ItemGroupDescription(it.item, 0, [], it.slot, it.isFromInventory)
                purchaseItemsGroups[key].numItems += 1
                purchaseItemsGroups[key].regionIdList.append(_RegionId(it.areaID, it.slot, it.regionID))

        notModifiedOutfit = self.__ctx.getNotModifiedItems(self.__ctx.currentSeason)
        notModifiedItemsGroups = {}
        for container in notModifiedOutfit.containers():
            for slot in container.slots():
                for idx in range(slot.capacity()):
                    item = slot.getItem(idx)
                    if item:
                        if isServiceItem(item) and hasCustomDefaultCamouflage:
                            continue
                        if not isNonHistoric or not item.isHistorical():
                            if item.intCD not in notModifiedItemsGroups:
                                notModifiedItemsGroups[item.intCD] = _ItemGroupDescription(item, 0, [], slot.getType(), True)
                            notModifiedItemsGroups[item.intCD].numItems += 1
                            notModifiedItemsGroups[item.intCD].regionIdList.append(_RegionId(container.getAreaID(), slot.getType(), idx))

        if purchaseItemsGroups and notModifiedItemsGroups:
            self._list.append({'userName': text_styles.main(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_NONHISTORIC_TABLEHEADERS_NEW)),
             'isTitle': True})
        purchaseItemsGroupsSorted = sorted(purchaseItemsGroups.values(), key=lambda v: (TYPES_ORDER.index(v.slotType), v.item.intCD, not v.isFromInventory))
        for group in purchaseItemsGroupsSorted:
            self._list.append(self._makeVO(group, False, group.isFromInventory))

        if purchaseItemsGroups and notModifiedItemsGroups:
            self._list.append({'userName': text_styles.main(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_NONHISTORIC_TABLEHEADERS_PURCHASE)),
             'isTitle': True})
        notModifiedItemsGroupsSorted = sorted(notModifiedItemsGroups.values(), key=lambda v: (TYPES_ORDER.index(v.slotType), v.item.intCD))
        for group in notModifiedItemsGroupsSorted:
            self._list.append(self._makeVO(group, True))

    def rebuildList(self, isNonHistoric):
        self.buildList(isNonHistoric)
        self.refresh()

    def _makeVO(self, itemGroupDescription, isAlreadyPurchased, isFromInventory=False):
        imageIcon = ''
        userName = ''
        numItemsStr = ''
        price = None
        item = self.service.getItemByCD(itemGroupDescription.item.intCD)
        regionIdListVO = []
        if item is not None:
            imageIcon = item.icon
            userName = text_styles.main(item.userName)
            if not isAlreadyPurchased and not isFromInventory:
                numItemsStr = text_styles.main('{} x  '.format(itemGroupDescription.numItems))
                price = getItemPricesVO(item.buyPrices.itemPrice)[0]
            else:
                numItemsStr = text_styles.main('{} '.format(itemGroupDescription.numItems))
            regionIdListVO = [ regionId._asdict() for regionId in itemGroupDescription.regionIdList ]
        return _DisplayedItemsVO(item.intCD, imageIcon, userName, numItemsStr, item.isHistorical(), price, isAlreadyPurchased, item.isWide(), regionIdListVO)._asdict()
