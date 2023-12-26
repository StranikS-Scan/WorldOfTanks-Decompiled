# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_navigation_helper.py
from adisp import adisp_process, isAsync
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents, CameraMovementStates
from gui.impl.new_year.navigation import NewYearNavigation
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showLootBoxEntry
from gui.shared.events import LobbySimpleEvent
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace

def switchNewYearView(objectName, aliasName=None, executeBeforeSwitch=None, **kwargs):
    _kwargs = {'forceShowMainView': True}
    _kwargs.update(kwargs)
    ctx = {'objectName': objectName,
     'viewAlias': aliasName,
     'executeBeforeSwitch': executeBeforeSwitch,
     'kwargs': _kwargs}
    g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.SWITCH_NEW_YEAR_VIEW, ctx), EVENT_BUS_SCOPE.LOBBY)


def showLootBox(lootBoxType, category=''):
    ctx = {'lootBoxType': lootBoxType,
     'category': category}
    g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.SHOW_LOOT_BOX_VIEW, ctx), EVENT_BUS_SCOPE.LOBBY)


class NewYearNavigationHelper(object):
    hangarSpace = dependency.descriptor(IHangarSpace)

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
    @adisp_process
    def __onSwitchEvent(event):
        ctx = event.ctx
        objectName = ctx.get('objectName')
        aliasName = ctx.get('viewAlias')
        executeBeforeSwitch = ctx.get('executeBeforeSwitch')
        kwargs = ctx.get('kwargs', {})
        if objectName:
            if executeBeforeSwitch:
                if isAsync(executeBeforeSwitch):
                    execRes = yield executeBeforeSwitch()
                else:
                    execRes = executeBeforeSwitch()
                if not execRes:
                    return
            NewYearNavigation.switchTo(objectName=objectName, viewAlias=aliasName, **kwargs)

    @staticmethod
    def __onShowLootBox(event):
        category = event.ctx.get('category')
        lootBoxType = event.ctx.get('lootBoxType')
        if lootBoxType:
            showLootBoxEntry(lootBoxType=lootBoxType, category=category)

    @classmethod
    def __onCameraEntityUpdated(cls, event):
        ctx = event.ctx
        state = ctx['state']
        if state == CameraMovementStates.MOVING_TO_OBJECT:
            if NewYearNavigation.getCurrentObject():
                NewYearNavigation.closeMainView()
