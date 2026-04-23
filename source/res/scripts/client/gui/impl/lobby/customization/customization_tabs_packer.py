# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/customization_tabs_packer.py
from CurrentVehicle import g_currentVehicle
from gui.customization.constants import CustomizationModes
from gui.impl.gen.view_models.views.lobby.customization.customization_tab_item_model import CustomizationTabItemModel
from gui.impl.lobby.customization.shared import CustomizationTabs, getTabGroupId, checkSlotsFilling
from gui.shared.gui_items import GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.customization.c11n_items import Style

def fillTabsModel(tabsModel, ctx, carouselDP):
    tabsData = getItemTabsData(ctx, carouselDP)
    if not tabsData:
        selectedTab = -1
    else:
        selectedTab = ctx.tabId
    tabsList = tabsModel.getTabItemsList()
    tabsList.clear()
    for tabData in tabsData:
        tabId = tabData.get('id')
        tabItem = CustomizationTabItemModel()
        tabItem.setGroupId(tabData.get('groupId'))
        tabItem.setId(tabId)
        tabItem.setItemType(tabData.get('itemTypeName'))
        tabItem.setIsPlus(tabData.get('showPlus'))
        tabItem.setNoveltyCounter(tabData.get('noveltyCounter', 0))
        tabItem.setIsSelected(tabId == selectedTab)
        tabsList.addViewModel(tabItem)

    tabsList.invalidate()


def getItemTabsData(ctx, carouselDP):
    vehicle = g_currentVehicle.item
    proxy = g_currentVehicle.itemsCache.items
    tabsData = []
    season = ctx.season
    if ctx.modeId == CustomizationModes.EDITABLE_STYLE:
        itemFilter = ctx.mode.style.isItemInstallable
    else:
        itemFilter = lambda item: __filterAvailableStyles(item, vehicle)
    visibleTabs = getVisibleTabs(carouselDP)
    outfit = ctx.mode.currentOutfit
    selectedGroupId, _ = getTabGroupId(ctx.tabId)
    for tabId in visibleTabs:
        slotType = CustomizationTabs.SLOT_TYPES[tabId]
        itemTypeName = GUI_ITEM_TYPE_NAMES[slotType]
        slotsCount, filledSlotsCount = checkSlotsFilling(outfit, slotType)
        groupId, _ = getTabGroupId(tabId)
        showPlus = filledSlotsCount < slotsCount and selectedGroupId == groupId
        tabItemTypes = CustomizationTabs.ITEM_TYPES[tabId]
        noveltyCounter = 0
        if tabId in CustomizationTabs.STYLES_ALL:
            prefix = CustomizationTabs.STYLE_PREFIX[tabId]
            itemTypeName = itemTypeName + '_{}'.format(prefix)
            newItems = [ item for item in vehicle.getNewC11nItems(proxy) if isinstance(item, Style) ]
            for item in newItems:
                if item.is3D and tabId == CustomizationTabs.STYLED_3D or not item.is3D and tabId == CustomizationTabs.STYLED_2D:
                    noveltyCounter += item.getNoveltyCounter(vehicle)

        else:
            noveltyCounter = vehicle.getC11nItemsNoveltyCounter(proxy, itemTypes=tabItemTypes, season=season, itemFilter=itemFilter)
        tabsData.append({'itemTypeName': itemTypeName,
         'id': tabId,
         'groupId': groupId,
         'showPlus': showPlus,
         'noveltyCounter': noveltyCounter})

    return tabsData


def getVisibleTabs(carouselDP):
    return carouselDP.getVisibleTabs()


def __filterAvailableStyles(item, vehicle):
    return False if item.isStyleOnly else item.inventoryCount or item.installedCount(vehicle.intCD)
