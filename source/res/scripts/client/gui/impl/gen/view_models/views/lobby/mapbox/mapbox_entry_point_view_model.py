# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mapbox/mapbox_entry_point_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class State(IntEnum):
    UNDEFINED = 0
    BEFORE = 1
    ACTIVE = 2
    NOTPRIMETIME = 3
    AFTER = 4


class MapboxEntryPointViewModel(ViewModel):
    __slots__ = ('onActionClick',)

    def __init__(self, properties=5, commands=1):
        super(MapboxEntryPointViewModel, self).__init__(properties=properties, commands=commands)

    def getStartTime(self):
        return self._getNumber(0)

    def setStartTime(self, value):
        self._setNumber(0, value)

    def getEndTime(self):
        return self._getNumber(1)

    def setEndTime(self, value):
        self._setNumber(1, value)

    def getLeftTime(self):
        return self._getNumber(2)

    def setLeftTime(self, value):
        self._setNumber(2, value)

    def getState(self):
        return State(self._getNumber(3))

    def setState(self, value):
        self._setNumber(3, value.value)

    def getPerformanceAlertEnabled(self):
        return self._getBool(4)

    def setPerformanceAlertEnabled(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(MapboxEntryPointViewModel, self)._initialize()
        self._addNumberProperty('startTime', -1)
        self._addNumberProperty('endTime', -1)
        self._addNumberProperty('leftTime', -1)
        self._addNumberProperty('state')
        self._addBoolProperty('performanceAlertEnabled', False)
        self.onActionClick = self._addCommand('onActionClick')
