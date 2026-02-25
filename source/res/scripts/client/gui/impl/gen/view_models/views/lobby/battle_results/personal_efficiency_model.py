# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/personal_efficiency_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class ValueType(IntEnum):
    INTEGER = 0
    TIME = 1
    NON_NEGATIVE_INTEGER = 2


class PersonalEfficiencyModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(PersonalEfficiencyModel, self).__init__(properties=properties, commands=commands)

    def getParamType(self):
        return self._getString(0)

    def setParamType(self, value):
        self._setString(0, value)

    def getValue(self):
        return self._getReal(1)

    def setValue(self, value):
        self._setReal(1, value)

    def getValueType(self):
        return ValueType(self._getNumber(2))

    def setValueType(self, value):
        self._setNumber(2, value.value)

    def _initialize(self):
        super(PersonalEfficiencyModel, self)._initialize()
        self._addStringProperty('paramType', '')
        self._addRealProperty('value', 0.0)
        self._addNumberProperty('valueType', ValueType.INTEGER.value)
