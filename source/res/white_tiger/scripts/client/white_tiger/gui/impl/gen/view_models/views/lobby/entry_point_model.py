# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/entry_point_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class State(Enum):
    ACTIVE = 'active'
    LOCKED = 'locked'
    BATTLES_END = 'battlesEnd'


class EntryPointModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=4, commands=1):
        super(EntryPointModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getTimeLeft(self):
        return self._getNumber(1)

    def setTimeLeft(self, value):
        self._setNumber(1, value)

    def getHunterLootBoxesCount(self):
        return self._getNumber(2)

    def setHunterLootBoxesCount(self, value):
        self._setNumber(2, value)

    def getBossLootBoxesCount(self):
        return self._getNumber(3)

    def setBossLootBoxesCount(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(EntryPointModel, self)._initialize()
        self._addStringProperty('state')
        self._addNumberProperty('timeLeft', 0)
        self._addNumberProperty('hunterLootBoxesCount', 0)
        self._addNumberProperty('bossLootBoxesCount', 0)
        self.onClick = self._addCommand('onClick')
