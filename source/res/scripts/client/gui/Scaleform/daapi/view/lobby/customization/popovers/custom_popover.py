# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/popovers/custom_popover.py
from itertools import ifilter
import typing
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.customization.popovers import orderKey, C11nPopoverItemData
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.customization.shared import ITEM_TYPE_TO_SLOT_TYPE, getSlotDataFromSlot
from gui.Scaleform.daapi.view.meta.CustomizationItemsPopoverMeta import CustomizationItemsPopoverMeta
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.customization.shared import isOutfitVisuallyEmpty, SEASON_TYPE_TO_NAME, C11nId
from gui.shared.formatters import text_styles, getItemPricesVO
from helpers import dependency
from skeletons.gui.customization import ICustomizationService

class CustomPopover(CustomizationItemsPopoverMeta):
    __service = dependency.descriptor(ICustomizationService)

    def __init__(self, ctx=None):
        super(CustomPopover, self).__init__(ctx)
        self.__isNonHistoric = False

    def onWindowClose(self):
        self.destroy()

    def remove(self, intCD, slotIds):
        self.__ctx.mode.removeFromSlots(slotIds)

    def removeAll(self):
        filterMethod = (lambda item: not item.isHistorical()) if self.__isNonHistoric else None
        self.__ctx.mode.removeItemsFromSeason(filterMethod=filterMethod)
        return

    def showOnlyNonHistoric(self, value):
        self.__isNonHistoric = value
        self._assignedDP.setNonHistoric(self.__isNonHistoric)
        self.__update()

    def _populate(self):
        super(CustomPopover, self)._populate()
        self.__ctx = self.__service.getCtx()
        self.__ctx.events.onCacheResync += self.__update
        self.__ctx.events.onSeasonChanged += self.__update
        self.__ctx.events.onItemInstalled += self.__update
        self.__ctx.events.onItemsRemoved += self.__update
        self.__ctx.events.onChangesCanceled += self.__update
        self._assignedDP = CustomPopoverDataProvider(self.__isNonHistoric)
        self._assignedDP.setFlashObject(self.as_getDPS())
        self.__update()

    def _dispose(self):
        if self.__ctx.events is not None:
            self.__ctx.events.onChangesCanceled -= self.__update
            self.__ctx.events.onItemsRemoved -= self.__update
            self.__ctx.events.onItemInstalled -= self.__update
            self.__ctx.events.onSeasonChanged -= self.__update
            self.__ctx.events.onCacheResync -= self.__update
        self.__ctx = None
        super(CustomPopover, self)._dispose()
        return

    def __setHeader(self):
        outfit = self.__ctx.mode.currentOutfit
        nonHistoricItems = [ intCD for intCD in outfit.items() if not self.__service.getItemByCD(intCD).isHistorical() ]
        nonHistoricItemsCount = len(nonHistoricItems)
        checkBoxLabel = R.strings.vehicle_customization.customization.itemsPopover.historicCheckBox.items
        checkBoxLabel = backport.text(checkBoxLabel())
        counterLabel = text_styles.vehicleStatusSimpleText('({})'.format(nonHistoricItemsCount))
        seasonName = SEASON_TYPE_TO_NAME[self.__ctx.season]
        seasonImage = R.images.gui.maps.icons.customization.items_popover.dyn('{}_back_list'.format(seasonName))
        seasonImage = backport.image(seasonImage())
        seasonLabel = R.strings.vehicle_customization.customization.infotype.mapType.dyn(seasonName)
        seasonLabel = backport.text(seasonLabel())
        title = R.strings.vehicle_customization.customization.itemsPopover.title.items
        title = text_styles.highTitle(backport.text(title(), mapType=seasonLabel))
        if self.__isNonHistoric and nonHistoricItemsCount == 0:
            isClear = True
            clearMessage = R.strings.vehicle_customization.customization.itemsPopover.clear.nonHistoricMassage
            clearMessage = backport.text(clearMessage())
        elif isOutfitVisuallyEmpty(outfit):
            isClear = True
            clearMessage = R.strings.vehicle_customization.customization.itemsPopover.clear.message
            clearMessage = backport.text(clearMessage())
        else:
            isClear = False
            clearMessage = ''
        self.as_showClearMessageS(isClear, text_styles.main(clearMessage))
        headerVO = {'title': title,
         'checkBoxText': checkBoxLabel,
         'counterText': counterLabel,
         'currentSeasonImage': seasonImage}
        self.as_setHeaderDataS(headerVO)

    def __update(self, *_):
        self._assignedDP.rebuildList()
        self.__setHeader()


