# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/price_item_model.py
from frameworks.wulf import ViewModel

class PriceItemModel(ViewModel):
    __slots__ = ()

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getValue(self):
        return self._getReal(1)

    def setValue(self, value):
        self._setReal(1, value)

    def _initialize(self):
        super(PriceItemModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addRealProperty('value', 0.0)
