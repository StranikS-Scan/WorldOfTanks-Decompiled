# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/page/header/user_account_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.page.header.subscriptions_model import SubscriptionsModel
from gui.impl.gen.view_models.views.lobby.page.header.user_info_model import UserInfoModel

class UserAccountModel(ViewModel):
    __slots__ = ('onOpenAccountDashboard',)

    def __init__(self, properties=2, commands=1):
        super(UserAccountModel, self).__init__(properties=properties, commands=commands)

    @property
    def userInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getUserInfoType():
        return UserInfoModel

    @property
    def subscriptions(self):
        return self._getViewModel(1)

    @staticmethod
    def getSubscriptionsType():
        return SubscriptionsModel

    def _initialize(self):
        super(UserAccountModel, self)._initialize()
        self._addViewModelProperty('userInfo', UserInfoModel())
        self._addViewModelProperty('subscriptions', SubscriptionsModel())
        self.onOpenAccountDashboard = self._addCommand('onOpenAccountDashboard')
