# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/year_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class YearState(IntEnum):
    NOTSTARTED = 0
    ACTIVE = 1
    OFFSEASON = 3
    FINISHED = 4


class YearModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(YearModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return YearState(self._getNumber(0))

    def setState(self, value):
        self._setNumber(0, value.value)

    def _initialize(self):
        super(YearModel, self)._initialize()
        self._addNumberProperty('state')
