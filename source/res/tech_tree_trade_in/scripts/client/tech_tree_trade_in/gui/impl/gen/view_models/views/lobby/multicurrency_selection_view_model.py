# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/gen/view_models/views/lobby/multicurrency_selection_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.base_currency_info_view_model import BaseCurrencyInfoViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.resource_info_view_model import ResourceInfoViewModel

class MulticurrencySelectionViewModel(ViewModel):
    __slots__ = ('onConfirm',)

    def __init__(self, properties=2, commands=1):
        super(MulticurrencySelectionViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def baseCurrency(self):
        return self._getViewModel(0)

    @staticmethod
    def getBaseCurrencyType():
        return BaseCurrencyInfoViewModel

    def getResources(self):
        return self._getArray(1)

    def setResources(self, value):
        self._setArray(1, value)

    @staticmethod
    def getResourcesType():
        return ResourceInfoViewModel

    def _initialize(self):
        super(MulticurrencySelectionViewModel, self)._initialize()
        self._addViewModelProperty('baseCurrency', BaseCurrencyInfoViewModel())
        self._addArrayProperty('resources', Array())
        self.onConfirm = self._addCommand('onConfirm')
