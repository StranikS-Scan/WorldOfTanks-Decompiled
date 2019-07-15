# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_bottom_panel.py
from collections import namedtuple
from CurrentVehicle import g_currentVehicle
from gui.customization.shared import SEASON_TYPE_TO_NAME, getTotalPurchaseInfo
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.customization.customization_carousel import CustomizationCarouselDataProvider, comparisonKey
from gui.Scaleform.daapi.view.lobby.customization.customization_item_vo import buildCustomizationItemDataVO
from gui.Scaleform.daapi.view.lobby.customization.shared import C11nMode, TABS_SLOT_TYPE_MAPPING, TABS_ITEM_TYPE_MAPPING, C11nTabs
from gui.Scaleform.daapi.view.meta.CustomizationBottomPanelMeta import CustomizationBottomPanelMeta
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.shared.gui_items.customization.outfit import Area
from gui.shared.formatters import text_styles, icons, getItemPricesVO, getMoneyVO
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from gui.shared.money import Money
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.graphics import isRendererPipelineDeferred
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from helpers.i18n import makeString as _ms
from items.components.c11n_constants import SeasonType
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from account_helpers.AccountSettings import AccountSettings, CUSTOMIZATION_SECTION, PROJECTION_DECAL_ONLY_ONCE_HINT_SHOWN_FIELD
CustomizationCarouselDataVO = namedtuple('CustomizationCarouselDataVO', ('displayString', 'isZeroCount', 'shouldShow', 'itemLayoutSize', 'bookmarks'))

