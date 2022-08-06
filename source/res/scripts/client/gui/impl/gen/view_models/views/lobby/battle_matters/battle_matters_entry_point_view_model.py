# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_matters/battle_matters_entry_point_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class State(IntEnum):
    NORMAL = 0
    HASTOKEN = 1
    ERROR = 2


class BattleMattersEntryPointViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=5, commands=1):
        super(BattleMattersEntryPointViewModel, self).__init__(properties=properties, commands=commands)

    def getCurrentProgress(self):
        return self._getNumber(0)

    def setCurrentProgress(self, value):
        self._setNumber(0, value)

    def getMaxProgress(self):
        return self._getNumber(1)

    def setMaxProgress(self, value):
        self._setNumber(1, value)

    def getQuestNumber(self):
        return self._getNumber(2)

    def setQuestNumber(self, value):
        self._setNumber(2, value)

    def getIsCompleted(self):
        return self._getBool(3)

    def setIsCompleted(self, value):
        self._setBool(3, value)

    def getState(self):
        return State(self._getNumber(4))

    def setState(self, value):
        self._setNumber(4, value.value)

    def _initialize(self):
        super(BattleMattersEntryPointViewModel, self)._initialize()
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('maxProgress', 0)
        self._addNumberProperty('questNumber', 0)
        self._addBoolProperty('isCompleted', False)
        self._addNumberProperty('state')
        self.onClick = self._addCommand('onClick')
