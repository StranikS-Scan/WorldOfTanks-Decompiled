# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_bottom_panel.py
from collections import namedtuple
from CurrentVehicle import g_currentVehicle
from gui.customization.shared import C11nId
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.customization.customization_carousel import CustomizationCarouselDataProvider, comparisonKey
from gui.Scaleform.daapi.view.lobby.customization.customization_item_vo import buildCustomizationItemDataVO
from gui.Scaleform.daapi.view.lobby.customization.shared import C11nMode, TABS_SLOT_TYPE_MAPPING, TABS_ITEM_TYPE_MAPPING, C11nTabs, getTotalPurchaseInfo
from gui.Scaleform.daapi.view.meta.CustomizationBottomPanelMeta import CustomizationBottomPanelMeta
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.shared.formatters import text_styles, icons, getItemPricesVO, getMoneyVO
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from gui.shared.money import Money
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.graphics import isRendererPipelineDeferred
from helpers import dependency
from helpers.i18n import makeString as _ms
from items.components.c11n_constants import SeasonType
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.daapi.view.lobby.customization.shared import SEASON_TYPE_TO_NAME
CustomizationCarouselDataVO = namedtuple('CustomizationCarouselDataVO', ('displayString', 'isZeroCount', 'shouldShow', 'itemLayoutSize', 'bookmarks'))