class CustomizationBottomPanel(CustomizationBottomPanelMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    service = dependency.descriptor(ICustomizationService)

    def __init__(self):
        super(CustomizationBottomPanel, self).__init__()
        self.__ctx = None
        self._carouselDP = None
        self._propertySheetShow = False
        self._projectionDecalOnlyOnceHintShow = False
        self._selectedItem = None
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
        self.__ctx.onCaruselItemSelected += self.__onCaruselItemSelected
        self.__ctx.onCaruselItemUnselected += self.__onCaruselItemUnselected
        self.__ctx.onSlotUnselected += self.__onSlotUnselected
        self.__ctx.onFilterPopoverClosed += self.__onFilterPopoverClosed
        self.__ctx.onPropertySheetShown += self.onPropertySheetShown
        self.__ctx.onPropertySheetHidden += self.onPropertySheetHidden
        self.__ctx.onGetItemBackToHand += self.__onGetItemBackToHand
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
        self.__ctx.onCaruselItemSelected -= self.__onCaruselItemSelected
        self.__ctx.onCaruselItemUnselected -= self.__onCaruselItemUnselected
        self.__ctx.onSlotUnselected -= self.__onSlotUnselected
        self.__ctx.onFilterPopoverClosed -= self.__onFilterPopoverClosed
        self.__ctx.onPropertySheetShown -= self.onPropertySheetShown
        self.__ctx.onPropertySheetHidden -= self.onPropertySheetHidden
        self.__ctx.onGetItemBackToHand -= self.__onGetItemBackToHand
        g_currentVehicle.onChanged -= self.__onVehicleChanged
        self._carouselDP = None
        self.__ctx = None
        self._selectedItem = None
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
        self._carouselDP.invalidateFiltered()
        self.__refreshCarousel()

    def showGroupFromTab(self, tabIndex):
        self.__ctx.tabChanged(tabIndex)

    def onSelectItem(self, index, intCD):
        self.__ctx.caruselItemSelected(index, intCD)

    def blinkCounter(self):
        self.as_playFilterBlinkS()

    def __onNextCarouselItemInstalled(self, item):
        self._carouselDP.selectItem(item)
        self.as_scrollToSlotS(item.intCD)

    def __onResetC11nItemsNovelty(self):
        self.__setNotificationCounters()

    def __onSlotUnselected(self):
        self._carouselDP.refresh()

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
        self._carouselDP.invalidateFiltered()
        self.__refreshCarousel()

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
        self.__updateFilterMessage()

    def __updateFilterMessage(self):
        message = backport.text(R.strings.vehicle_customization.carousel.message.description())
        if self._propertySheetShow and self.__ctx.currentTab == C11nTabs.PROJECTION_DECAL:
            message = backport.text(R.strings.vehicle_customization.carousel.message.propertysheet())
        self.as_carouselFilterMessageS('{}{}\n{}'.format(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ATTENTIONICONFILLED, vSpace=-3), text_styles.neutral(VEHICLE_CUSTOMIZATION.CAROUSEL_MESSAGE_HEADER), text_styles.main(message)))

    def __updateSetSwitcherData(self):
        self.as_setSwitchersDataS(self.__getSwitcherInitData(self.__ctx.mode, self.__ctx.stylesTabEnabled))

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
        label = _ms(VEHICLE_CUSTOMIZATION.COMMIT_APPLY)
        tooltip = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_BUYDISABLED_BODY
        fromStorageCount = 0
        toByeCount = 0
        for item in purchaseItems:
            if item.isFromInventory:
                fromStorageCount += 1
            if not item.isDismantling:
                toByeCount += 1

        outfitsModified = self.__ctx.isOutfitsModified()
        if outfitsModified:
            if cartInfo.totalPrice != ITEM_PRICE_EMPTY:
                label = _ms(VEHICLE_CUSTOMIZATION.COMMIT_BUY)
            if fromStorageCount > 0 or toByeCount > 0:
                self.__showBill()
            else:
                self.__hideBill()
                tooltip = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_NOTSELECTEDITEMS
        else:
            self.__hideBill()
        fromStorageCount = text_styles.stats('({})'.format(fromStorageCount))
        toByeCount = text_styles.stats('({})'.format(toByeCount))
        self.as_setBottomPanelPriceStateS({'buyBtnEnabled': outfitsModified,
         'buyBtnLabel': label,
         'buyBtnTooltip': tooltip,
         'isHistoric': self.__ctx.currentOutfit.isHistorical(),
         'billVO': {'title': text_styles.highlightText(_ms(VEHICLE_CUSTOMIZATION.BUYPOPOVER_RESULT)),
                    'priceLbl': text_styles.main('{} {}'.format(_ms(VEHICLE_CUSTOMIZATION.BUYPOPOVER_PRICE), toByeCount)),
                    'fromStorageLbl': text_styles.main('{} {}'.format(_ms(VEHICLE_CUSTOMIZATION.BUYPOPOVER_FROMSTORAGE), fromStorageCount)),
                    'isEnoughStatuses': getMoneyVO(Money(True, True, True)),
                    'pricePanel': totalPriceVO[0]}})
        itemsPopoverBtnEnabled = False
        for item, component in self.__ctx.currentOutfit.itemsFull():
            if component.isFilled():
                itemsPopoverBtnEnabled = True
                break

        self.as_setItemsPopoverBtnEnabledS(itemsPopoverBtnEnabled)

    def __showBill(self):
        self.as_showBillS()

    def __hideBill(self):
        self.as_hideBillS()

    def __refreshHotFilters(self):
        self.as_setCarouselFiltersDataS({'hotFilters': [self._carouselDP.getOwnedFilter(), self._carouselDP.getAppliedFilter()]})

    def __clearFilter(self):
        self._carouselDP.clearFilter()

    def __refreshCarousel(self):
        self._carouselDP.buildList(self.__ctx.currentTab, self.__ctx.currentSeason)
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
        if item.itemTypeID == GUI_ITEM_TYPE.STYLE:
            isApplied = self.__ctx.modifiedStyle == item
        else:
            isApplied = any((self.__ctx.getModifiedOutfit(season).has(item) for season in SeasonType.COMMON_SEASONS))
        noPrice = item.buyCount <= 0
        isDarked = purchaseLimit == 0 and itemInventoryCount == 0
        isAlreadyUsed = isDarked and not isApplied
        forceLocked = isAlreadyUsed
        autoRentEnabled = self.__ctx.autoRentEnabled()
        return buildCustomizationItemDataVO(item, itemInventoryCount, showUnsupportedAlert=showUnsupportedAlert, isCurrentlyApplied=isCurrentlyApplied, isAlreadyUsed=isAlreadyUsed, forceLocked=forceLocked, isDarked=isDarked, noPrice=noPrice, autoRentEnabled=autoRentEnabled, vehicle=g_currentVehicle.item)

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
        self._carouselDP.invalidateFiltered()
        self.__refreshCarousel()
        self.__refreshHotFilters()
        if not self._propertySheetShow:
            self.as_scrollToSlotS(-1, True)

    def __onCacheResync(self, *_):
        if not g_currentVehicle.isPresent():
            return
        self.__updateTabs()
        self.__setBottomPanelBillData()
        self._carouselDP.invalidateCache()
        self.__refreshCarousel()
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
        self.__refreshCarousel()
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

    def __onItemsInstalled(self, item, component, slotId, buyLimitReached):
        self.__updateTabs(self.__ctx.currentTab)
        self.__setBottomPanelBillData()
        if self._propertySheetShow:
            self._carouselDP.selectItem(item)
        self._carouselDP.invalidateFiltered()
        self.__refreshCarousel()

    def __onTabChanged(self, tabIndex):
        self.__updateTabs(self.__ctx.currentTab)
        self.__refreshCarousel()
        if tabIndex == C11nTabs.PROJECTION_DECAL:
            self.__onProjectionDecalOnlyOnceHintShown()
        else:
            self.__onProjectionDecalOnlyOnceHintHidden()
        self.__updateSetSwitcherData()
        self.__setNotificationCounters()
        self.__scrollToNewItem()

    def __onTabsUpdated(self, tabIndex):
        self.__updateTabs(tabIndex)
        self.__refreshCarousel()

    def __onItemsRemoved(self):
        self.__updateTabs(self.__ctx.currentTab)
        self.__setBottomPanelBillData()
        self.__refreshCarousel()

    def __onModeChanged(self, mode):
        self.__setBottomPanelBillData()
        self.__setFooterInitData()
        self.__scrollToNewItem()

    def __onChangesCanceled(self):
        self.__updateTabs(self.__ctx.currentTab)
        self.__setBottomPanelBillData()
        self.__refreshCarousel()

    def __onItemSold(self, item, count):
        self._needCaruselFullRebuild = self._carouselDP.getOwnedFilter()

    def __onItemDataChanged(self, areaId, slotId, regionIdx, refreshCarousel):
        self.__setBottomPanelBillData()
        if refreshCarousel:
            self.__refreshCarousel()

    def __scrollToNewItem(self):
        currentTypes = TABS_ITEM_TYPE_MAPPING[self.__ctx.currentTab]
        newItems = sorted(g_currentVehicle.item.getNewC11nItems(g_currentVehicle.itemsCache.items), key=comparisonKey)
        for item in newItems:
            if item.itemTypeID in currentTypes and item.season & self.__ctx.currentSeason:
                self.as_scrollToSlotS(item.intCD)
                return

    def __onFilterPopoverClosed(self):
        self.blinkCounter()

    def onPropertySheetShown(self, anchorId):
        self._propertySheetShow = True
        slotId = self.__ctx.getSlotIdByAnchorId(anchorId)
        if slotId is not None:
            self._selectedItem = self.__ctx.getItemFromRegion(slotId)
            self._carouselDP.selectItem(self._selectedItem)
        self._carouselDP.invalidateFiltered()
        self.__refreshCarousel()
        self.as_scrollToSlotS(self._selectedItem.intCD, True)
        self.__updateFilterMessage()
        return

    def onPropertySheetHidden(self):
        self._propertySheetShow = False
        self._carouselDP.selectItem(None)
        self._carouselDP.invalidateFiltered()
        self.__refreshCarousel()
        self.as_scrollToSlotS(self._selectedItem.intCD, True)
        self.__updateFilterMessage()
        return

    def __onGetItemBackToHand(self, intCD):
        self.resetFilter()

    def __onCaruselItemSelected(self, index, intCD):
        item = self.service.getItemByCD(intCD) if intCD != -1 else None
        if self._propertySheetShow:
            if item is not None:
                self._carouselDP.selectItem(item)
        else:
            self._carouselDP.selectItem(item)
        if self._projectionDecalOnlyOnceHintShow:
            self.__onProjectionDecalOnlyOnceHintHidden(True)
        return

    def __onCaruselItemUnselected(self, index, intCD):
        self._carouselDP.selectItem(None)
        return

    def __onProjectionDecalOnlyOnceHintShown(self):
        customizationSettings = AccountSettings.getSettings(CUSTOMIZATION_SECTION)
        if not customizationSettings.get(PROJECTION_DECAL_ONLY_ONCE_HINT_SHOWN_FIELD, False):
            if self.__ctx.currentOutfit.getContainer(Area.MISC).slotFor(GUI_ITEM_TYPE.PROJECTION_DECAL).isEmpty():
                self.as_onProjectionDecalOnlyOnceHintShownS()
                self._projectionDecalOnlyOnceHintShow = True

    def __onProjectionDecalOnlyOnceHintHidden(self, record=False):
        customizationSettings = AccountSettings.getSettings(CUSTOMIZATION_SECTION)
        if record:
            customizationSettings[PROJECTION_DECAL_ONLY_ONCE_HINT_SHOWN_FIELD] = True
            AccountSettings.setSettings(CUSTOMIZATION_SECTION, customizationSettings)
        self._projectionDecalOnlyOnceHintShow = False
        self.as_onProjectionDecalOnlyOnceHintHiddenS()
