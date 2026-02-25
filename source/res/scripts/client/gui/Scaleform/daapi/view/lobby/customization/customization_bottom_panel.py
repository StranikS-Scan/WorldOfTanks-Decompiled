# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_bottom_panel.py
from collections import namedtuple, OrderedDict
import typing
import BigWorld
from CurrentVehicle import g_currentVehicle
from account_helpers.AccountSettings import AccountSettings, CUSTOMIZATION_SECTION, CustomizationFilter, PROJECTION_DECAL_HINT_SHOWN_FIELD, CUSTOMIZATION_STYLE_ITEMS_VISITED
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.customization.customization_carousel import CustomizationCarouselDataProvider, comparisonKey, FilterTypes, FilterAliases
from gui.Scaleform.daapi.view.lobby.customization.customization_item_vo import buildCustomizationItemDataVO
from gui.Scaleform.daapi.view.lobby.customization.shared import checkSlotsFilling, isItemUsedUp, getTabGroupId, CustomizationTabs, getMultiSlot, BillPopoverButtons
from gui.Scaleform.daapi.view.meta.CustomizationBottomPanelMeta import CustomizationBottomPanelMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.customization.constants import CustomizationModes, CustomizationModeSource
from gui.customization.shared import SEASON_TYPE_TO_NAME, getTotalPurchaseInfo, isVehicleCanBeCustomized, C11nId
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles, icons, getItemPricesVO, getMoneyVO
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from gui.shared.gui_items.customization.c11n_items import Style
from gui.shared.money import Money
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from helpers.i18n import makeString as _ms
from items.components.c11n_constants import SeasonType
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from tutorial.hints_manager import HINT_SHOWN_STATUS
from vehicle_outfit.outfit import Area

class CarouselFilterTypes(object):
    GROUP = 'group'
    DISPLAY_GROUP = 'displayGroup'
    HISTORIC = 'historic'
    NON_HISTORIC = 'nonHistoric'
    FANTASTICAL = 'fantastical'
    INVENTORY = 'inventory'
    APPLIED = 'applied'
    FAVORITE = 'favorite'
    FORMFACTOR_GROUPS = 'formfactorGroups'
    ON_ANOTHER_VEH = 'onAnotherVeh'
    ONLY_PROGRESSION_DECALS = 'onlyProgressionDecals'
    ONLY_EDITABLE_STYLES = 'onlyEditableStyles'
    ONLY_NON_EDITABLE_STYLES = 'onlyNonEditableStyles'
    ONLY_PROGRESSION_STYLES = 'onlyProgressionStyles'
    VO_TYPE_TO_FILTER = {'purchasedEnabled': INVENTORY,
     'historicEnabled': HISTORIC,
     'nonHistoricEnabled': NON_HISTORIC,
     'fantasticalEnabled': FANTASTICAL,
     'appliedEnabled': APPLIED,
     'favoriteEnabled': FAVORITE,
     'hideOnAnotherVehEnabled': ON_ANOTHER_VEH,
     'showOnlyProgressionDecalsEnabled': ONLY_PROGRESSION_DECALS,
     'showOnlyEditableStylesEnabled': ONLY_EDITABLE_STYLES,
     'showOnlyNonEditableStylesEnabled': ONLY_NON_EDITABLE_STYLES,
     'showOnlyProgressionStylesEnabled': ONLY_PROGRESSION_STYLES}


FILTER_TYPES_MAPPING = {CarouselFilterTypes.HISTORIC: FilterTypes.HISTORIC,
 CarouselFilterTypes.NON_HISTORIC: FilterTypes.HISTORIC,
 CarouselFilterTypes.FANTASTICAL: FilterTypes.HISTORIC,
 CarouselFilterTypes.INVENTORY: FilterTypes.INVENTORY,
 CarouselFilterTypes.APPLIED: FilterTypes.APPLIED,
 CarouselFilterTypes.FAVORITE: FilterTypes.FAVORITE,
 CarouselFilterTypes.FORMFACTOR_GROUPS: FilterTypes.FORMFACTORS,
 CarouselFilterTypes.ON_ANOTHER_VEH: FilterTypes.USED_UP,
 CarouselFilterTypes.ONLY_PROGRESSION_DECALS: FilterTypes.PROGRESSION,
 CarouselFilterTypes.ONLY_EDITABLE_STYLES: FilterTypes.EDITABLE_STYLES,
 CarouselFilterTypes.ONLY_NON_EDITABLE_STYLES: FilterTypes.EDITABLE_STYLES,
 CarouselFilterTypes.ONLY_PROGRESSION_STYLES: FilterTypes.PROGRESSION_STYLE}
FILTER_ALIAS_MAPPING = {CarouselFilterTypes.HISTORIC: FilterAliases.HISTORIC,
 CarouselFilterTypes.NON_HISTORIC: FilterAliases.NON_HISTORIC,
 CarouselFilterTypes.FANTASTICAL: FilterAliases.FANTASTICAL,
 CarouselFilterTypes.ONLY_EDITABLE_STYLES: FilterAliases.EDITABLE_STYLES,
 CarouselFilterTypes.ONLY_NON_EDITABLE_STYLES: FilterAliases.NON_EDITABLE_STYLES}
HOT_FILTER_MAPPING = {FilterTypes.INVENTORY: CarouselFilterTypes.INVENTORY,
 FilterTypes.APPLIED: CarouselFilterTypes.APPLIED,
 FilterTypes.FAVORITE: CarouselFilterTypes.FAVORITE}
CustomizationCarouselDataVO = namedtuple('CustomizationCarouselDataVO', ('displayString', 'isZeroCount', 'shouldShow', 'itemLayoutSize', 'bookmarks', 'arrows', 'showSeparators'))
STYLE_TAB_LABEL_TMPL = '{}-{}'

