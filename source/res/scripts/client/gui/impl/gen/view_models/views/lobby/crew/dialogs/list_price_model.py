# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/list_price_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.dialogs.dialog_template_generic_tooltip_view_model import DialogTemplateGenericTooltipViewModel
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencyViewModel

class ListPriceModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ListPriceModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return CurrencyViewModel

    @property
    def priceTooltip(self):
        return self._getViewModel(1)

    @staticmethod
    def getPriceTooltipType():
        return DialogTemplateGenericTooltipViewModel

    def getKwargs(self):
        return self._getString(2)

    def setKwargs(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(ListPriceModel, self)._initialize()
        self._addViewModelProperty('price', CurrencyViewModel())
        self._addViewModelProperty('priceTooltip', DialogTemplateGenericTooltipViewModel())
        self._addStringProperty('kwargs', '')
