# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/universal_flag/universal_flag_entry_tooltip_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class TimerIconType(Enum):
    CLOCK = 'clock'
    FLAG = 'flag'
    NONE = 'none'


class UniversalFlagEntryTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(UniversalFlagEntryTooltipModel, self).__init__(properties=properties, commands=commands)

    def getCaption(self):
        return self._getString(0)

    def setCaption(self, value):
        self._setString(0, value)

    def getDescription(self):
        return self._getString(1)

    def setDescription(self, value):
        self._setString(1, value)

    def getTimerTime(self):
        return self._getNumber(2)

    def setTimerTime(self, value):
        self._setNumber(2, value)

    def getTimerText(self):
        return self._getString(3)

    def setTimerText(self, value):
        self._setString(3, value)

    def getTimerIconType(self):
        return TimerIconType(self._getString(4))

    def setTimerIconType(self, value):
        self._setString(4, value.value)

    def getTimestamp(self):
        return self._getNumber(5)

    def setTimestamp(self, value):
        self._setNumber(5, value)

    def getTooltipBackground(self):
        return self._getString(6)

    def setTooltipBackground(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(UniversalFlagEntryTooltipModel, self)._initialize()
        self._addStringProperty('caption', '')
        self._addStringProperty('description', '')
        self._addNumberProperty('timerTime', 0)
        self._addStringProperty('timerText', '')
        self._addStringProperty('timerIconType')
        self._addNumberProperty('timestamp', 0)
        self._addStringProperty('tooltipBackground', '')
