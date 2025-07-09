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
from gui.customization.shared import SEASONS_ORDER, isOutfitVisuallyEmpty, SEASON_TYPE_TO_NAME, C11nId
from gui.shared.formatters import text_styles, getItemPricesVO
from helpers import dependency
from gui import makeHtmlString
from items.components.c11n_constants import CustomizationDisplayType, SeasonType
from skeletons.gui.customization import ICustomizationService
POPOVER_SEASONS_ORDER = (SeasonType.ALL,) + SEASONS_ORDER

class CustomPopover(CustomizationItemsPopoverMeta):
    __service = dependency.descriptor(ICustomizationService)

    def __init__(self, ctx=None):
        super(CustomPopover, self).__init__(ctx)
        self.__isHistoric = False
        self.__isNonHistoric = False
        self.__isFantastical = False

    def onWindowClose(self):
        self.destroy()

    def remove(self, intCD, slotIds, season):
        self.__ctx.mode.removeFromSlots(slotIds, season)

    def removeAll(self):
        if self.__isHistoric and self.__isNonHistoric and self.__isFantastical:
            filterMethod = lambda item: item.customizationDisplayType() == CustomizationDisplayType.HISTORICAL or item.customizationDisplayType() == CustomizationDisplayType.NON_HISTORICAL or item.customizationDisplayType() == CustomizationDisplayType.FANTASTICAL
        elif self.__isHistoric and self.__isNonHistoric:
            filterMethod = lambda item: item.customizationDisplayType() == CustomizationDisplayType.HISTORICAL or item.customizationDisplayType() == CustomizationDisplayType.NON_HISTORICAL
        elif self.__isHistoric and self.__isFantastical:
            filterMethod = lambda item: item.customizationDisplayType() == CustomizationDisplayType.HISTORICAL or item.customizationDisplayType() == CustomizationDisplayType.FANTASTICAL
        elif self.__isNonHistoric and self.__isFantastical:
            filterMethod = lambda item: item.customizationDisplayType() == CustomizationDisplayType.NON_HISTORICAL or item.customizationDisplayType() == CustomizationDisplayType.FANTASTICAL
        elif self.__isHistoric:
            filterMethod = lambda item: item.customizationDisplayType() == CustomizationDisplayType.HISTORICAL
        elif self.__isNonHistoric:
            filterMethod = lambda item: item.customizationDisplayType() == CustomizationDisplayType.NON_HISTORICAL
        elif self.__isFantastical:
            filterMethod = lambda item: item.customizationDisplayType() == CustomizationDisplayType.FANTASTICAL
        else:
            filterMethod = None
        for season in SeasonType.REGULAR:
            self.__ctx.mode.removeItemsFromSeason(season=season, filterMethod=filterMethod)

        return

    def onFilterChanged(self, showHistoric, showNonHistoric, showFantastical):
        self.__isHistoric = showHistoric
        self.__isNonHistoric = showNonHistoric
        self.__isFantastical = showFantastical
        self._assignedDP.setHistoric(self.__isHistoric)
        self._assignedDP.setNonHistoric(self.__isNonHistoric)
        self._assignedDP.setFantastical(self.__isFantastical)
        self.__update()

    def _populate(self):
        super(CustomPopover, self)._populate()
        self.__ctx = self.__service.getCtx()
        self.__ctx.events.onCacheResync += self.__update
        self.__ctx.events.onSeasonChanged += self.__update
        self.__ctx.events.onItemInstalled += self.__update
        self.__ctx.events.onItemsRemoved += self.__update
        self.__ctx.events.onChangesCanceled += self.__update
        self._assignedDP = CustomPopoverDataProvider(self.__isHistoric, self.__isNonHistoric, self.__isFantastical)
        self._assignedDP.setFlashObject(self.as_getDPS())
        self.__update()

    def _dispose(self):
        if self.__ctx.events is not None:
            self.__ctx.events.onChangesCanceled -= self.__update
            self.__ctx.events.onItemsRemoved -= self.__update
            self.__ctx.events.onItemInstalled -= self.__update
            self.__ctx.events.onSeasonChanged -= self.__update
            self.__ctx.events.onCacheResync -= self.__update
        self._assignedDP.fini()
        self._assignedDP = None
        self.__ctx = None
        super(CustomPopover, self)._dispose()
        return

    def __setHeader(self):
        historicItemsCount = 0
        nonHistoricItemsCount = 0
        fantasticalItemsCount = 0
        allOutfitsEmpty = True
        for outfit in self.__ctx.mode.getModifiedOutfits().values() + [self.__ctx.commonModifiedOutfit]:
            historicItems = [ intCD for intCD in outfit.items() if self.__service.getItemByCD(intCD).customizationDisplayType() == CustomizationDisplayType.HISTORICAL ]
            historicItemsCount += len(historicItems)
            nonHistoricItems = [ intCD for intCD in outfit.items() if self.__service.getItemByCD(intCD).customizationDisplayType() == CustomizationDisplayType.NON_HISTORICAL ]
            nonHistoricItemsCount += len(nonHistoricItems)
            fantasticalItems = [ intCD for intCD in outfit.items() if self.__service.getItemByCD(intCD).customizationDisplayType() == CustomizationDisplayType.FANTASTICAL ]
            fantasticalItemsCount += len(fantasticalItems)
            if not isOutfitVisuallyEmpty(outfit):
                allOutfitsEmpty = False

        title = backport.text(R.strings.vehicle_customization.customization.kitPopover.title.summary())
        if allOutfitsEmpty:
            isClear = True
            clearMessage = R.strings.vehicle_customization.customization.itemsPopover.message.clear
            clearMessage = backport.text(clearMessage())
        elif self.__isHistoric or self.__isNonHistoric or self.__isFantastical:
            itemsCount = 0
            if self.__isHistoric:
                itemsCount += historicItemsCount
            if self.__isNonHistoric:
                itemsCount += nonHistoricItemsCount
            if self.__isFantastical:
                itemsCount += fantasticalItemsCount
            if itemsCount == 0:
                isClear = True
                clearMessage = R.strings.vehicle_customization.customization.itemsPopover.message.clearFiltered
                clearMessage = backport.text(clearMessage())
            else:
                isClear = False
                clearMessage = ''
        else:
            isClear = False
            clearMessage = ''
        self.as_showClearMessageS(isClear, text_styles.main(clearMessage))
        headerVO = {'title': title}
        self.as_setHeaderDataS(headerVO)

    def __update(self, *_):
        self._assignedDP.rebuildList()
        self.__setHeader()


