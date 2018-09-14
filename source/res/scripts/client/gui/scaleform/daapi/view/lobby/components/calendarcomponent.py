# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/components/CalendarComponent.py
from debug_utils import LOG_DEBUG
from Event import Event, EventManager
from gui.Scaleform.daapi.view.meta.CalendarMeta import CalendarMeta
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class CalendarComponent(CalendarMeta, DAAPIModule):

    def __init__(self):
        super(CalendarComponent, self).__init__()
        self.__em = EventManager()
        self.onMonthChangedEvent = Event(self.__em)
        self.onDateSelectedEvent = Event(self.__em)

    def onMonthChanged(self, timestamp):
        self.onMonthChangedEvent(timestamp)

    def onDateSelected(self, timestamp):
        self.onDateSelectedEvent(timestamp)

    def _dispose(self):
        self.__em.clear()
        super(CalendarComponent, self)._dispose()
