# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/impl/gen/view_models/views/lobby/tooltips/widget_tooltip_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class WinbackState(Enum):
    IN_PROGRESS = 'inProgress'
    COMPLETE = 'complete'
    DISABLE = 'disable'


class WidgetTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(WidgetTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return WinbackState(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getIsTimerDisplayed(self):
        return self._getBool(1)

    def setIsTimerDisplayed(self, value):
        self._setBool(1, value)

    def getCurrentTimerDate(self):
        return self._getNumber(2)

    def setCurrentTimerDate(self, value):
        self._setNumber(2, value)

    def getProgressionName(self):
        return self._getString(3)

    def setProgressionName(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(WidgetTooltipViewModel, self)._initialize()
        self._addStringProperty('state')
        self._addBoolProperty('isTimerDisplayed', False)
        self._addNumberProperty('currentTimerDate', 0)
        self._addStringProperty('progressionName', '')
