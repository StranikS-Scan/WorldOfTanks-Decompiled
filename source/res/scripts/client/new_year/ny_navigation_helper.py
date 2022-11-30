# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_navigation_helper.py
from gui.impl.new_year.navigation import NewYearNavigation
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showLootBoxEntry
from gui.shared.events import LobbySimpleEvent
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents, CameraMovementStates

def switchNewYearView(anchorName, aliasName=None, **kwargs):
    _kwargs = {'forceShowMainView': True}
    _kwargs.update(kwargs)
    ctx = {'anchorName': anchorName,
     'viewAlias': aliasName,
     'instantly': True,
     'kwargs': _kwargs}
    g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.SWITCH_NEW_YEAR_VIEW, ctx), EVENT_BUS_SCOPE.LOBBY)


def showLootBox(lootBoxType, category=''):
    ctx = {'lootBoxType': lootBoxType,
     'category': category}
    g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.SHOW_LOOT_BOX_VIEW, ctx), EVENT_BUS_SCOPE.LOBBY)


class NewYearNavigationHelper(object):

    def onLobbyInited(self):
        g_eventBus.addListener(LobbySimpleEvent.SWITCH_NEW_YEAR_VIEW, self.__onSwitchEvent, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(LobbySimpleEvent.SHOW_LOOT_BOX_VIEW, self.__onShowLootBox, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated)

    def clear(self):
        g_eventBus.removeListener(LobbySimpleEvent.SWITCH_NEW_YEAR_VIEW, self.__onSwitchEvent, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(LobbySimpleEvent.SHOW_LOOT_BOX_VIEW, self.__onShowLootBox, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated)
        NewYearNavigation.clear()

    @staticmethod
    def __onSwitchEvent(event):
        ctx = event.ctx
        anchorName = ctx.get('anchorName')
        aliasName = ctx.get('viewAlias')
        anchordAsObject = ctx.get('anchordAsObject', False)
        kwargs = ctx.get('kwargs', {})
        if anchorName:
            if anchordAsObject:
                instantly = ctx.get('instantly', False)
                args = ctx.get('args')
                NewYearNavigation.showMainView(anchorName, viewAlias=aliasName, instantly=instantly, withFade=True, *args, **kwargs)
            else:
                NewYearNavigation.switchByAnchorName(anchorName, aliasName, **kwargs)

    @staticmethod
    def __onShowLootBox(event):
        category = event.ctx.get('category')
        lootBoxType = event.ctx.get('lootBoxType')
        if lootBoxType:
            showLootBoxEntry(lootBoxType=lootBoxType, category=category)

    @staticmethod
    def __onCameraEntityUpdated(event):
        ctx = event.ctx
        state = ctx['state']
        if state == CameraMovementStates.MOVING_TO_OBJECT:
            NewYearNavigation.closeMainView()
