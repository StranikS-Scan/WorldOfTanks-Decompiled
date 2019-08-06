# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableAdventCalendarHangarObject.py
from ClientSelectableObject import ClientSelectableObject
from gui.game_control import CalendarInvokeOrigin
from helpers import dependency
from skeletons.gui.game_control import ICalendarController

class ClientSelectableAdventCalendarHangarObject(ClientSelectableObject):
    __calendarController = dependency.descriptor(ICalendarController)

    def onMouseClick(self):
        super(ClientSelectableAdventCalendarHangarObject, self).onMouseClick()
        self.__calendarController.showWindow(invokedFrom=CalendarInvokeOrigin.ACTION)
