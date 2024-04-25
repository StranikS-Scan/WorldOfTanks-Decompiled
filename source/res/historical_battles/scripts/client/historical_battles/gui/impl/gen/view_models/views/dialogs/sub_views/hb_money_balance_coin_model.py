# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/dialogs/sub_views/hb_money_balance_coin_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.dialogs.dialog_template_generic_tooltip_view_model import DialogTemplateGenericTooltipViewModel

class HbMoneyBalanceCoinModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(HbMoneyBalanceCoinModel, self).__init__(properties=properties, commands=commands)

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

    def getCount(self):
        return self._getNumber(2)

    def setCount(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(HbMoneyBalanceCoinModel, self)._initialize()
        self._addViewModelProperty('tooltip', DialogTemplateGenericTooltipViewModel())
        self._addStringProperty('name', '')
        self._addNumberProperty('count', 0)
