# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/supply_params_model.py
from frameworks.wulf import ViewModel

class SupplyParamsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(SupplyParamsModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getValue(self):
        return self._getString(1)

    def setValue(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(SupplyParamsModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('value', '')
