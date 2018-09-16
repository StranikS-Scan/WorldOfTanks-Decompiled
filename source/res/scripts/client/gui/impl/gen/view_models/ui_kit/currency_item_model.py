# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/ui_kit/currency_item_model.py
from frameworks.wulf import ViewModel

class CurrencyItemModel(ViewModel):
    __slots__ = ()

    def getValue(self):
        return self._getString(0)

    def setValue(self, value):
        self._setString(0, value)

    def getCurrency(self):
        return self._getString(1)

    def setCurrency(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(CurrencyItemModel, self)._initialize()
        self._addStringProperty('value', '--')
        self._addStringProperty('currency', '')
