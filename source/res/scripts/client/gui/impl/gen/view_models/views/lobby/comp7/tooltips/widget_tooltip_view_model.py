# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/tooltips/widget_tooltip_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class ProgressionState(Enum):
    COMPLETED = 'completed'
    IN_PROGRESS = 'inProgress'


class WidgetTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(WidgetTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getProgressionState(self):
        return ProgressionState(self._getString(0))

    def setProgressionState(self, value):
        self._setString(0, value.value)

    def getTime(self):
        return self._getNumber(1)

    def setTime(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(WidgetTooltipViewModel, self)._initialize()
        self._addStringProperty('progressionState', ProgressionState.IN_PROGRESS.value)
        self._addNumberProperty('time', 0)
