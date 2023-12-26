# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/notifications/ny_piggy_bank_single_reward_model.py
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.new_year.notifications.ny_reward_notification_model import NyRewardNotificationModel
from gui.impl.gen.view_models.views.lobby.notifications.notification_model import NotificationModel

class NyPiggyBankSingleRewardModel(NotificationModel):
    __slots__ = ('onStylePreview', 'onGoToFriends')

    def __init__(self, properties=4, commands=2):
        super(NyPiggyBankSingleRewardModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewards(self):
        return self._getViewModel(1)

    @staticmethod
    def getRewardsType():
        return NyRewardNotificationModel

    def getIsButtonDisabled(self):
        return self._getBool(2)

    def setIsButtonDisabled(self, value):
        self._setBool(2, value)

    def getIsStyle(self):
        return self._getBool(3)

    def setIsStyle(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(NyPiggyBankSingleRewardModel, self)._initialize()
        self._addViewModelProperty('rewards', UserListModel())
        self._addBoolProperty('isButtonDisabled', False)
        self._addBoolProperty('isStyle', False)
        self.onStylePreview = self._addCommand('onStylePreview')
        self.onGoToFriends = self._addCommand('onGoToFriends')