class CustomizationBottomPanel(CustomizationBottomPanelMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    service = dependency.descriptor(ICustomizationService)

    def __init__(self):
        super(CustomizationBottomPanel, self).__init__()
        self.__ctx = None
        self._carouselDP = None
        self._currentParentSlot = None
        self._propertySheetShow = False
        return

    def _populate(self):
        super(CustomizationBottomPanel, self)._populate()
        self.__ctx = self.service.getCtx()
        self._carouselDP = CustomizationCarouselDataProvider(g_currentVehicle, self._carouseItemWrapper, self.__ctx)
        self._carouselDP.setFlashObject(self.getDp())
        self._carouselDP.setEnvironment(self.app)
        self.__ctx.onCarouselFilter += self.__onCarouselFilter
        self.__ctx.onCacheResync += self.__onCacheResync
        self.__ctx.onCustomizationSeasonChanged += self.__onSeasonChanged
        self.__ctx.onCustomizationItemInstalled += self.__onItemsInstalled
        self.__ctx.onCustomizationTabChanged += self.__onTabChanged
        self.__ctx.onCustomizationTabsUpdated += self.__onTabsUpdated
        self.__ctx.onCustomizationItemsRemoved += self.__onItemsRemoved
        self.__ctx.onCustomizationModeChanged += self.__onModeChanged
        self.__ctx.onChangesCanceled += self.__onChangesCanceled
        self.__ctx.onCustomizationItemSold += self.__onItemSold
        self.__ctx.onCustomizationItemDataChanged += self.__onItemDataChanged
        self.__ctx.onNextCarouselItemInstalled += self.__onNextCarouselItemInstalled
        self.__ctx.onResetC11nItemsNovelty += self.__onResetC11nItemsNovelty
        self.__ctx.onSlotSelected += self.__onSlotSelected
        self.__ctx.onSlotUnselected += self.__onSlotUnselected
        self.__ctx.onFilterPopoverClosed += self.__onFilterPopoverClosed
        self.__ctx.onPropertySheetShown += self.onPropertySheetShown
        self.__ctx.onPropertySheetHidden += self.onPropertySheetHidden
        g_currentVehicle.onChanged += self.__onVehicleChanged
        g_clientUpdateManager.addMoneyCallback(self.__setBottomPanelBillData)
        self.__updateTabs(self.__ctx.currentTab)
        self.__setFooterInitData()
        self.__setBottomPanelBillData()
        self.__updatePopoverBtnIcon()

    def _dispose(self):
        super(CustomizationBottomPanel, self)._dispose()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__ctx.onCustomizationItemDataChanged -= self.__onItemDataChanged
        self.__ctx.onCustomizationItemSold -= self.__onItemSold
        self.__ctx.onChangesCanceled -= self.__onChangesCanceled
        self.__ctx.onCustomizationModeChanged -= self.__onModeChanged
        self.__ctx.onCustomizationItemsRemoved -= self.__onItemsRemoved
        self.__ctx.onCustomizationTabChanged -= self.__onTabChanged
        self.__ctx.onCustomizationTabsUpdated -= self.__onTabsUpdated
        self.__ctx.onCustomizationItemInstalled -= self.__onItemsInstalled
        self.__ctx.onCustomizationSeasonChanged -= self.__onSeasonChanged
        self.__ctx.onCacheResync -= self.__onCacheResync
        self.__ctx.onCarouselFilter -= self.__onCarouselFilter
        self.__ctx.onNextCarouselItemInstalled -= self.__onNextCarouselItemInstalled
        self.__ctx.onResetC11nItemsNovelty -= self.__onResetC11nItemsNovelty
        self.__ctx.onSlotSelected -= self.__onSlotSelected
        self.__ctx.onSlotUnselected -= self.__onSlotUnselected
        self.__ctx.onFilterPopoverClosed -= self.__onFilterPopoverClosed
        self.__ctx.onPropertySheetShown -= self.onPropertySheetShown
        self.__ctx.onPropertySheetHidden -= self.onPropertySheetHidden
        g_currentVehicle.onChanged -= self.__onVehicleChanged
        self._carouselDP = None
        self.__ctx = None
        return

    def getDp(self):
        return self.as_getDataProviderS()

    def switchToStyle(self):
        self.__ctx.switchToStyle()
        self.__updatePopoverBtnIcon()

    def switchToCustom(self):
        self.__ctx.switchToCustom()
        self.__updatePopoverBtnIcon()

    def onSelectHotFilter(self, index, value):
        (self._carouselDP.setOwnedFilter, self._carouselDP.setAppliedFilter)[index](value)
        self.__refreshCarousel(rebuild=False, force=True)

    def showGroupFromTab(self, tabIndex):
        self.__ctx.tabChanged(tabIndex)

    def onSelectItem(self, index, intCD):
        self._carouselDP.selectItemIdx(index)
        self.__ctx.caruselItemSelected(index, intCD)

    def blinkCounter(self):
        self.as_playFilterBlinkS()

    def __onNextCarouselItemInstalled(self, index):
        self._carouselDP.selectItemIdx(index)

    def __onResetC11nItemsNovelty(self):
        self.__setNotificationCounters()

    def __onSlotSelected(self, areaId, slotType, regionIdx):
        anchorId = C11nId(areaId, slotType, regionIdx)
        slotId = self.__ctx.getSlotIdByAnchorId(anchorId)
        itemIdx = -1
        if slotId is not None:
            item = self.__ctx.getItemFromRegion(slotId)
            if item is not None and item.intCD in self._carouselDP.collection:
                itemIdx = self._carouselDP.collection.index(item.intCD)
        slot = g_currentVehicle.item.getAnchorBySlotId(slotType, areaId, regionIdx)
        if slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
            parent = slot if slot.isParent else g_currentVehicle.item.getAnchorById(slot.parentSlotId)
            self._currentParentSlot = parent
        self._carouselDP.selectItemIdx(itemIdx)
        return

    def __onSlotUnselected(self):
        self._currentParentSlot = None
        self._carouselDP.refresh()
        return

    def __setNotificationCounters(self):
        vehicle = g_currentVehicle.item
        proxy = g_currentVehicle.itemsCache.items
        tabsCounters = []
        for tabIdx in self.__ctx.visibleTabs:
            tabsCounters.append(vehicle.getC11nItemsNoveltyCounter(proxy, itemTypes=TABS_ITEM_TYPE_MAPPING[tabIdx], season=self.__ctx.currentSeason))

        if self.__ctx.mode == C11nMode.STYLE:
            itemTypes = GUI_ITEM_TYPE.CUSTOMIZATIONS_WITHOUT_STYLE
        else:
            itemTypes = (GUI_ITEM_TYPE.STYLE,)
        self.as_setNotificationCountersS({'tabsCounters': tabsCounters,
         'switchersCounter': vehicle.getC11nItemsNoveltyCounter(proxy, itemTypes=itemTypes)})

    def resetFilter(self):
        self.__clearFilter()
        self.refreshFilterData()
        self.__refreshHotFilters()
        self.__refreshCarousel(rebuild=False, force=True)

    def refreshFilterData(self):
        self.as_setFilterDataS(self._carouselDP.getFilterData())

    @property
    def carouselItems(self):
        return self._carouselDP.collection

    def __updateTabs(self, selectedTab=-1):
        tabsDP, pluses = self.__getItemTabsData()
        self.as_setBottomPanelTabsDataS({'tabsDP': tabsDP,
         'selectedTab': selectedTab})
        self.as_setBottomPanelTabsPlusesS(pluses)

    def __setFooterInitData(self):
        self.as_setBottomPanelInitDataS({'tabsAvailableRegions': C11nTabs.AVAILABLE_REGIONS,
         'defaultStyleLabel': VEHICLE_CUSTOMIZATION.DEFAULTSTYLE_LABEL,
         'carouselInitData': self.__getCarouselInitData(),
         'filtersVO': {'popoverAlias': VIEW_ALIAS.CUSTOMIZATION_FILTER_POPOVER,
                       'mainBtn': {'value': RES_ICONS.MAPS_ICONS_BUTTONS_FILTER,
                                   'tooltip': VEHICLE_CUSTOMIZATION.CAROUSEL_FILTER_MAINBTN},
                       'hotFilters': [{'value': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_STORAGE_ICON,
                                       'tooltip': VEHICLE_CUSTOMIZATION.CAROUSEL_FILTER_STORAGEBTN,
                                       'selected': self._carouselDP.getOwnedFilter()}, {'value': RES_ICONS.MAPS_ICONS_BUTTONS_EQUIPPED_ICON,
                                       'tooltip': VEHICLE_CUSTOMIZATION.CAROUSEL_FILTER_EQUIPPEDBTN,
                                       'selected': self._carouselDP.getAppliedFilter()}]}})
        self.__updateSetSwitcherData()
        self.__setNotificationCounters()

    def __updateSetSwitcherData(self):
        self.as_setSwitchersDataS(self.__getSwitcherInitData(self.__ctx.mode, self.__ctx.stylesTabEnabled))

    @staticmethod
    def __getCarouselInitData():
        return {'message': '{}{}\n{}'.format(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ATTENTIONICONFILLED, vSpace=-3), text_styles.neutral(VEHICLE_CUSTOMIZATION.CAROUSEL_MESSAGE_HEADER), text_styles.main(VEHICLE_CUSTOMIZATION.CAROUSEL_MESSAGE_DESCRIPTION))}

    @staticmethod
    def __getSwitcherInitData(mode, rightEnabled):
        data = {'leftLabel': VEHICLE_CUSTOMIZATION.SWITCHER_NAME_CUSTSOMSTYLE,
         'rightLabel': VEHICLE_CUSTOMIZATION.SWITCHER_NAME_DEFAULTSTYLE,
         'leftEvent': 'installStyle',
         'rightEvent': 'installStyles',
         'isLeft': mode == C11nMode.CUSTOM,
         'rightEnabled': rightEnabled}
        return data

    def __buildCustomizationCarouselDataVO(self):
        isZeroCount = self._carouselDP.itemCount == 0
        countStyle = text_styles.error if isZeroCount else text_styles.main
        displayString = text_styles.main('{} / {}'.format(countStyle(str(self._carouselDP.itemCount)), str(self._carouselDP.totalItemCount)))
        shouldShow = self._carouselDP.hasAppliedFilter()
        return CustomizationCarouselDataVO(displayString, isZeroCount, shouldShow, itemLayoutSize=self._carouselDP.getItemSizeData(), bookmarks=self._carouselDP.getBookmarkData())._asdict()

    def __setBottomPanelBillData(self, *_):
        purchaseItems = self.__ctx.getPurchaseItems()
        cartInfo = getTotalPurchaseInfo(purchaseItems)
        totalPriceVO = getItemPricesVO(cartInfo.totalPrice)
        if cartInfo.totalPrice != ITEM_PRICE_EMPTY:
            label = _ms(VEHICLE_CUSTOMIZATION.COMMIT_BUY)
        else:
            label = _ms(VEHICLE_CUSTOMIZATION.COMMIT_APPLY)
        tooltip = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_BUYDISABLED_BODY
        fromStorageCount = 0
        toByeCount = 0
        for item in purchaseItems:
            if item.isFromInventory:
                fromStorageCount += 1
            if not item.isDismantling:
                toByeCount += 1

        if fromStorageCount > 0 or toByeCount > 0:
            self.__showBill()
        else:
            self.__hideBill()
            tooltip = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_NOTSELECTEDITEMS
        fromStorageCount = text_styles.stats('({})'.format(fromStorageCount))
        toByeCount = text_styles.stats('({})'.format(toByeCount))
        outfitsModified = self.__ctx.isOutfitsModified()
        self.as_setBottomPanelPriceStateS({'buyBtnEnabled': outfitsModified,
         'buyBtnLabel': label,
         'buyBtnTooltip': tooltip,
         'isHistoric': self.__ctx.currentOutfit.isHistorical(),
         'billVO': {'title': text_styles.highlightText(_ms(VEHICLE_CUSTOMIZATION.BUYPOPOVER_RESULT)),
                    'priceLbl': text_styles.main('{} {}'.format(_ms(VEHICLE_CUSTOMIZATION.BUYPOPOVER_PRICE), toByeCount)),
                    'fromStorageLbl': text_styles.main('{} {}'.format(_ms(VEHICLE_CUSTOMIZATION.BUYPOPOVER_FROMSTORAGE), fromStorageCount)),
                    'isEnoughStatuses': getMoneyVO(Money(True, True, True)),
                    'pricePanel': totalPriceVO[0]}})
        itemsPopoverBtnEnabled = True
        if self.__ctx.currentOutfit.isEmpty():
            itemsPopoverBtnEnabled = False
        self.as_setItemsPopoverBtnEnabledS(itemsPopoverBtnEnabled)

    def __showBill(self):
        self.as_showBillS()

    def __hideBill(self):
        self.as_hideBillS()

    def __refreshHotFilters(self):
        self.as_setCarouselFiltersDataS({'hotFilters': [self._carouselDP.getOwnedFilter(), self._carouselDP.getAppliedFilter()]})

    def __clearFilter(self):
        self._carouselDP.clearFilter()

    def __refreshCarousel(self, rebuild=False, force=False):
        if rebuild or force or self._carouselDP.getAppliedFilter() or self._carouselDP.getOwnedFilter():
            if rebuild:
                self._carouselDP.buildList(self.__ctx.currentTab, self.__ctx.currentSeason, refresh=False)
            else:
                self._carouselDP.updateList(refresh=False)
            self.as_setCarouselDataS(self.__buildCustomizationCarouselDataVO())
        self._carouselDP.refresh()

    def _carouseItemWrapper(self, itemCD):
        item = self.service.getItemByCD(itemCD)
        itemInventoryCount = self.__ctx.getItemInventoryCount(item)
        purchaseLimit = self.__ctx.getPurchaseLimit(item)
        if item.itemTypeID == GUI_ITEM_TYPE.MODIFICATION:
            showUnsupportedAlert = not isRendererPipelineDeferred()
        else:
            showUnsupportedAlert = False
        isCurrentlyApplied = itemCD in self._carouselDP.getCurrentlyApplied()
        noPrice = item.buyCount <= 0
        isDarked = purchaseLimit == 0 and itemInventoryCount == 0
        isAlreadyUsed = isDarked and not isCurrentlyApplied
        forceLocked = isAlreadyUsed
        isUnsupportedForm = False
        autoRentEnabled = self.__ctx.autoRentEnabled()
        if item.itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL and self._currentParentSlot is not None and (not self.__ctx.isSlotFilled(self.__ctx.selectedAnchor) or self._propertySheetShow):
            isUnsupportedForm = item.formfactor in self._currentParentSlot.getUnsupportedForms(g_currentVehicle.item)
            forceLocked = forceLocked or isUnsupportedForm
        return buildCustomizationItemDataVO(item, itemInventoryCount, showUnsupportedAlert=showUnsupportedAlert, isCurrentlyApplied=isCurrentlyApplied, isAlreadyUsed=isAlreadyUsed, forceLocked=forceLocked, isDarked=isDarked, noPrice=noPrice, autoRentEnabled=autoRentEnabled, vehicle=g_currentVehicle.item, isUnsupportedForm=isUnsupportedForm)

    def __getItemTabsData(self):
        data = []
        pluses = []
        for tabIdx in self.__ctx.visibleTabs:
            itemTypeID = TABS_SLOT_TYPE_MAPPING[tabIdx]
            typeName = GUI_ITEM_TYPE_NAMES[itemTypeID]
            slotsCount, filledSlotsCount = self.__ctx.checkSlotsFilling(itemTypeID, self.__ctx.currentSeason)
            showPlus = filledSlotsCount < slotsCount
            data.append({'label': _ms(ITEM_TYPES.customizationPlural(typeName)),
             'icon': RES_ICONS.getCustomizationIcon(typeName),
             'tooltip': makeTooltip(ITEM_TYPES.customizationPlural(typeName), TOOLTIPS.customizationItemTab(typeName)),
             'id': tabIdx})
            pluses.append(showPlus)

        return (data, pluses)

    def __onCarouselFilter(self, **kwargs):
        if 'group' in kwargs:
            self._carouselDP.setActiveGroupIndex(kwargs['group'])
        if 'historic' in kwargs:
            self._carouselDP.setHistoricalFilter(kwargs['historic'])
        if 'inventory' in kwargs:
            self._carouselDP.setOwnedFilter(kwargs['inventory'])
        if 'applied' in kwargs:
            self._carouselDP.setAppliedFilter(kwargs['applied'])
        if 'formfactorGroups' in kwargs:
            self._carouselDP.setFormfactorGroupsFilter(kwargs['formfactorGroups'])
        self.__refreshCarousel(rebuild=False, force=True)
        self.__refreshHotFilters()

    def __onCacheResync(self, *_):
        if not g_currentVehicle.isPresent():
            return
        self.__updateTabs()
        self.__setBottomPanelBillData()
        self.__refreshCarousel(rebuild=True, force=True)
        self.__setNotificationCounters()

    def __onVehicleChanged(self):
        self.__updateTabs(self.__ctx.currentTab)
        self._carouselDP.updateTabGroups()
        self.resetFilter()
        self.__updatePopoverBtnIcon()
        self.__setBottomPanelBillData()
        self.__setFooterInitData()
        self.__scrollToNewItem()

    def __onSeasonChanged(self, seasonType):
        self.__updateTabs(self.__ctx.currentTab)
        self.__refreshCarousel(rebuild=True, force=True)
        self.__updatePopoverBtnIcon()
        self.__setBottomPanelBillData()
        self.__setNotificationCounters()
        self.__scrollToNewItem()

    def __updatePopoverBtnIcon(self):
        if self.__ctx.currentTab == 0:
            imgSrc = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_ITEMS_POPOVER_DEFAULT_LIST30X16
        else:
            imgSrc = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_ITEMS_POPOVER_DESERT_LIST30X16
            if self.__ctx.currentSeason == SeasonType.WINTER:
                imgSrc = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_ITEMS_POPOVER_WINTER_LIST30X16
            elif self.__ctx.currentSeason == SeasonType.SUMMER:
                imgSrc = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_ITEMS_POPOVER_SUMMER_LIST30X16
        if self.__ctx.mode == C11nMode.STYLE:
            tooltip = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_ITEMSPOPOVER_BTN_STYLE_DISABLED
        else:
            seasonName = SEASON_TYPE_TO_NAME.get(self.service.getCtx().currentSeason)
            mapName = VEHICLE_CUSTOMIZATION.getMapName(seasonName)
            tooltip = _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_ITEMSPOPOVER_BTN_DISABLED, mapType=_ms(mapName))
        self.as_showPopoverBtnIconS(imgSrc, tooltip)

    def __onItemsInstalled(self, *args):
        self.__updateTabs(self.__ctx.currentTab)
        self.__setBottomPanelBillData()
        self.__refreshCarousel(rebuild=False, force=False)

    def __onTabChanged(self, tabIndex):
        self.__refreshCarousel(rebuild=True, force=True)
        self.__updateTabs(self.__ctx.currentTab)
        self.__updateSetSwitcherData()
        self.__setNotificationCounters()
        self.__scrollToNewItem()

    def __onTabsUpdated(self, tabIndex):
        self.__updateTabs(tabIndex)
        self.__refreshCarousel(rebuild=True, force=True)

    def __onItemsRemoved(self):
        self.__updateTabs(self.__ctx.currentTab)
        self.__setBottomPanelBillData()
        self.__refreshCarousel(rebuild=False, force=False)

    def __onModeChanged(self, mode):
        self._carouselDP.selectItem(self.__ctx.modifiedStyle if mode == C11nMode.STYLE else None)
        self.__setBottomPanelBillData()
        self.__setFooterInitData()
        self.__scrollToNewItem()
        return

    def __onChangesCanceled(self):
        self.__updateTabs(self.__ctx.currentTab)
        self.__setBottomPanelBillData()
        self.__refreshCarousel(rebuild=False, force=False)

    def __onItemSold(self, item, count):
        self._needCaruselFullRebuild = self._carouselDP.getOwnedFilter()

    def __onItemDataChanged(self, areaId, slotId, regionIdx, changeAnchor, updatePropertiesSheet, refreshCarousel):
        self.__setBottomPanelBillData()
        if refreshCarousel:
            self.__refreshCarousel(rebuild=False, force=False)

    def __scrollToNewItem(self):
        currentTypes = TABS_ITEM_TYPE_MAPPING[self.__ctx.currentTab]
        newItems = sorted(g_currentVehicle.item.getNewC11nItems(g_currentVehicle.itemsCache.items), key=comparisonKey)
        for item in newItems:
            if item.itemTypeID in currentTypes and item.season & self.__ctx.currentSeason:
                self.as_scrollToSlotS(item.intCD)
                return

    def __onFilterPopoverClosed(self):
        self.blinkCounter()

    def onPropertySheetShown(self):
        self._propertySheetShow = True

    def onPropertySheetHidden(self):
        self._propertySheetShow = False
