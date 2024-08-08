# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wot_anniversary/entry_point_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class State(IntEnum):
    INPROGRESS = 0
    CLAIMREWARDS = 1
    WAITQUESTS = 2
    COMPLETED = 3


class EntryPointModel(ViewModel):
    __slots__ = ('onEnterEventLobby',)

    def __init__(self, properties=2, commands=1):
        super(EntryPointModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getNumber(0))

    def setState(self, value):
        self._setNumber(0, value.value)

    def getBalance(self):
        return self._getNumber(1)

    def setBalance(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(EntryPointModel, self)._initialize()
        self._addNumberProperty('state')
        self._addNumberProperty('balance', -1)
        self.onEnterEventLobby = self._addCommand('onEnterEventLobby')
