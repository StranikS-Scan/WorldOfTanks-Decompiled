# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/common_balance_content_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel

class CommonBalanceContentModel(ViewModel):
    __slots__ = ()

    @property
    def currency(self):
        return self._getViewModel(0)

    def _initialize(self):
        super(CommonBalanceContentModel, self)._initialize()
        self._addViewModelProperty('currency', UserListModel())
