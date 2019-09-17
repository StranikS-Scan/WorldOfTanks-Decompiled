# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableMiniGamesHangarObject.py
from ClientSelectableObject import ClientSelectableObject
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showFestMiniGameOverlay
from helpers import dependency
from skeletons.festival import IFestivalController

class ClientSelectableMiniGamesHangarObject(ClientSelectableObject):
    __festController = dependency.descriptor(IFestivalController)

    @property
    def enabled(self):
        return self.__festController.isMiniGamesEnabled()

    def onMouseClick(self):
        super(ClientSelectableMiniGamesHangarObject, self).onMouseClick()
        showFestMiniGameOverlay(fromHangar=True)

    def onEnterWorld(self, preReq):
        super(ClientSelectableMiniGamesHangarObject, self).onEnterWorld(preReq)
        self.__dispatchEvent(events.MiniGamesEvent.MINI_GAMES_OBJECT_ENTER)

    def onLeaveWorld(self):
        self.__dispatchEvent(events.MiniGamesEvent.MINI_GAMES_OBJECT_LEAVE)
        super(ClientSelectableMiniGamesHangarObject, self).onLeaveWorld()

    def __dispatchEvent(self, eventType):
        g_eventBus.handleEvent(events.AdventCalendarEvent(eventType, ctx={'entity': self}), scope=EVENT_BUS_SCOPE.LOBBY)
