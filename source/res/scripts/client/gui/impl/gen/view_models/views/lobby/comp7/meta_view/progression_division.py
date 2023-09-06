# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/meta_view/progression_division.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class Division(IntEnum):
    A = 1
    B = 2
    C = 3
    D = 4
    E = 5


class State(IntEnum):
    ACHIEVED = 0
    CURRENT = 1
    INACTIVE = 2


class ProgressionDivision(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(ProgressionDivision, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return Division(self._getNumber(0))

    def setName(self, value):
        self._setNumber(0, value.value)

    def getState(self):
        return State(self._getNumber(1))

    def setState(self, value):
        self._setNumber(1, value.value)

    def _initialize(self):
        super(ProgressionDivision, self)._initialize()
        self._addNumberProperty('name')
        self._addNumberProperty('state')
