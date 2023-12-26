# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/notifications/receiving_rewards_model.py
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.new_year.notifications.ny_reward_notification_model import NyRewardNotificationModel
from gui.impl.gen.view_models.views.lobby.notifications.notification_model import NotificationModel

class ReceivingRewardsModel(NotificationModel):
    __slots__ = ('onClick', 'onStylePreview', 'onGoToRewards', 'onRecruit')

    def __init__(self, properties=5, commands=4):
        super(ReceivingRewardsModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewards(self):
        return self._getViewModel(1)

    @staticmethod
    def getRewardsType():
        return NyRewardNotificationModel

    @property
    def hugeRewards(self):
        return self._getViewModel(2)

    @staticmethod
    def getHugeRewardsType():
        return NyRewardNotificationModel

    def getIsButtonDisabled(self):
        return self._getBool(3)

    def setIsButtonDisabled(self, value):
        self._setBool(3, value)

    def getLevel(self):
        return self._getNumber(4)

    def setLevel(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(ReceivingRewardsModel, self)._initialize()
        self._addViewModelProperty('rewards', UserListModel())
        self._addViewModelProperty('hugeRewards', UserListModel())
        self._addBoolProperty('isButtonDisabled', False)
        self._addNumberProperty('level', 0)
        self.onClick = self._addCommand('onClick')
        self.onStylePreview = self._addCommand('onStylePreview')
        self.onGoToRewards = self._addCommand('onGoToRewards')
        self.onRecruit = self._addCommand('onRecruit')
