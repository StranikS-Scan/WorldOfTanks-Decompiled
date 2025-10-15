# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/params_ttx_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class TtxComparisonStatus(Enum):
    INCREASE = 'increase'
    DECREASE = 'decrease'
    DEFAULT = 'default'


class ParamsTtxModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ParamsTtxModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getStatus(self):
        return TtxComparisonStatus(self._getString(1))

    def setStatus(self, value):
        self._setString(1, value.value)

    def getValue(self):
        return self._getReal(2)

    def setValue(self, value):
        self._setReal(2, value)

    def _initialize(self):
        super(ParamsTtxModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('status')
        self._addRealProperty('value', 0.0)