class CustomPopoverDataProvider(SortableDAAPIDataProvider):
    __service = dependency.descriptor(ICustomizationService)

    def __init__(self, isHistoric, isNonHistoric, isFantastical):
        super(CustomPopoverDataProvider, self).__init__()
        self._list = []
        self.__ctx = self.__service.getCtx()
        self.__isHistoric = isHistoric
        self.__isNonHistoric = isNonHistoric
        self.__isFantastical = isFantastical

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
        self.destroy()
        return

    def setHistoric(self, isHistoric):
        self.__isHistoric = isHistoric

    def setNonHistoric(self, isNonHistoric):
        self.__isNonHistoric = isNonHistoric

    def setFantastical(self, isFantastical):
        self.__isFantastical = isFantastical

    def buildList(self):
        self.clear()
        for season in POPOVER_SEASONS_ORDER:
            modifiedItemsData = self.__getModifiedItemsData(season)
            originalItemsData = self.__getOriginalItemsData(season)
            if modifiedItemsData or originalItemsData:
                self._list.append(self.__getSeasonGroupVO(season))
                for modifiedItemData in modifiedItemsData:
                    self._list.append(self.__makeItemDataVO(modifiedItemData, isModified=True))

                for originalItemData in originalItemsData:
                    self._list.append(self.__makeItemDataVO(originalItemData, isModified=False))

    def rebuildList(self):
        self.buildList()
        self.refresh()

    def __getModifiedItemsData(self, season=None):
        itemData = {}
        purchaseItems = self.__ctx.getPurchaseItems()
        season = season or self.__ctx.season
        purchaseItems = ifilter(lambda i: i.group == season, purchaseItems)
        if season == SeasonType.ALL:
            modifiedOutfit = self.__ctx.commonModifiedOutfit
            originalOutfit = self.__ctx.commonOriginalOutfit
        else:
            modifiedOutfit = self.__ctx.mode.getModifiedOutfit(season)
            originalOutfit = self.__ctx.mode.getOriginalOutfit(season)
        for pItem in purchaseItems:
            if self.isSkipItem(pItem.item):
                continue
            slotId = C11nId(pItem.areaID, pItem.slotType, pItem.regionIdx)
            modifiedSlotData = getSlotDataFromSlot(modifiedOutfit, slotId)
            originalSlotData = getSlotDataFromSlot(originalOutfit, slotId)
            if modifiedSlotData is None or originalSlotData is None or modifiedSlotData.isEqual(originalSlotData):
                continue
            key = (pItem.item.intCD, pItem.isFromInventory)
            if key not in itemData:
                itemData[key] = C11nPopoverItemData(item=pItem.item, season=season, isFromInventory=pItem.isFromInventory)
            itemData[key].slotsIds.append(slotId._asdict())

        itemBlocks = sorted(itemData.values(), key=orderKey)
        return itemBlocks

    def __getOriginalItemsData(self, season):
        itemData = {}
        notModifiedItems = self.__getNotModifiedItems(season)
        for intCD, regionIdx, container in notModifiedItems:
            item = self.__service.getItemByCD(intCD)
            if item.isHiddenInUI():
                continue
            if self.isSkipItem(item):
                continue
            areaId = container.getAreaID()
            slotType = ITEM_TYPE_TO_SLOT_TYPE[item.itemTypeID]
            slotId = C11nId(areaId, slotType, regionIdx)
            if intCD not in itemData:
                itemData[intCD] = C11nPopoverItemData(item=item, season=season, isFromInventory=True)
            itemData[intCD].slotsIds.append(slotId._asdict())

        itemBlocks = sorted(itemData.values(), key=orderKey)
        return itemBlocks

    def isSkipItem(self, item):
        itemCustomizationDisplayType = item.customizationDisplayType()
        if self.__isHistoric and self.__isNonHistoric and self.__isFantastical:
            return False
        if self.__isHistoric and self.__isNonHistoric and itemCustomizationDisplayType == CustomizationDisplayType.FANTASTICAL:
            return True
        if self.__isHistoric and self.__isFantastical and itemCustomizationDisplayType == CustomizationDisplayType.NON_HISTORICAL:
            return True
        if self.__isNonHistoric and self.__isFantastical and itemCustomizationDisplayType == CustomizationDisplayType.HISTORICAL:
            return True
        if self.__isHistoric and not self.__isNonHistoric and not self.__isFantastical and itemCustomizationDisplayType != CustomizationDisplayType.HISTORICAL:
            return True
        if not self.__isHistoric and self.__isNonHistoric and not self.__isFantastical and itemCustomizationDisplayType != CustomizationDisplayType.NON_HISTORICAL:
            return True
        return True if not self.__isHistoric and not self.__isNonHistoric and self.__isFantastical and itemCustomizationDisplayType != CustomizationDisplayType.FANTASTICAL else False

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
        rarity = item.rarity
        isRare = bool(rarity)
        rarityIconSource = ''
        rarityBackgroundIconSource = ''
        if isRare:
            rarityIconSource = backport.image(R.images.gui.maps.icons.customization.rarity.sign.s20x20.dyn(rarity)())
            rarityBackgroundIconSource = backport.image(R.images.gui.maps.icons.customization.rarity.glow.s104x104.dyn(rarity)())
        itemDataVO = {'id': item.intCD,
         'icon': icon,
         'userName': name,
         'numItems': countLabel,
         'customizationDisplayType': item.customizationDisplayType(),
         'price': price,
         'isApplied': isApplied,
         'isWide': item.isWide(),
         'itemsList': itemData.slotsIds,
         'seasonType': itemData.season,
         'isDim': item.isDim(),
         'rarityIcon': rarityIconSource,
         'rarityBackground': rarityBackgroundIconSource}
        return itemDataVO

    @staticmethod
    def __getSeasonGroupVO(season):
        seasonName = SEASON_TYPE_TO_NAME[season]
        seasonTitle = makeHtmlString('html_templates:lobby/customization/StylePopoverSeasonName', seasonName, ctx={'align': 'CENTER'})
        seasonGroupVO = {'titleLabel': seasonTitle,
         'isTitle': True}
        return seasonGroupVO

    def __getNotModifiedItems(self, season):
        if season != SeasonType.ALL:
            notModifiedOutfit = self.__ctx.mode.getNotModifiedItems(season)
            return [ (intCD, regionIdx, container) for intCD, _, regionIdx, container, _ in notModifiedOutfit.itemsFull() ]
        notModifiedCommonOutfit = self.__ctx.getNotModifedCommonItems()
        return [ (intCD, region, container) for intCD, _, region, container, _ in notModifiedCommonOutfit.itemsFull() ]
