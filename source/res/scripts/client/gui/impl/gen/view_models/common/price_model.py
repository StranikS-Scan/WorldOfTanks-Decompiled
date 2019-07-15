# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/price_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel

class PriceModel(ViewModel):
    __slots__ = ()

    @property
    def price(self):
        return self._getViewModel(0)

    @property
    def defPrice(self):
        return self._getViewModel(1)

    @property
    def discount(self):
        return self._getViewModel(2)

    def _initialize(self):
        super(PriceModel, self)._initialize()
        self._addViewModelProperty('price', UserListModel())
        self._addViewModelProperty('defPrice', UserListModel())
        self._addViewModelProperty('discount', UserListModel())
