# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/components/CalendarComponent.py
from debug_utils import LOG_DEBUG
import BigWorld
from Event import Event, EventManager
from gui.Scaleform.daapi.view.meta.CalendarMeta import CalendarMeta

class CalendarComponent(CalendarMeta):

    def __init__(self):
        super(CalendarComponent, self).__init__()
        self.__em = EventManager()
        self.onMonthChangedEvent = Event(self.__em)
        self.onDateSelectedEvent = Event(self.__em)

    def onMonthChanged(self, timestamp):
        self.onMonthChangedEvent(timestamp)

    def onDateSelected(self, timestamp):
        self.onDateSelectedEvent(timestamp)

    def formatYMHeader(self, rawDate):
        return BigWorld.wg_getYMDateFormat(rawDate)

    def _dispose(self):
        self.__em.clear()
        super(CalendarComponent, self)._dispose()
