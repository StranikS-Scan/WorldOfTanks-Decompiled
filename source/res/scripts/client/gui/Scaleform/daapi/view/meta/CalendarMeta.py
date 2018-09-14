# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CalendarMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class CalendarMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    """

    def onMonthChanged(self, rawDate):
        self._printOverrideError('onMonthChanged')

    def onDateSelected(self, rawDate):
        self._printOverrideError('onDateSelected')

    def formatYMHeader(self, rawDate):
        self._printOverrideError('formatYMHeader')

    def as_openMonthS(self, rawDate):
        return self.flashObject.as_openMonth(rawDate) if self._isDAAPIInited() else None

    def as_selectDateS(self, rawDate):
        return self.flashObject.as_selectDate(rawDate) if self._isDAAPIInited() else None

    def as_updateMonthEventsS(self, items):
        return self.flashObject.as_updateMonthEvents(items) if self._isDAAPIInited() else None

    def as_setCalendarMessageS(self, message):
        return self.flashObject.as_setCalendarMessage(message) if self._isDAAPIInited() else None

    def as_setMinAvailableDateS(self, rawDate):
        return self.flashObject.as_setMinAvailableDate(rawDate) if self._isDAAPIInited() else None

    def as_setMaxAvailableDateS(self, rawDate):
        return self.flashObject.as_setMaxAvailableDate(rawDate) if self._isDAAPIInited() else None
