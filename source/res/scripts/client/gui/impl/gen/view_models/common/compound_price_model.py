# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/compound_price_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel

class CompoundPriceModel(ViewModel):
    __slots__ = ()

    @property
    def prices(self):
        return self._getViewModel(0)

    def _initialize(self):
        super(CompoundPriceModel, self)._initialize()
        self._addViewModelProperty('prices', UserListModel())
