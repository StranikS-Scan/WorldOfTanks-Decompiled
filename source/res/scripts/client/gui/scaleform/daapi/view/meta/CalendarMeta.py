# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CalendarMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class CalendarMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def onMonthChanged(self, rawDate):
        """
        :param rawDate:
        :return :
        """
        self._printOverrideError('onMonthChanged')

    def onDateSelected(self, rawDate):
        """
        :param rawDate:
        :return :
        """
        self._printOverrideError('onDateSelected')

    def formatYMHeader(self, rawDate):
        """
        :param rawDate:
        :return String:
        """
        self._printOverrideError('formatYMHeader')

    def as_openMonthS(self, rawDate):
        """
        :param rawDate:
        :return :
        """
        return self.flashObject.as_openMonth(rawDate) if self._isDAAPIInited() else None

    def as_selectDateS(self, rawDate):
        """
        :param rawDate:
        :return :
        """
        return self.flashObject.as_selectDate(rawDate) if self._isDAAPIInited() else None

    def as_updateMonthEventsS(self, items):
        """
        :param items:
        :return :
        """
        return self.flashObject.as_updateMonthEvents(items) if self._isDAAPIInited() else None

    def as_setCalendarMessageS(self, message):
        """
        :param message:
        :return :
        """
        return self.flashObject.as_setCalendarMessage(message) if self._isDAAPIInited() else None

    def as_setMinAvailableDateS(self, rawDate):
        """
        :param rawDate:
        :return :
        """
        return self.flashObject.as_setMinAvailableDate(rawDate) if self._isDAAPIInited() else None

    def as_setMaxAvailableDateS(self, rawDate):
        """
        :param rawDate:
        :return :
        """
        return self.flashObject.as_setMaxAvailableDate(rawDate) if self._isDAAPIInited() else None
