# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/views/battle_royale_entry_point_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class State(Enum):
    ACTIVE = 'active'
    DISABLED = 'disabled'
    POSTEVENT = 'postevent'


class BattleRoyaleEntryPointModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=3, commands=1):
        super(BattleRoyaleEntryPointModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getTimestamp(self):
        return self._getNumber(1)

    def setTimestamp(self, value):
        self._setNumber(1, value)

    def getIsSingle(self):
        return self._getBool(2)

    def setIsSingle(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(BattleRoyaleEntryPointModel, self)._initialize()
        self._addStringProperty('state', State.ACTIVE.value)
        self._addNumberProperty('timestamp', 0)
        self._addBoolProperty('isSingle', True)
        self.onClick = self._addCommand('onClick')
