# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/utils.py
from __future__ import absolute_import
import typing
from collections import namedtuple, OrderedDict
from functools import partial
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.clans.clan_helpers import isStrongholdsEnabled
from gui.impl.gen.view_models.views.lobby.hangar.main_menu_model import MainMenuModel
from gui.impl.gen.view_models.views.lobby.hangar.menu_item_model import MenuItemModel
from gui.server_events.events_dispatcher import showMissions
from gui.shared.event_dispatcher import showShop, showStorage, showBarracks, showViewByAlias, showTechTree, showModeSelectorWindow, showPersonalMissionCampaignSelectorWindow
from gui.shared.system_factory import registerMenuItems, collectMenuItems
from gui.tournament.tournament_helpers import showTournaments, isTournamentEnabled
from helpers import dependency
from items import vehicles
from items.components.c11n_constants import CustomizationType
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.lobby_context import ILobbyContext
from shared_utils import findFirst
MenuItemEntry = namedtuple('MenuItemEntry', ['handler', 'showCondition', 'enabledCondition'])
SHARED_MENU_ITEMS = OrderedDict([(MainMenuModel.MODE_SELECTOR, MenuItemEntry(showModeSelectorWindow, lambda : True, lambda : True))])

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def isPersonalMissionsEnabled(lobbyContext=None):
    serverSettings = lobbyContext.getServerSettings() if lobbyContext is not None else None
    return serverSettings.isPersonalMissionsEnabled() if serverSettings is not None else False


SHOP_MENU_ITEM = (MainMenuModel.SHOP, MenuItemEntry(showShop, lambda : True, lambda : True))
STORAGE_MENU_ITEM = (MainMenuModel.STORAGE, MenuItemEntry(showStorage, lambda : True, lambda : True))
MISSIONS_MENU_ITEM = (MainMenuModel.MISSIONS, MenuItemEntry(showMissions, lambda : True, lambda : True))
PERSONAL_MISSIONS_MENU_ITEM = (MainMenuModel.PERSONAL_MISSIONS, MenuItemEntry(showPersonalMissionCampaignSelectorWindow, lambda : True, isPersonalMissionsEnabled))
ACHIEVEMENTS_MENU_ITEM = (MainMenuModel.ACHIEVEMENTS, MenuItemEntry(partial(showViewByAlias, VIEW_ALIAS.LOBBY_PROFILE), lambda : True, lambda : True))
TECHTREE_MENU_ITEM = (MainMenuModel.TECHTREE, MenuItemEntry(showTechTree, lambda : True, lambda : True))
BARRACKS_MENU_ITEM = (MainMenuModel.BARRACKS, MenuItemEntry(showBarracks, lambda : True, lambda : True))
TOURNAMENT_MENU_ITEM = (MainMenuModel.TOURNAMENT, MenuItemEntry(showTournaments, isTournamentEnabled, isTournamentEnabled))
CLANS_MENU_ITEM = (MainMenuModel.CLANS, MenuItemEntry(partial(showViewByAlias, VIEW_ALIAS.LOBBY_STRONGHOLD), lambda : True, isStrongholdsEnabled))
RANDOM_MENU_ITEMS = OrderedDict(list(SHARED_MENU_ITEMS.items()) + [SHOP_MENU_ITEM,
 STORAGE_MENU_ITEM,
 MISSIONS_MENU_ITEM,
 PERSONAL_MISSIONS_MENU_ITEM,
 ACHIEVEMENTS_MENU_ITEM,
 TECHTREE_MENU_ITEM,
 BARRACKS_MENU_ITEM,
 TOURNAMENT_MENU_ITEM,
 CLANS_MENU_ITEM])
registerMenuItems('hangar', RANDOM_MENU_ITEMS)

def getSharedMenuItems():
    return SHARED_MENU_ITEMS.copy()


def getMenuItems():
    return collectMenuItems('hangar')


def fillMenuItems(model, menuData=RANDOM_MENU_ITEMS):
    menuItems = model.getMenuItems()
    menuItems.clear()
    for menuItemName in menuData:
        menuEntry = menuData.get(menuItemName)
        if not menuEntry.showCondition():
            continue
        menuItem = MenuItemModel()
        menuItem.setName(menuItemName)
        menuItem.setState(MenuItemModel.ENABLED if menuEntry.enabledCondition() else MenuItemModel.DISABLED)
        menuItems.addViewModel(menuItem)

    menuItems.invalidate()
    currentModeItem = findFirst(lambda item: item.isSelected(), battle_selector_items.getItems().getItems().values())
    if currentModeItem:
        model.setModeName(currentModeItem.getLabel())
        model.setModeId(currentModeItem.getData())


def fillMenuSharedItems(model, menuData=SHARED_MENU_ITEMS):
    fillMenuItems(model, menuData)


def navigateTo(args):
    name = args.get('name')
    menuEntry = RANDOM_MENU_ITEMS.get(name)
    menuEntry.handler()


def take3DStyles(customizationSerivce):
    customizationCache = vehicles.g_cache.customization20().itemTypes
    type = CustomizationType.STYLE
    result = []
    for itemID in customizationCache[type]:
        intCD = vehicles.makeIntCompactDescrByID('customizationItem', type, itemID)
        item = customizationSerivce.getItemByCD(intCD)
        if item.is3D and not item.isHiddenInUI():
            result.append(item)

    return result
