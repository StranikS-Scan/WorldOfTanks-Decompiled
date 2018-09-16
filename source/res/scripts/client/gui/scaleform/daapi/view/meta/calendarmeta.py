# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CalendarMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class CalendarMeta(BaseDAAPIComponent):

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

    def as_setMinAvailableDateS(self, rawDate):
        return self.flashObject.as_setMinAvailableDate(rawDate) if self._isDAAPIInited() else None

    def as_setMaxAvailableDateS(self, rawDate):
        return self.flashObject.as_setMaxAvailableDate(rawDate) if self._isDAAPIInited() else None

    def as_setHighlightedDaysS(self, hightlightedTimestamps):
        """
        :param hightlightedTimestamps: Represented by Array (AS)
        """
        return self.flashObject.as_setHighlightedDays(hightlightedTimestamps) if self._isDAAPIInited() else None

    def as_setDayTooltipTypeS(self, tooltipType):
        return self.flashObject.as_setDayTooltipType(tooltipType) if self._isDAAPIInited() else None