class CustomizationBottomPanel(CustomizationBottomPanelMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    eventsCache = dependency.descriptor(IEventsCache)
    service = dependency.descriptor(ICustomizationService)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(CustomizationBottomPanel, self).__init__()
        self.__ctx = None
        self._carouselDP = None
        self._selectedItem = None
        return

    def _populate(self):
        super(CustomizationBottomPanel, self)._populate()
        self.__ctx = self.service.getCtx()
        self._carouselDP = CustomizationCarouselDataProvider(self._carouseItemWrapper)
        self._carouselDP.setFlashObject(self.getDp())
        self._carouselDP.setEnvironment(self.app)
        self.__ctx.events.onCarouselFiltered += self.__onCarouselFiltered
        self.__ctx.events.onCacheResync += self.__onCacheResync
        self.__ctx.events.onSeasonChanged += self.__onSeasonChanged
        self.__ctx.events.onItemInstalled += self.__onItemsInstalled
        self.__ctx.events.onTabChanged += self.__onTabChanged
        self.__ctx.events.onItemsRemoved += self.__onItemsRemoved
        self.__ctx.events.onModeChanged += self.__onModeChanged
        self.__ctx.events.onChangesCanceled += self.__onChangesCanceled
        self.__ctx.events.onComponentChanged += self.__onComponentChanged
        self.__ctx.events.onInstallNextCarouselItem += self.__onInstallNextCarouselItem
        self.__ctx.events.onItemSelected += self.__onItemSelected
        self.__ctx.events.onItemUnselected += self.__onItemUnselected
        self.__ctx.events.onSlotSelected += self.__onSlotSelected
        self.__ctx.events.onSlotUnselected += self.__onSlotUnselected
        self.__ctx.events.onFilterPopoverClosed += self.__onFilterPopoverClosed
        self.__ctx.events.onGetItemBackToHand += self.__onGetItemBackToHand
        g_currentVehicle.onChanged += self.__onVehicleChanged
        g_clientUpdateManager.addMoneyCallback(self.__setBottomPanelBillData)
        self.__setBottomPanelBillData()
        self.__updatePopoverBtn()
        self.__c11nSettings = AccountSettings.getSettings(CUSTOMIZATION_SECTION)
        self.__c11nFilterSettings = AccountSettings.getFilter(CustomizationFilter.CUSTOMIZATION_FILTER)
        self.__serverSettings = self.settingsCore.serverSettings
        self.__stageSwitcherVisibility = False
        self.__applyCurrentFilter()
        self.__setFooterInitData()
        BigWorld.callback(0.0, lambda : self.__onTabChanged(self.__ctx.tabId))

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__ctx.events.onComponentChanged -= self.__onComponentChanged
        self.__ctx.events.onChangesCanceled -= self.__onChangesCanceled
        self.__ctx.events.onModeChanged -= self.__onModeChanged
        self.__ctx.events.onItemsRemoved -= self.__onItemsRemoved
        self.__ctx.events.onTabChanged -= self.__onTabChanged
        self.__ctx.events.onItemInstalled -= self.__onItemsInstalled
        self.__ctx.events.onSeasonChanged -= self.__onSeasonChanged
        self.__ctx.events.onCacheResync -= self.__onCacheResync
        self.__ctx.events.onCarouselFiltered -= self.__onCarouselFiltered
        self.__ctx.events.onInstallNextCarouselItem -= self.__onInstallNextCarouselItem
        self.__ctx.events.onItemSelected -= self.__onItemSelected
        self.__ctx.events.onItemUnselected -= self.__onItemUnselected
        self.__ctx.events.onSlotSelected -= self.__onSlotSelected
        self.__ctx.events.onSlotUnselected -= self.__onSlotUnselected
        self.__ctx.events.onFilterPopoverClosed -= self.__onFilterPopoverClosed
        self.__ctx.events.onGetItemBackToHand -= self.__onGetItemBackToHand
        g_currentVehicle.onChanged -= self.__onVehicleChanged
        self._carouselDP._dispose()
        self._carouselDP = None
        self.__ctx = None
        self._selectedItem = None
        self.__c11nSettings = None
        self.__c11nFilterSettings = None
        self.__serverSettings = None
        super(CustomizationBottomPanel, self)._dispose()
        return

    def getDp(self):
        return self.as_getDataProviderS()

    def returnToStyledMode(self):
        self.__changeMode(CustomizationModes.STYLED)

    def onSelectHotFilter(self, index, value):
        filterType = (FilterTypes.INVENTORY, FilterTypes.APPLIED, FilterTypes.FAVORITE)[index]
        self._carouselDP.updateCarouselFilter(filterType, value)
        self.__refreshHotFilters()
        self.__setFilterSettings({HOT_FILTER_MAPPING[filterType]: value})
        self.__rebuildCarousel()
        self.__updateHints()

    def showGroupFromTab(self, tabIndex):
        self.__ctx.changeTab(tabIndex)

    def onSelectItem(self, index, intCD, progressionLevel):
        if intCD != -1:
            self.__ctx.mode.selectItem(intCD, progressionLevel)
            if self.__ctx.tabId == CustomizationTabs.PROJECTION_DECALS:
                self.__onProjectionDecalOnlyOnceHintHidden(record=True)
            elif self.__ctx.tabId in CustomizationTabs.STYLES_ALL:
                self.__onEditableStylesHintsHidden(record=True)
        else:
            self.__ctx.mode.unselectItem()

    def onEditItem(self, intCD):
        self.__ctx.editStyle(intCD, source=CustomizationModeSource.CAROUSEL)
        self.__updatePopoverBtn()

    def onItemIsNewAnimationShown(self, intCD):
        visitedSet = AccountSettings.getSettings(CUSTOMIZATION_STYLE_ITEMS_VISITED)
        visitedSet.add(intCD)
        AccountSettings.setSettings(CUSTOMIZATION_STYLE_ITEMS_VISITED, visitedSet)

    def blinkCounter(self):
        self.as_playFilterBlinkS()

    def resetFilter(self):
        self.__clearFilter()
        self.refreshFilterData()
        self.__rebuildCarousel()

    def refreshFilterData(self):
        filterData = self._carouselDP.getFilterData()
        self.as_setFilterDataS(filterData)

    @property
    def carouselItems(self):
        return self._carouselDP.collection

    def getVisibleTabs(self):
        return self._carouselDP.getVisibleTabs()

    def isItemUnsuitable(self, item):
        return self._carouselDP.processDependentParams(item)[1]

    def __changeMode(self, modeId):
        self.__ctx.changeMode(modeId, source=CustomizationModeSource.BOTTOM_PANEL)
        self.__updatePopoverBtn()

    def __onInstallNextCarouselItem(self, reverse):
        if self.__ctx.mode.selectedSlot is None:
            return
        else:
            item = self._carouselDP.getNextItem(reverse)
            if item is None:
                return
            self.__ctx.mode.selectItem(item.intCD)
            return

    def __onSlotSelected(self, *_, **__):
        if self.__ctx.tabId == CustomizationTabs.PROJECTION_DECALS:
            self.__rebuildCarousel(scroll=True)
        else:
            self._carouselDP.refresh()
            self.__updateSelection(scroll=True)
        self.__updatePopoverBtn()
        self.__updateFilterMessage()

    def __onSlotUnselected(self):
        if self.__ctx.tabId == CustomizationTabs.PROJECTION_DECALS:
            prevSelected = self._selectedItem
            self.__rebuildCarousel()
            if prevSelected is not None:
                self.__scrollToItem(prevSelected.intCD, True)
        else:
            self._carouselDP.refresh()
            self.__updateSelection(scroll=True)
        self.__updateFilterMessage()
        self.__updatePopoverBtn()
        return

    def __setNotificationCounters(self):
        vehicle = g_currentVehicle.item
        proxy = g_currentVehicle.itemsCache.items
        tabsCounters = []
        visibleTabs = self.getVisibleTabs()
        season = self.__ctx.season
        if self.__ctx.modeId == CustomizationModes.EDITABLE_STYLE:
            itemFilter = self.__ctx.mode.style.isItemInstallable
        else:
            itemFilter = lambda item: self.__filterAvailableItems(item, vehicle)
        for tabId in visibleTabs:
            tabItemTypes = CustomizationTabs.ITEM_TYPES[tabId]
            if tabId in CustomizationTabs.STYLES_ALL:
                noveltyCounter = 0
                newItems = [ item for item in vehicle.getNewC11nItems(proxy) if isinstance(item, Style) ]
                for item in newItems:
                    if item.is3D and tabId == CustomizationTabs.STYLES_3D or not item.is3D and tabId == CustomizationTabs.STYLES_2D:
                        noveltyCounter += item.getNoveltyCounter(vehicle)

                tabsCounters.append(noveltyCounter)
            tabsCounters.append(vehicle.getC11nItemsNoveltyCounter(proxy, itemTypes=tabItemTypes, season=season, itemFilter=itemFilter))

        self.as_setNotificationCountersS({'tabsCounters': tabsCounters})

    @staticmethod
    def __filterAvailableItems(item, vehicle):
        return False if item.isStyleOnly else item.inventoryCount or item.installedCount(vehicle.intCD)

    def __resetTabs(self):
        self.as_setBottomPanelTabsDataS({'tabsDP': [],
         'selectedTab': -1})

    def __updateTabs(self):
        tabsData, pluses = self.__getItemTabsData()
        if not tabsData:
            selectedTab = -1
        else:
            selectedTab = self.__ctx.tabId
        self.as_setBottomPanelTabsDataS({'tabsDP': tabsData,
         'selectedTab': selectedTab,
         'isEditable': self.__ctx.modeId == CustomizationModes.EDITABLE_STYLE})
        self.as_setBottomPanelTabsPlusesS(pluses)

    def __setFooterInitData(self):
        self.as_setBottomPanelInitDataS({'tabsAvailableRegions': CustomizationTabs.ALL,
         'filtersVO': {'popoverAlias': VIEW_ALIAS.CUSTOMIZATION_FILTER_POPOVER,
                       'mainBtn': {'value': RES_ICONS.MAPS_ICONS_BUTTONS_FILTER,
                                   'tooltip': VEHICLE_CUSTOMIZATION.CAROUSEL_FILTER_MAINBTN},
                       'hotFilters': [{'value': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_STORAGE_ICON,
                                       'tooltip': VEHICLE_CUSTOMIZATION.CAROUSEL_FILTER_STORAGEBTN,
                                       'selected': self._carouselDP.isFilterApplied(FilterTypes.INVENTORY)}, {'value': RES_ICONS.MAPS_ICONS_BUTTONS_EQUIPPED_ICON,
                                       'tooltip': VEHICLE_CUSTOMIZATION.CAROUSEL_FILTER_EQUIPPEDBTN,
                                       'selected': self._carouselDP.isFilterApplied(FilterTypes.APPLIED)}, {'value': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_FAVORITE_FILTER,
                                       'tooltip': VEHICLE_CUSTOMIZATION.CAROUSEL_FILTER_FAVORITEBTN,
                                       'selected': self._carouselDP.isFilterApplied(FilterTypes.FAVORITE)}]}})
        self.__setNotificationCounters()
        self.__updateFilterMessage()

    def __updateFilterMessage(self):
        self.as_carouselFilterMessageS(text_styles.leadingText('{}{}\n{}'.format(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ATTENTIONICONFILLED, vSpace=-3), text_styles.cream15(VEHICLE_CUSTOMIZATION.CAROUSEL_MESSAGE_HEADER), text_styles.main(self.__getFilterMessage())), 6))

    def __getFilterMessage(self):
        selectedSlot = self.__ctx.mode.selectedSlot
        if selectedSlot is not None and selectedSlot.slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
            return backport.text(R.strings.vehicle_customization.carousel.message.propertysheet())
        else:
            if g_currentVehicle.item.isProgressionDecalsOnly:
                if not isVehicleCanBeCustomized(g_currentVehicle.item, GUI_ITEM_TYPE.PROJECTION_DECAL):
                    return backport.text(R.strings.vehicle_customization.carousel.message.noProgressionDecals())
            return backport.text(R.strings.vehicle_customization.carousel.message.description())

    def __buildCustomizationCarouselDataVO(self):
        isZeroCount = self._carouselDP.itemCount == 0
        countStyle = text_styles.error if isZeroCount else text_styles.main
        displayString = text_styles.main('{} / {}'.format(countStyle(str(self._carouselDP.itemCount)), str(self._carouselDP.totalItemCount)))
        self.__ctx.carouselItemsCounts = (self._carouselDP.itemCount, self._carouselDP.totalItemCount)
        shouldShow = self._carouselDP.hasAppliedFilter()
        if self.__c11nFilterSettings.get(CustomizationFilter.DISPLAY_GROUP) or self.__ctx.modeId == CustomizationModes.EDITABLE_STYLE:
            bookmarks = self._carouselDP.getBookmarskData()
            arrows = self._carouselDP.getArrowsData()
            showSeparators = self._carouselDP.getShowSeparatorsData()
        else:
            bookmarks = []
            arrows = []
            showSeparators = False
        return CustomizationCarouselDataVO(displayString, isZeroCount or self._carouselDP.hasNewNonFilteredItem(), shouldShow, itemLayoutSize=self._carouselDP.getItemSizeData(), bookmarks=bookmarks, arrows=arrows, showSeparators=showSeparators)._asdict()

    def __setBottomPanelBillData(self, *_):
        purchaseItems = self.__ctx.mode.getPurchaseItems()
        purchaseItems = self.__processBillDataPurchaseItems(purchaseItems)
        cartInfo = getTotalPurchaseInfo(purchaseItems)
        totalPriceVO = getItemPricesVO(cartInfo.totalPrice)
        label = _ms(VEHICLE_CUSTOMIZATION.COMMIT_APPLY)
        fromStorageCount = 0
        hasLockedItemsInStyle = False
        toBuyCount = 0
        lockedCount = 0
        for pItem in purchaseItems:
            if not pItem.item.isHiddenInUI():
                if not pItem.item.isUnlockedByToken():
                    lockedCount += 1
                elif pItem.isFromInventory:
                    fromStorageCount += 1
                else:
                    toBuyCount += 1
                curItem = pItem.item
                if curItem.isQuestsProgression and curItem.itemTypeID == GUI_ITEM_TYPE.STYLE:
                    totalItems = curItem.descriptor.questsProgression.getTotalCount()
                    itemsOpened = sum([ curItem.descriptor.questsProgression.getUnlockedCount(token, self.eventsCache.questsProgress.getTokenCount(token)) for token in curItem.descriptor.questsProgression.getGroupTokens() ])
                    hasLockedItemsInStyle = totalItems != itemsOpened

        for pItem in purchaseItems:
            if pItem.item.itemTypeID != GUI_ITEM_TYPE.PERSONAL_NUMBER:
                continue
            if not pItem.component.isFilled():
                hasEmptyNumber = True
                break
        else:
            hasEmptyNumber = False

        hasLockedItems = self.__ctx.mode.isOutfitsHasLockedItems()
        outfitsModified = buyBtnEnabled = self.__ctx.isOutfitsModified()
        if buyBtnEnabled and cartInfo.totalPrice != ITEM_PRICE_EMPTY:
            label = _ms(VEHICLE_CUSTOMIZATION.COMMIT_BUY)
        if hasEmptyNumber:
            tooltip = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_EMPTYPERSONALNUMBER
        elif hasLockedItems:
            tooltip = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_LOCKEDITEMSAPPLY
        elif self.__ctx.mode.isOutfitsEmpty():
            tooltip = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_NOTSELECTEDITEMS
        else:
            tooltip = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_ALREADYAPPLIED
        if outfitsModified:
            if fromStorageCount > 0 or toBuyCount > 0:
                self.__showBill()
            else:
                self.__hideBill()
        else:
            self.__hideBill()
        compoundPrice = totalPriceVO[0]
        if not compoundPrice['price']:
            compoundPrice['price'] = getMoneyVO(Money(gold=0))
        fromStorageCount = text_styles.stats('({})'.format(fromStorageCount))
        toBuyCount = text_styles.stats('({})'.format(toBuyCount))
        billLines = [self.__makeBillLine(text_styles.main('{} {}'.format(_ms(VEHICLE_CUSTOMIZATION.BUYPOPOVER_PRICE), toBuyCount)), compoundPrice=compoundPrice, isEnoughStatuses=getMoneyVO(Money(True, True, True))), self.__makeBillLine(text_styles.main('{} {}'.format(_ms(VEHICLE_CUSTOMIZATION.BUYPOPOVER_FROMSTORAGE), fromStorageCount)), icon=RES_ICONS.MAPS_ICONS_CUSTOMIZATION_STORAGE_ICON)]
        buttons = [self.__makeButton(_ms(VEHICLE_CUSTOMIZATION.BUYPOPOVER_BTNCLEARALL), BillPopoverButtons.CUSTOMIZATION_CLEAR, RES_ICONS.MAPS_ICONS_CUSTOMIZATION_ICON_CROSS)]
        if hasLockedItems or hasLockedItemsInStyle:
            lockedCountText = text_styles.stats('({})'.format(lockedCount))
            billLines.append(self.__makeBillLine(text_styles.main('{} {}'.format(_ms(VEHICLE_CUSTOMIZATION.BUYPOPOVER_LOCKED), lockedCountText)), icon=RES_ICONS.MAPS_ICONS_CUSTOMIZATION_LOCK_ICON))
            buttons.append(self.__makeButton(_ms(VEHICLE_CUSTOMIZATION.BUYPOPOVER_BTNCLEARLOCKED), BillPopoverButtons.CUSTOMIZATION_CLEAR_LOCKED, enabled=lockedCount > 0))
        self.as_setBottomPanelPriceStateS({'buyBtnEnabled': buyBtnEnabled and not hasLockedItems,
         'buyBtnLabel': label,
         'buyBtnTooltip': tooltip,
         'customizationDisplayType': self.__ctx.mode.currentOutfit.customizationDisplayType(),
         'billVO': {'title': text_styles.highlightText(_ms(VEHICLE_CUSTOMIZATION.BUYPOPOVER_RESULT)),
                    'lines': billLines,
                    'buttons': buttons}})
        itemsPopoverBtnEnabled = False
        for intCD, component, _, _, _ in self.__ctx.mode.currentOutfit.itemsFull():
            if component.isFilled():
                item = self.service.getItemByCD(intCD)
                if item.isHiddenInUI():
                    continue
                itemsPopoverBtnEnabled = True
                break

        self.as_setItemsPopoverBtnEnabledS(itemsPopoverBtnEnabled)

    def __makeBillLine(self, label, icon=None, compoundPrice=None, isEnoughStatuses=None):
        return {'label': label,
         'icon': icon,
         'compoundPrice': compoundPrice,
         'isEnoughStatuses': isEnoughStatuses}

    def __makeButton(self, label, event, icon=None, enabled=True):
        return {'label': label,
         'icon': icon,
         'event': event,
         'enabled': enabled}

    def __showBill(self):
        self.as_showBillS()

    def __hideBill(self):
        self.as_hideBillS()

    def __refreshHotFilters(self):
        self.as_setCarouselFiltersDataS({'hotFilters': [self._carouselDP.isFilterApplied(FilterTypes.INVENTORY), self._carouselDP.isFilterApplied(FilterTypes.APPLIED), self._carouselDP.isFilterApplied(FilterTypes.FAVORITE)],
         'newHiddenElementsCount': self._carouselDP.refreshNewHiddenElementsCount()})

    def __clearFilter(self):
        self.__c11nFilterSettings = AccountSettings.getFilterDefaults((CustomizationFilter.CUSTOMIZATION_FILTER,))
        AccountSettings.setFilter(CustomizationFilter.CUSTOMIZATION_FILTER, self.__c11nFilterSettings)
        self._carouselDP.clearFilter()
        self.__refreshHotFilters()

    def __rebuildCarousel(self, scroll=False):
        self.__applyCurrentFilter()
        self._carouselDP.invalidateFilteredItems()
        self._carouselDP.buildList()
        self._carouselDP.refresh()
        self.__updateSelection(scroll)
        self.as_setCarouselDataS(self.__buildCustomizationCarouselDataVO())

    def _carouseItemWrapper(self, itemCD):
        item = self.service.getItemByCD(itemCD)
        inventoryCount = self.__ctx.mode.getItemInventoryCount(item)
        purchaseLimit = self.__ctx.mode.getPurchaseLimit(item)
        isApplied = itemCD in self._carouselDP.getAppliedItems()
        isBaseStyleItem = itemCD in self._carouselDP.getBaseStyleItems()
        if item.isStyleOnly or isBaseStyleItem:
            isDarked = isUsedUp = False
        else:
            isDarked = purchaseLimit <= 0 and inventoryCount <= 0
            isUsedUp = isItemUsedUp(item)
        showEditableHint = False
        showEditBtnHint = False
        if self.__ctx.modeId == CustomizationModes.STYLED:
            autoRentEnabled = self.__ctx.mode.isAutoRentEnabled()
            if item.isProgressionRequired:
                showEditableHint = not bool(self.__serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.C11N_PROGRESSION_REQUIRED_STYLE_SLOT_HINT))
                showEditBtnHint = not bool(self.__serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.C11N_PROGRESSION_REQUIRED_STYLE_SLOT_BUTTON_HINT))
            elif item.isEditable:
                showEditableHint = not bool(self.__serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.C11N_EDITABLE_STYLE_SLOT_HINT))
                showEditBtnHint = not bool(self.__serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.C11N_EDITABLE_STYLE_SLOT_BUTTON_HINT))
        else:
            autoRentEnabled = False
        isChained, isUnsuitable = self._carouselDP.processDependentParams(item)
        return buildCustomizationItemDataVO(item=item, count=inventoryCount, isApplied=isApplied, isDarked=isDarked, isUsedUp=isUsedUp, autoRentEnabled=autoRentEnabled, vehicle=g_currentVehicle.item, showEditableHint=showEditableHint, showEditBtnHint=showEditBtnHint, isChained=isChained, isUnsuitable=isUnsuitable, isInProgress=item.isQuestInProgress())

    def __getItemTabsData(self):
        tabsData = []
        pluses = []
        visibleTabs = self.getVisibleTabs()
        outfit = self.__ctx.mode.currentOutfit
        for tabId in visibleTabs:
            slotType = CustomizationTabs.SLOT_TYPES[tabId]
            itemTypeName = GUI_ITEM_TYPE_NAMES[slotType]
            slotsCount, filledSlotsCount = checkSlotsFilling(outfit, slotType)
            showPlus = filledSlotsCount < slotsCount
            groupId, _ = getTabGroupId(tabId)
            labelR = R.strings.item_types.customization.plural
            tooltipR = R.strings.tooltips.customization.tabs
            tabStr = itemTypeName
            if tabId in CustomizationTabs.STYLES_ALL:
                labelR = labelR.style
                tooltipR = tooltipR.style
                prefix = CustomizationTabs.STYLE_PREFIX[tabId]
                tabStr = 'c_{}'.format(prefix)
                iconName = '{}_{}_hover'.format(itemTypeName, prefix)
            else:
                iconName = '{}_hover'.format(itemTypeName)
            icon = backport.image(R.images.gui.maps.icons.customization.customization_icon.dyn(iconName)())
            label = backport.text(labelR.dyn(tabStr)())
            tooltip = backport.text(tooltipR.dyn(tabStr).body())
            tabsData.append({'label': label,
             'icon': icon,
             'tooltip': makeTooltip(label, tooltip),
             'id': tabId,
             'groupId': groupId})
            pluses.append(showPlus)

        return (tabsData, pluses)

    def __applyCarouselFilter(self, kwargs):
        for key, value in kwargs.iteritems():
            filterType = FILTER_TYPES_MAPPING.get(key)
            filterAlias = FILTER_ALIAS_MAPPING.get(key)
            if FILTER_TYPES_MAPPING.get(key):
                if FILTER_ALIAS_MAPPING.get(key):
                    self._carouselDP.updateCarouselFilter(filterType, value, filterAlias)
                else:
                    self._carouselDP.updateCarouselFilter(filterType, value)

    def __onCarouselFiltered(self, **kwargs):
        if CarouselFilterTypes.GROUP in kwargs:
            self._carouselDP.updateSelectedGroup(kwargs[CarouselFilterTypes.GROUP])
        self.__applyCarouselFilter(kwargs)
        self.__refreshHotFilters()
        self.__setFilterSettings(kwargs)
        self.__rebuildCarousel()
        self.__updateHints()

    def __setFilterSettings(self, kwargs):
        currentFilterTab = CustomizationTabs.TAB_TO_GROUP.get(self.__ctx.tabId)
        for key, value in kwargs.iteritems():
            if key == CarouselFilterTypes.GROUP:
                self.__c11nFilterSettings[currentFilterTab] = value
                continue
            if key == CarouselFilterTypes.FORMFACTOR_GROUPS:
                for formfactor, formfactorValue in value.iteritems():
                    self.__c11nFilterSettings[formfactor] = formfactorValue

                continue
            self.__c11nFilterSettings[key] = value

        AccountSettings.setFilter(CustomizationFilter.CUSTOMIZATION_FILTER, self.__c11nFilterSettings)

    def __applyCurrentFilter(self):
        carouselFilterData = self._carouselDP.getFilterData()
        currentFilterTab = CustomizationTabs.TAB_TO_GROUP.get(self.__ctx.tabId)
        if currentFilterTab:
            groupFilter = self.__c11nFilterSettings[currentFilterTab]
            if groupFilter == -1:
                groupFilter = carouselFilterData['groupCount'] - 1
            if groupFilter != -1:
                self._carouselDP.updateSelectedGroup(groupFilter)
        for key, value in carouselFilterData.iteritems():
            if key == CarouselFilterTypes.GROUP:
                continue
            if key == CarouselFilterTypes.FORMFACTOR_GROUPS:
                if value:
                    formfactorGroups = OrderedDict({CustomizationFilter.FORMFACTOR_SQUARE: self.__c11nFilterSettings[CustomizationFilter.FORMFACTOR_SQUARE],
                     CustomizationFilter.FORMFACTOR_RECT1X2: self.__c11nFilterSettings[CustomizationFilter.FORMFACTOR_RECT1X2],
                     CustomizationFilter.FORMFACTOR_RECT1X3: self.__c11nFilterSettings[CustomizationFilter.FORMFACTOR_RECT1X3],
                     CustomizationFilter.FORMFACTOR_RECT1X4: self.__c11nFilterSettings[CustomizationFilter.FORMFACTOR_RECT1X4],
                     CustomizationFilter.FORMFACTOR_RECT1X6: self.__c11nFilterSettings[CustomizationFilter.FORMFACTOR_RECT1X6]})
                    self._carouselDP.updateCarouselFilter(FilterTypes.FORMFACTORS, formfactorGroups)
                continue
            filterType = CarouselFilterTypes.VO_TYPE_TO_FILTER.get(key)
            if filterType:
                currentFilterValue = self.__c11nFilterSettings[filterType]
                if value != currentFilterValue:
                    self.__applyCarouselFilter({filterType: currentFilterValue})

    def __onCacheResync(self, reason, items):
        if not g_currentVehicle.isPresent():
            return
        typesForUpdate = {GUI_ITEM_TYPE.CUSTOMIZATION, GUI_ITEM_TYPE.CUSTOMIZATIONS}
        if not typesForUpdate & set(items):
            return
        self._carouselDP.invalidateItems()
        self.__updateTabs()
        self.__setBottomPanelBillData()
        self.__rebuildCarousel()
        self.__setNotificationCounters()

    def __onVehicleChanged(self):
        self._carouselDP.invalidateItems()
        self.__updateTabs()
        self.refreshFilterData()
        self.__rebuildCarousel()
        self.__updatePopoverBtn()
        self.__setBottomPanelBillData()
        self.__setFooterInitData()
        self.__scrollToPreferredItem()

    def __onSeasonChanged(self, seasonType):
        self.__updateTabs()
        self.__rebuildCarousel()
        self.__updatePopoverBtn()
        self.__setBottomPanelBillData()
        self.__setNotificationCounters()
        self.__scrollToPreferredItem()

    def __updatePopoverBtn(self):
        imgSrc = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_ITEMS_POPOVER_DEFAULT_LIST30X16
        tooltip = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_ITEMSPOPOVER_BTN_STYLE_DISABLED
        if self.__ctx.modeId != CustomizationModes.STYLED:
            if self.__ctx.season == SeasonType.WINTER:
                imgSrc = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_ITEMS_POPOVER_WINTER_LIST30X16
            elif self.__ctx.season == SeasonType.SUMMER:
                imgSrc = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_ITEMS_POPOVER_SUMMER_LIST30X16
            elif self.__ctx.season == SeasonType.DESERT:
                imgSrc = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_ITEMS_POPOVER_DESERT_LIST30X16
            seasonName = SEASON_TYPE_TO_NAME.get(self.__ctx.season)
            mapName = VEHICLE_CUSTOMIZATION.getMapName(seasonName)
            tooltip = _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_ITEMSPOPOVER_BTN_DISABLED, mapType=_ms(mapName))
        if self.__ctx.modeId == CustomizationModes.CUSTOM:
            popoverAlias = VIEW_ALIAS.CUSTOMIZATION_ITEMS_POPOVER
        else:
            style = self.__ctx.mode.currentOutfit.style
            if style is not None and style.isEditable:
                if style.isQuestsProgression:
                    popoverAlias = VIEW_ALIAS.CUSTOMIZATION_PROGRESSIVE_KIT_POPOVER
                else:
                    popoverAlias = VIEW_ALIAS.CUSTOMIZATION_EDITED_KIT_POPOVER
            else:
                popoverAlias = VIEW_ALIAS.CUSTOMIZATION_KIT_POPOVER
        self.as_updatePopoverBtnS(imgSrc, popoverAlias, tooltip)
        return

    def __onItemsInstalled(self, item, slotId, season, component):
        self.__updateTabs()
        self.__setBottomPanelBillData()
        self.__rebuildCarousel()
        if slotId == self.__ctx.mode.selectedSlot and (season is None or season == self.__ctx.season):
            self.__scrollToItem(item.intCD, self._selectedItem.id == item.id)
        return

    def __onTabChanged(self, tabIndex, itemCD=None):
        self.__updateTabs()
        self.__rebuildCarousel()
        self.__refreshHotFilters()
        self.__setNotificationCounters()
        itemCD = itemCD or self.__updateHints()
        if itemCD is not None:
            self.__scrollToItem(itemCD)
        elif self._selectedItem is None:
            self.__scrollToPreferredItem()
        return

    def __onItemsRemoved(self, *_, **__):
        self.__updateTabs()
        self.__setBottomPanelBillData()
        selectedItem = self._selectedItem
        self.__rebuildCarousel()
        if selectedItem is not None:
            self.__scrollToItem(selectedItem.intCD, immediately=True)
        return

    def __onModeChanged(self, modeId, prevModeId):
        self._carouselDP.modeChanged(modeId, prevModeId)
        self.__setBottomPanelBillData()
        self.__setFooterInitData()
        if modeId == CustomizationModes.EDITABLE_STYLE:
            record = self.__ctx.mode.source in (CustomizationModeSource.CAROUSEL, CustomizationModeSource.PROPERTIES_SHEET, CustomizationModeSource.CONTEXT_MENU)
            self.__onEditableStylesHintsHidden(record=record)
        self.__updatePopoverBtn()

    def __onChangesCanceled(self):
        self.__updateTabs()
        self.__setBottomPanelBillData()
        self.__updatePopoverBtn()
        self._carouselDP.invalidateFilteredItems()
        self.__rebuildCarousel()

    def __onComponentChanged(self, slotId, refreshCarousel):
        self.__setBottomPanelBillData()
        if refreshCarousel:
            self.__rebuildCarousel()

    def __scrollToPreferredItem(self):
        tabId = self.__ctx.mode.tabId
        itemTypes = CustomizationTabs.ITEM_TYPES[tabId]
        newItems = sorted(g_currentVehicle.item.getNewC11nItems(g_currentVehicle.itemsCache.items), key=comparisonKey)
        for item in newItems:
            if tabId in CustomizationTabs.STYLES_ALL:
                if self.__isStyleTabHasItem(item, tabId):
                    self.__scrollToItem(item.intCD, immediately=True)
                    return
                continue
            if item.itemTypeID in itemTypes and item.season & self.__ctx.season and self.__filterAvailableItems(item, g_currentVehicle.item):
                self.__scrollToItem(item.intCD, immediately=True)
                return

        if tabId in CustomizationTabs.STYLES_ALL:
            style = self.__ctx.mode.modifiedStyle
            if style is not None and self.__isStyleTabHasItem(style, tabId) and style in self._carouselDP.getItemsData():
                self.__scrollToItem(style.intCD, immediately=True)
            return
        else:
            for item in self._carouselDP.getItemsData():
                if item.intCD in self.__ctx.mode.currentOutfit.items() and item.itemTypeID in itemTypes and item.season & self.__ctx.season:
                    self.__scrollToItem(item.intCD, immediately=True)
                    return

            return

    def __isStyleTabHasItem(self, item, tabId):
        return True if isinstance(item, Style) and (item.is3D and tabId == CustomizationTabs.STYLES_3D or not item.is3D and tabId == CustomizationTabs.STYLES_2D) else False

    def __scrollToItem(self, itemCD, immediately=False):
        self.as_scrollToSlotS(itemCD, immediately)

    def __onFilterPopoverClosed(self):
        self.blinkCounter()

    def __onGetItemBackToHand(self, item, progressionLevel=-1, scrollToItem=False):
        if scrollToItem:
            self.__scrollToItem(item.intCD, immediately=True)

    def __onItemSelected(self, *_):
        self.__updateSelection()

    def __onItemUnselected(self):
        self.__updateSelection()

    def __updateSelection(self, scroll=False):
        if self.__ctx.mode.selectedItem is not None:
            self._selectedItem = self.__ctx.mode.selectedItem
        elif self.__ctx.mode.selectedSlot is not None:
            slotId = self.__ctx.mode.selectedSlot
            if slotId.slotType == GUI_ITEM_TYPE.STYLE:
                self._selectedItem = self.__ctx.mode.modifiedStyle
            else:
                self._selectedItem = self.__ctx.mode.getItemFromSlot(slotId)
        else:
            self._selectedItem = None
        self._carouselDP.selectItem(self._selectedItem)
        if self._selectedItem is not None and scroll:
            self.__scrollToItem(self._selectedItem.intCD, True)
        self.__updateStageSwitcherVisibility()
        self.__updatePopoverBtn()
        return

    def __updateHints(self):
        intCD = None
        if self.__ctx.tabId == CustomizationTabs.PROJECTION_DECALS:
            self.__onProjectionDecalOnlyOnceHintShown()
        else:
            self.__onProjectionDecalOnlyOnceHintHidden()
        if self.__ctx.tabId in CustomizationTabs.STYLES_ALL:
            intCD = self.__onEditableStylesHintsShown()
        else:
            self.__onEditableStylesHintsHidden()
        return intCD

    def __onProjectionDecalOnlyOnceHintShown(self):
        if self.__c11nSettings.get(PROJECTION_DECAL_HINT_SHOWN_FIELD, False):
            return
        else:
            isCarouselEmpty = not self._carouselDP.collection
            slotId = C11nId(Area.MISC, GUI_ITEM_TYPE.PROJECTION_DECAL, -1)
            multiSlot = getMultiSlot(self.__ctx.mode.currentOutfit, slotId)
            isSlotEmpty = multiSlot is not None and multiSlot.isEmpty()
            visible = isSlotEmpty and not isCarouselEmpty
            self.as_setProjectionDecalHintVisibilityS(visible)
            return

    def __onProjectionDecalOnlyOnceHintHidden(self, record=False):
        if record and not self.__c11nSettings.get(PROJECTION_DECAL_HINT_SHOWN_FIELD, False):
            self.__c11nSettings[PROJECTION_DECAL_HINT_SHOWN_FIELD] = True
            AccountSettings.setSettings(CUSTOMIZATION_SECTION, self.__c11nSettings)
        self.as_setProjectionDecalHintVisibilityS(False)

    def __onEditableStylesHintsShown(self):
        if not self.__serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.C11N_EDITABLE_STYLES_HINT):
            for intCD in self._carouselDP.collection:
                item = self.service.getItemByCD(intCD)
                if item.itemTypeID != GUI_ITEM_TYPE.STYLE:
                    return
                if item.canBeEditedForVehicle(g_currentVehicle.item.intCD):
                    self.as_setEditableStyleHintVisibilityS(True)
                    return item.intCD

            self.__onEditableStylesHintsHidden(record=False)
        elif not self.__serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.C11N_PROGRESSION_REQUIRED_STYLES_HINT):
            for intCD in self._carouselDP.collection:
                item = self.service.getItemByCD(intCD)
                if item.itemTypeID != GUI_ITEM_TYPE.STYLE:
                    return
                if item.isProgressionRequiredCanBeEdited(g_currentVehicle.item.intCD):
                    self.as_setEditableProgressionRequiredStyleHintVisibilityS(True)
                    return item.intCD

            self.__onEditableStylesHintsHidden(record=False)
        else:
            self.__onEditableStylesHintsHidden(record=False)

    def __onEditableStylesHintsHidden(self, record=False):
        self.as_setEditableStyleHintVisibilityS(False)
        self.as_setEditableProgressionRequiredStyleHintVisibilityS(False)
        if not record:
            return
        else:
            editableStylesVisited = self.__serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.C11N_EDITABLE_STYLES_HINT)
            editableProgressionRequiredStylesVisited = self.__serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.C11N_PROGRESSION_REQUIRED_STYLES_HINT)
            if not editableStylesVisited or not editableProgressionRequiredStylesVisited:
                editable = None
                editableProgressionRequired = None
                styles = self._carouselDP.getCarouselData(modeId=CustomizationModes.STYLED, tabId=CustomizationTabs.STYLES_2D)
                styles.extend(self._carouselDP.getCarouselData(modeId=CustomizationModes.STYLED, tabId=CustomizationTabs.STYLES_3D))
                for intCD in styles:
                    item = self.service.getItemByCD(intCD)
                    if item.itemTypeID != GUI_ITEM_TYPE.STYLE:
                        break
                    if item.isEditable:
                        editable = item
                        if editable.isProgressionRequiredCanBeEdited(g_currentVehicle.item.intCD):
                            editableProgressionRequired = editable
                            break

                settings = {}
                if editable is not None:
                    settings[OnceOnlyHints.C11N_EDITABLE_STYLES_HINT] = HINT_SHOWN_STATUS
                if editableProgressionRequired is not None:
                    settings[OnceOnlyHints.C11N_PROGRESSION_REQUIRED_STYLES_HINT] = HINT_SHOWN_STATUS
                if settings:
                    self.__serverSettings.setOnceOnlyHintsSettings(settings)
            return

    def __processBillDataPurchaseItems(self, purchseItems):
        if self.__ctx.modeId not in (CustomizationModes.EDITABLE_STYLE, CustomizationModes.STYLED):
            return purchseItems
        result = purchseItems[:1]
        for pItem in purchseItems[1:]:
            if pItem.isEdited:
                result.append(pItem)

        return result

    def __updateStageSwitcherVisibility(self):
        newVisibility = False
        if self.__ctx.mode.modeId == CustomizationModes.STYLED:
            styleItem = self.__ctx.mode.currentOutfit.style
            if styleItem:
                newVisibility = styleItem.isProgression
        if self.__stageSwitcherVisibility != newVisibility:
            self.__stageSwitcherVisibility = newVisibility
            self.as_setStageSwitcherVisibilityS(self.__stageSwitcherVisibility)
