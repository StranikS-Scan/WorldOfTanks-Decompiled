# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_navigation_helper.py
from gui.impl.new_year.navigation import NewYearNavigation
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showLootBoxEntry
from gui.shared.events import LobbySimpleEvent

def switchNewYearView(anchorName, aliasName=None):
    ctx = {'anchorName': anchorName,
     'viewAlias': aliasName}
    g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.SWITCH_NEW_YEAR_VIEW, ctx), EVENT_BUS_SCOPE.LOBBY)


def showLootBox(lootBoxType, category):
    ctx = {'lootBoxType': lootBoxType,
     'category': category}
    g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.SHOW_LOOT_BOX_VIEW, ctx), EVENT_BUS_SCOPE.LOBBY)


class NewYearNavigationHelper(object):

    def onLobbyInited(self):
        g_eventBus.addListener(LobbySimpleEvent.SWITCH_NEW_YEAR_VIEW, self.__onSwitchEvent, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(LobbySimpleEvent.SHOW_LOOT_BOX_VIEW, self.__onShowLootBox, EVENT_BUS_SCOPE.LOBBY)

    def clear(self):
        g_eventBus.removeListener(LobbySimpleEvent.SWITCH_NEW_YEAR_VIEW, self.__onSwitchEvent, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(LobbySimpleEvent.SHOW_LOOT_BOX_VIEW, self.__onShowLootBox, EVENT_BUS_SCOPE.LOBBY)

    @staticmethod
    def __onSwitchEvent(event):
        anchorName = event.ctx.get('anchorName')
        aliasName = event.ctx.get('viewAlias')
        if anchorName:
            NewYearNavigation.switchByAnchorName(anchorName, aliasName)

    @staticmethod
    def __onShowLootBox(event):
        category = event.ctx.get('category')
        lootBoxType = event.ctx.get('lootBoxType')
        if lootBoxType:
            showLootBoxEntry(lootBoxType=lootBoxType, category=category)
