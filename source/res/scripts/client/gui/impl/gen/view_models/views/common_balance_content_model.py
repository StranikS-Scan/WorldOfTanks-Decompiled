# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/common_balance_content_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel

class CommonBalanceContentModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(CommonBalanceContentModel, self).__init__(properties=properties, commands=commands)

    @property
    def currency(self):
        return self._getViewModel(0)

    @staticmethod
    def getCurrencyType():
        return UserListModel

    def _initialize(self):
        super(CommonBalanceContentModel, self)._initialize()
        self._addViewModelProperty('currency', UserListModel())
