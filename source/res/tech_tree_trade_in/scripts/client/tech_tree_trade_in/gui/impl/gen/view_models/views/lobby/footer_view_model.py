# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/gen/view_models/views/lobby/footer_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.price_model import PriceModel

class FooterState(IntEnum):
    NO_PRICE = 0
    BASIC_PRICE = 1
    COMPOUND_PRICE = 2
    UPDATING = 3


class FooterViewModel(ViewModel):
    __slots__ = ('onConfirm',)

    def __init__(self, properties=2, commands=1):
        super(FooterViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return PriceModel

    def getState(self):
        return FooterState(self._getNumber(1))

    def setState(self, value):
        self._setNumber(1, value.value)

    def _initialize(self):
        super(FooterViewModel, self)._initialize()
        self._addViewModelProperty('price', PriceModel())
        self._addNumberProperty('state', FooterState.NO_PRICE.value)
        self.onConfirm = self._addCommand('onConfirm')
