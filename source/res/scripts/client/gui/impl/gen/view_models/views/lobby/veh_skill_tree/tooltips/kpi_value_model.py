# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/veh_skill_tree/tooltips/kpi_value_model.py
from frameworks.wulf import ViewModel

class KpiValueModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(KpiValueModel, self).__init__(properties=properties, commands=commands)

    def getBaseValue(self):
        return self._getReal(0)

    def setBaseValue(self, value):
        self._setReal(0, value)

    def getValueKey(self):
        return self._getString(1)

    def setValueKey(self, value):
        self._setString(1, value)

    def getValue(self):
        return self._getReal(2)

    def setValue(self, value):
        self._setReal(2, value)

    def getValueType(self):
        return self._getString(3)

    def setValueType(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(KpiValueModel, self)._initialize()
        self._addRealProperty('baseValue', 0.0)
        self._addStringProperty('valueKey', '')
        self._addRealProperty('value', 0.0)
        self._addStringProperty('valueType', 'mul')
