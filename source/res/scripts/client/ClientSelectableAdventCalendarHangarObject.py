# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableAdventCalendarHangarObject.py
from ClientSelectableObject import ClientSelectableObject
from gui.game_control import CalendarInvokeOrigin
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.game_control import ICalendarController

class ClientSelectableAdventCalendarHangarObject(ClientSelectableObject):
    __calendarController = dependency.descriptor(ICalendarController)

    def onMouseClick(self):
        super(ClientSelectableAdventCalendarHangarObject, self).onMouseClick()
        self.__calendarController.showWindow(invokedFrom=CalendarInvokeOrigin.ACTION)

    def onEnterWorld(self, preReq):
        super(ClientSelectableAdventCalendarHangarObject, self).onEnterWorld(preReq)
        self.__dispatchEvent(events.AdventCalendarEvent.ADVENT_CALENDAR_OBJECT_ENTER)

    def onLeaveWorld(self):
        self.__dispatchEvent(events.AdventCalendarEvent.ADVENT_CALENDAR_OBJECT_LEAVE)
        super(ClientSelectableAdventCalendarHangarObject, self).onLeaveWorld()

    @staticmethod
    def __dispatchEvent(eventType):
        g_eventBus.handleEvent(events.AdventCalendarEvent(eventType), scope=EVENT_BUS_SCOPE.LOBBY)
