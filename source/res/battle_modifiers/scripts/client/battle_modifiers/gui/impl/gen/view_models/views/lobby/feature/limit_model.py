# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/client/battle_modifiers/gui/impl/gen/view_models/views/lobby/feature/limit_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class LimitType(Enum):
    MIN = 'min'
    MAX = 'max'


class LimitModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(LimitModel, self).__init__(properties=properties, commands=commands)

    def getLimitType(self):
        return LimitType(self._getString(0))

    def setLimitType(self, value):
        self._setString(0, value.value)

    def getValue(self):
        return self._getReal(1)

    def setValue(self, value):
        self._setReal(1, value)

    def _initialize(self):
        super(LimitModel, self)._initialize()
        self._addStringProperty('limitType')
        self._addRealProperty('value', 0.0)
