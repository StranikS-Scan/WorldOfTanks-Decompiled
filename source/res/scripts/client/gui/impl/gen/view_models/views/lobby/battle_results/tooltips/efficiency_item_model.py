# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/tooltips/efficiency_item_model.py
from enum import Enum
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class Unit(Enum):
    SEC = 'sec'
    COUNT = 'count'


class EfficiencyItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(EfficiencyItemModel, self).__init__(properties=properties, commands=commands)

    def getLabel(self):
        return self._getResource(0)

    def setLabel(self, value):
        self._setResource(0, value)

    def getValue(self):
        return self._getReal(1)

    def setValue(self, value):
        self._setReal(1, value)

    def getValueType(self):
        return self._getResource(2)

    def setValueType(self, value):
        self._setResource(2, value)

    def _initialize(self):
        super(EfficiencyItemModel, self)._initialize()
        self._addResourceProperty('label', R.invalid())
        self._addRealProperty('value', 0.0)
        self._addResourceProperty('valueType', R.invalid())
