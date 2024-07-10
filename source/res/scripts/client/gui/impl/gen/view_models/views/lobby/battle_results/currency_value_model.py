# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/currency_value_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class ValueModifiers(Enum):
    UNDEFINED = 'undefined'
    MUL = 'mul'
    ADD = 'add'
    SUB = 'sub'
    PROCENT = 'procent'
    SHOW_NEGATIVE_IMPACT = 'showNegativeImpact'


class CurrencyValueModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(CurrencyValueModel, self).__init__(properties=properties, commands=commands)

    def getCurrencyType(self):
        return self._getString(0)

    def setCurrencyType(self, value):
        self._setString(0, value)

    def getValue(self):
        return self._getReal(1)

    def setValue(self, value):
        self._setReal(1, value)

    def getIsShown(self):
        return self._getBool(2)

    def setIsShown(self, value):
        self._setBool(2, value)

    def getModifiers(self):
        return self._getArray(3)

    def setModifiers(self, value):
        self._setArray(3, value)

    @staticmethod
    def getModifiersType():
        return ValueModifiers

    def _initialize(self):
        super(CurrencyValueModel, self)._initialize()
        self._addStringProperty('currencyType', '')
        self._addRealProperty('value', 0.0)
        self._addBoolProperty('isShown', False)
        self._addArrayProperty('modifiers', Array())
