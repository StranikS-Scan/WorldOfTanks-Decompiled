# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/feature/fun_random_entry_point_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class State(IntEnum):
    BEFORE = 0
    ACTIVE = 1
    NOTPRIMETIME = 2
    AFTER = 3


class FunRandomEntryPointViewModel(ViewModel):
    __slots__ = ('onActionClick',)

    def __init__(self, properties=4, commands=1):
        super(FunRandomEntryPointViewModel, self).__init__(properties=properties, commands=commands)

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

    def _initialize(self):
        super(FunRandomEntryPointViewModel, self)._initialize()
        self._addNumberProperty('startTime', -1)
        self._addNumberProperty('endTime', -1)
        self._addNumberProperty('leftTime', -1)
        self._addNumberProperty('state')
        self.onActionClick = self._addCommand('onActionClick')
