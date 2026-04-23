# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/customization_seasons_data_packer.py
from typing import TYPE_CHECKING
from CurrentVehicle import g_currentVehicle
from gui.customization.constants import CustomizationModes
from gui.customization.shared import SEASONS_ORDER, SEASON_TYPE_TO_NAME
from gui.impl.gen.view_models.views.lobby.customization.customization_seasons_item_model import CustomizationSeasonsItemModel
from gui.impl.lobby.customization.shared import CustomizationTabs, checkSlotsFilling, getItemTypesAvailableForVehicle
from gui.shared.gui_items import GUI_ITEM_TYPE
if TYPE_CHECKING:
    from typing import Dict, List
    from gui.impl.gen.view_models.views.lobby.customization.customization_seasons_model import CustomizationSeasonsModel
    from gui.impl.lobby.customization.context.context import CustomizationContext

def fillSeasonsModel(seasonsModel, ctx):
    seasonsData = getSeasonData(ctx)
    itemsList = seasonsModel.getSeasonsList()
    itemsList.clear()
    for season in seasonsData:
        itemData = CustomizationSeasonsItemModel()
        itemData.setSeason(season['season'])
        itemData.setIsFull(season['isFull'])
        itemData.setIsSelected(season['isSelected'])
        itemData.setItemNotificationCount(season['notificationCount'])
        itemsList.addViewModel(itemData)

    itemsList.invalidate()


def getSeasonData(ctx):
    seasonsList = []
    seasonNotificationCounters = getNotificationCounters(ctx)
    for season in SEASONS_ORDER:
        isFull = False
        if ctx.modeId == CustomizationModes.CUSTOM:
            outfit = ctx.mode.getModifiedOutfit(season)
            slotTypes = (CustomizationTabs.SLOT_TYPES[tabId] for tabId in CustomizationTabs.CUSTOM_ALL)
            isFull = all((filled_slots >= total_slots for total_slots, filled_slots in (checkSlotsFilling(outfit, slot_type) for slot_type in slotTypes)))
        elif ctx.modeId in CustomizationModes.ALL_STYLES:
            isFull = ctx.mode.currentOutfit.style is not None
        seasonsList.append({'season': SEASON_TYPE_TO_NAME.get(season),
         'isFull': isFull,
         'isSelected': season == ctx.season,
         'notificationCount': seasonNotificationCounters[season]})

    return seasonsList


def getNotificationCounters(ctx):
    seasonCounters = {}
    itemTypes = (GUI_ITEM_TYPE.STYLE,) if ctx.modeId in CustomizationModes.STYLED else getItemTypesAvailableForVehicle() - {GUI_ITEM_TYPE.STYLE}
    itemsFilter = lambda item: ctx.mode.style.isItemInstallable(item) and not item.isAllSeason() if ctx.modeId == CustomizationModes.EDITABLE_STYLE else (lambda item: not item.isAllSeason())
    for season in SEASONS_ORDER:
        seasonCounters[season] = g_currentVehicle.item.getC11nItemsNoveltyCounter(g_currentVehicle.itemsCache.items, itemTypes, season, itemsFilter) if ctx.season != season else 0

    return seasonCounters
