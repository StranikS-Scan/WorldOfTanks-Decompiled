# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/ui_kit/currency_item_model.py
from frameworks.wulf import ViewModel

class CurrencyItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(CurrencyItemModel, self).__init__(properties=properties, commands=commands)

    def getValue(self):
        return self._getString(0)

    def setValue(self, value):
        self._setString(0, value)

    def getCurrency(self):
        return self._getString(1)

    def setCurrency(self, value):
        self._setString(1, value)

    def getIsEnough(self):
        return self._getBool(2)

    def setIsEnough(self, value):
        self._setBool(2, value)

    def getSpecialTooltip(self):
        return self._getString(3)

    def setSpecialTooltip(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(CurrencyItemModel, self)._initialize()
        self._addStringProperty('value', '--')
        self._addStringProperty('currency', '')
        self._addBoolProperty('isEnough', True)
        self._addStringProperty('specialTooltip', '')
