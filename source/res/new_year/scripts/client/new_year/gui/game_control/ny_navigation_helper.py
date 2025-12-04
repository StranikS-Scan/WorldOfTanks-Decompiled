# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/game_control/ny_navigation_helper.py
from skeletons.gui.shared.utils import IHangarSpace
from helpers import dependency
from new_year.gui.impl.new_year.navigation import NewYearNavigation
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from new_year.gui.shared.event_dispatcher import showLootBoxEntry
from gui.shared.events import LobbySimpleEvent

def switchNewYearView(anchorName, aliasName=None):
    kwargs = {'forceShowMainView': True}
    ctx = {'anchorName': anchorName,
     'viewAlias': aliasName,
     'instantly': True,
     'kwargs': kwargs}
    g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.SWITCH_NEW_YEAR_VIEW, ctx), EVENT_BUS_SCOPE.LOBBY)


def showLootBox(lootBoxType, category=''):
    ctx = {'lootBoxType': lootBoxType,
     'category': category}
    g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.SHOW_LOOT_BOX_VIEW, ctx), EVENT_BUS_SCOPE.LOBBY)


def _externalSwitchToViewWithCtx(ctx, *args, **kwargs):
    ctx.update({'anchordAsObject': True,
     'instantly': True,
     'args': args,
     'kwargs': kwargs})
    g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.SWITCH_NEW_YEAR_VIEW, ctx), EVENT_BUS_SCOPE.LOBBY)


class NewYearNavigationHelper(object):
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def onLobbyInited(self):
        g_eventBus.addListener(LobbySimpleEvent.SWITCH_NEW_YEAR_VIEW, self.__onSwitchEvent, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(LobbySimpleEvent.SHOW_LOOT_BOX_VIEW, self.__onShowLootBox, EVENT_BUS_SCOPE.LOBBY)
        self.__hangarSpace.onHeroTankReady += self.__onHeroTankReady

    def clear(self):
        g_eventBus.removeListener(LobbySimpleEvent.SWITCH_NEW_YEAR_VIEW, self.__onSwitchEvent, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(LobbySimpleEvent.SHOW_LOOT_BOX_VIEW, self.__onShowLootBox, EVENT_BUS_SCOPE.LOBBY)
        self.__hangarSpace.onHeroTankReady -= self.__onHeroTankReady
        NewYearNavigation.clear()

    @staticmethod
    def __onSwitchEvent(event):
        ctx = event.ctx
        anchorName = ctx.get('anchorName')
        aliasName = ctx.get('viewAlias')
        anchordAsObject = ctx.get('anchordAsObject', False)
        if anchorName:
            if anchordAsObject:
                instantly = ctx.get('instantly', False)
                args = ctx.get('args')
                kwargs = ctx.get('kwargs')
                NewYearNavigation.showMainView(anchorName, viewAlias=aliasName, instantly=instantly, *args, **kwargs)
            else:
                NewYearNavigation.switchByAnchorName(anchorName)

    @staticmethod
    def __onShowLootBox(event):
        category = event.ctx.get('category')
        lootBoxType = event.ctx.get('lootBoxType')
        if lootBoxType:
            showLootBoxEntry(lootBoxType=lootBoxType, category=category)

    def __onHeroTankReady(self):
        NewYearNavigation.onHeroTankReady()
