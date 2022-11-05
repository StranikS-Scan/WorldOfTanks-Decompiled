# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/special_currency_model.py
from frameworks.wulf import ViewModel

class SpecialCurrencyModel(ViewModel):
    __slots__ = ('onGetMoreCurrency',)

    def __init__(self, properties=2, commands=1):
        super(SpecialCurrencyModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getValue(self):
        return self._getReal(1)

    def setValue(self, value):
        self._setReal(1, value)

    def _initialize(self):
        super(SpecialCurrencyModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addRealProperty('value', 0.0)
        self.onGetMoreCurrency = self._addCommand('onGetMoreCurrency')