class CustomPopoverDataProvider(SortableDAAPIDataProvider):
    __service = dependency.descriptor(ICustomizationService)

    def __init__(self, isNonHistoric):
        super(CustomPopoverDataProvider, self).__init__()
        self._list = []
        self.__ctx = self.__service.getCtx()
        self.__isNonHistoric = isNonHistoric

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

    def setNonHistoric(self, isNonHistoric):
        self.__isNonHistoric = isNonHistoric

    def buildList(self):
        self.clear()
        modifiedItemsData = self.__getModifiedItemsData()
        originalItemsData = self.__getOriginalItemsData()
        showGroupTitle = bool(modifiedItemsData and originalItemsData)
        if showGroupTitle:
            self._list.append(self.__makeItemsGroupVO(isModified=True))
        for itemData in modifiedItemsData:
            self._list.append(self.__makeItemDataVO(itemData, isModified=True))

        if showGroupTitle:
            self._list.append(self.__makeItemsGroupVO(isModified=False))
        for itemData in originalItemsData:
            self._list.append(self.__makeItemDataVO(itemData, isModified=False))

    def rebuildList(self):
        self.buildList()
        self.refresh()

    def __getModifiedItemsData(self):
        itemData = {}
        purchaseItems = self.__ctx.mode.getPurchaseItems()
        purchaseItems = ifilter(lambda i: i.group == self.__ctx.season, purchaseItems)
        modifiedOutfit = self.__ctx.mode.getModifiedOutfit()
        originalOutfit = self.__ctx.mode.getOriginalOutfit()
        for pItem in purchaseItems:
            if self.__isNonHistoric and pItem.item.isHistorical():
                continue
            slotId = C11nId(pItem.areaID, pItem.slotType, pItem.regionIdx)
            modifiedSlotData = getSlotDataFromSlot(modifiedOutfit, slotId)
            originalSlotData = getSlotDataFromSlot(originalOutfit, slotId)
            if modifiedSlotData is None or originalSlotData is None or modifiedSlotData.isEqual(originalSlotData):
                continue
            key = (pItem.item.intCD, pItem.isFromInventory)
            if key not in itemData:
                itemData[key] = C11nPopoverItemData(item=pItem.item, isFromInventory=pItem.isFromInventory)
            itemData[key].slotsIds.append(slotId._asdict())

        itemBlocks = sorted(itemData.values(), key=orderKey)
        return itemBlocks

    def __getOriginalItemsData(self):
        itemData = {}
        notModifiedOutfit = self.__ctx.mode.getNotModifiedItems()
        for intCD, _, regionIdx, container, _ in notModifiedOutfit.itemsFull():
            item = self.__service.getItemByCD(intCD)
            if item.isHiddenInUI():
                continue
            if self.__isNonHistoric and item.isHistorical():
                continue
            areaId = container.getAreaID()
            slotType = ITEM_TYPE_TO_SLOT_TYPE[item.itemTypeID]
            slotId = C11nId(areaId, slotType, regionIdx)
            if intCD not in itemData:
                itemData[intCD] = C11nPopoverItemData(item=item, isFromInventory=True)
            itemData[intCD].slotsIds.append(slotId._asdict())

        itemBlocks = sorted(itemData.values(), key=orderKey)
        return itemBlocks

    @staticmethod
    def __makeItemDataVO(itemData, isModified):
        item = itemData.item
        progressionLevel = item.getLatestOpenedProgressionLevel(g_currentVehicle.item)
        icon = item.icon if progressionLevel == -1 else item.iconByProgressionLevel(progressionLevel)
        name = text_styles.main(item.userName)
        if isModified and not itemData.isFromInventory:
            countLabel = text_styles.main('{} x '.format(len(itemData.slotsIds)))
            price = getItemPricesVO(item.buyPrices.itemPrice)[0]
        else:
            countLabel = text_styles.main('{} '.format(len(itemData.slotsIds)))
            price = None
        isApplied = not isModified
        itemDataVO = {'id': item.intCD,
         'icon': icon,
         'userName': name,
         'numItems': countLabel,
         'isHistoric': item.isHistorical(),
         'price': price,
         'isApplied': isApplied,
         'isWide': item.isWide(),
         'itemsList': itemData.slotsIds,
         'isDim': item.isDim()}
        return itemDataVO

    @staticmethod
    def __makeItemsGroupVO(isModified):
        if isModified:
            name = R.strings.vehicle_customization.customization.nonHistoric.tableHeaders.modified
        else:
            name = R.strings.vehicle_customization.customization.nonHistoric.tableHeaders.original
        name = text_styles.main(backport.text(name()))
        itemsGroupVO = {'userName': name,
         'isTitle': True}
        return itemsGroupVO
