# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/stronghold/stronghold_entry_point_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class State(IntEnum):
    NOTSTARTED = 0
    PRIMETIMENOW = 1
    PRIMETIMETODAY = 2
    PRIMETIMETOMORROW = 3
    PRIMETIMENOTCHOSEN = 4
    STARTED = 5
    ENDED = 6
    DATAERROR = 7


class StrongholdEntryPointViewModel(ViewModel):
    __slots__ = ('onOpen',)

    def __init__(self, properties=4, commands=1):
        super(StrongholdEntryPointViewModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getNumber(0))

    def setState(self, value):
        self._setNumber(0, value.value)

    def getIsSingle(self):
        return self._getBool(1)

    def setIsSingle(self, value):
        self._setBool(1, value)

    def getStartTimestamp(self):
        return self._getNumber(2)

    def setStartTimestamp(self, value):
        self._setNumber(2, value)

    def getEndTimestamp(self):
        return self._getNumber(3)

    def setEndTimestamp(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(StrongholdEntryPointViewModel, self)._initialize()
        self._addNumberProperty('state')
        self._addBoolProperty('isSingle', True)
        self._addNumberProperty('startTimestamp', 0)
        self._addNumberProperty('endTimestamp', 0)
        self.onOpen = self._addCommand('onOpen')
