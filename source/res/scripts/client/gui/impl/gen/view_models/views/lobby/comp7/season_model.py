# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/season_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class SeasonState(IntEnum):
    NOTSTARTED = 0
    JUSTSTARTED = 1
    ACTIVE = 2
    ENDSOON = 3
    END = 4
    DISABLED = 5


class SeasonModel(ViewModel):
    __slots__ = ('pollServerTime',)

    def __init__(self, properties=4, commands=1):
        super(SeasonModel, self).__init__(properties=properties, commands=commands)

    def getStartTimestamp(self):
        return self._getNumber(0)

    def setStartTimestamp(self, value):
        self._setNumber(0, value)

    def getEndTimestamp(self):
        return self._getNumber(1)

    def setEndTimestamp(self, value):
        self._setNumber(1, value)

    def getServerTimestamp(self):
        return self._getNumber(2)

    def setServerTimestamp(self, value):
        self._setNumber(2, value)

    def getState(self):
        return SeasonState(self._getNumber(3))

    def setState(self, value):
        self._setNumber(3, value.value)

    def _initialize(self):
        super(SeasonModel, self)._initialize()
        self._addNumberProperty('startTimestamp', 0)
        self._addNumberProperty('endTimestamp', 0)
        self._addNumberProperty('serverTimestamp', 0)
        self._addNumberProperty('state')
        self.pollServerTime = self._addCommand('pollServerTime')
