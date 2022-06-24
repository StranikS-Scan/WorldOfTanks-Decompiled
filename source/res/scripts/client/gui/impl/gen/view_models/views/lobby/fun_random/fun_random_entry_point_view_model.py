# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/fun_random/fun_random_entry_point_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class State(IntEnum):
    ACTIVE = 1
    NOTPRIMETIME = 2


class FunRandomEntryPointViewModel(ViewModel):
    __slots__ = ('onActionClick',)

    def __init__(self, properties=3, commands=1):
        super(FunRandomEntryPointViewModel, self).__init__(properties=properties, commands=commands)

    def getEndTime(self):
        return self._getNumber(0)

    def setEndTime(self, value):
        self._setNumber(0, value)

    def getLeftTime(self):
        return self._getNumber(1)

    def setLeftTime(self, value):
        self._setNumber(1, value)

    def getState(self):
        return State(self._getNumber(2))

    def setState(self, value):
        self._setNumber(2, value.value)

    def _initialize(self):
        super(FunRandomEntryPointViewModel, self)._initialize()
        self._addNumberProperty('endTime', -1)
        self._addNumberProperty('leftTime', -1)
        self._addNumberProperty('state')
        self.onActionClick = self._addCommand('onActionClick')
