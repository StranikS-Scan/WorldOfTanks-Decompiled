# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/dialogs/sub_views/select_money_view_model.py
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencyViewModel
from gui.impl.gen.view_models.views.dialogs.sub_views.select_option_base_item_view_model import SelectOptionBaseItemViewModel

class SelectMoneyViewModel(SelectOptionBaseItemViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(SelectMoneyViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def cost(self):
        return self._getViewModel(4)

    @staticmethod
    def getCostType():
        return CurrencyViewModel

    def _initialize(self):
        super(SelectMoneyViewModel, self)._initialize()
        self._addViewModelProperty('cost', CurrencyViewModel())
