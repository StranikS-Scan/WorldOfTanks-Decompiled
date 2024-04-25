# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/dialogs/sub_views/exchange_coin_data_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.dialogs.dialog_template_generic_tooltip_view_model import DialogTemplateGenericTooltipViewModel

class ExchangeCoinDataModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(ExchangeCoinDataModel, self).__init__(properties=properties, commands=commands)

    @property
    def tooltip(self):
        return self._getViewModel(0)

    @staticmethod
    def getTooltipType():
        return DialogTemplateGenericTooltipViewModel

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getAmount(self):
        return self._getNumber(2)

    def setAmount(self, value):
        self._setNumber(2, value)

    def getEnabled(self):
        return self._getBool(3)

    def setEnabled(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(ExchangeCoinDataModel, self)._initialize()
        self._addViewModelProperty('tooltip', DialogTemplateGenericTooltipViewModel())
        self._addStringProperty('name', '')
        self._addNumberProperty('amount', 0)
        self._addBoolProperty('enabled', False)
