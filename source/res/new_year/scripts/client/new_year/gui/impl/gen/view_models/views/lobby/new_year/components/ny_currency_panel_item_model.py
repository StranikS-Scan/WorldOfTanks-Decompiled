# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/components/ny_currency_panel_item_model.py
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.common.ny_currency_type_model import NyCurrencyTypeModel

class NyCurrencyPanelItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(NyCurrencyPanelItemModel, self).__init__(properties=properties, commands=commands)

    @property
    def currency(self):
        return self._getViewModel(0)

    @staticmethod
    def getCurrencyType():
        return NyCurrencyTypeModel

    def getAmount(self):
        return self._getNumber(1)

    def setAmount(self, value):
        self._setNumber(1, value)

    def getAllowClick(self):
        return self._getBool(2)

    def setAllowClick(self, value):
        self._setBool(2, value)

    def getIsCurrencyAvailable(self):
        return self._getBool(3)

    def setIsCurrencyAvailable(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(NyCurrencyPanelItemModel, self)._initialize()
        self._addViewModelProperty('currency', NyCurrencyTypeModel())
        self._addNumberProperty('amount', 0)
        self._addBoolProperty('allowClick', False)
        self._addBoolProperty('isCurrencyAvailable', True)
