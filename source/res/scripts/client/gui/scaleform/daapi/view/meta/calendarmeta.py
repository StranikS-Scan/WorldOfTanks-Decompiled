# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CalendarMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class CalendarMeta(BaseDAAPIComponent):

    def onMonthChanged(self, rawDate):
        self._printOverrideError('onMonthChanged')

    def onDateSelected(self, rawDate):
        self._printOverrideError('onDateSelected')

    def formatYMHeader(self, rawDate):
        self._printOverrideError('formatYMHeader')

    def as_openMonthS(self, rawDate):
        if self._isDAAPIInited():
            return self.flashObject.as_openMonth(rawDate)

    def as_selectDateS(self, rawDate):
        if self._isDAAPIInited():
            return self.flashObject.as_selectDate(rawDate)

    def as_updateMonthEventsS(self, items):
        if self._isDAAPIInited():
            return self.flashObject.as_updateMonthEvents(items)

    def as_setCalendarMessageS(self, message):
        if self._isDAAPIInited():
            return self.flashObject.as_setCalendarMessage(message)

    def as_setMinAvailableDateS(self, rawDate):
        if self._isDAAPIInited():
            return self.flashObject.as_setMinAvailableDate(rawDate)

    def as_setMaxAvailableDateS(self, rawDate):
        if self._isDAAPIInited():
            return self.flashObject.as_setMaxAvailableDate(rawDate)
