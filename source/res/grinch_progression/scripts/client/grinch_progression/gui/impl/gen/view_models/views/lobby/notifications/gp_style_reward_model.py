# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/impl/gen/view_models/views/lobby/notifications/gp_style_reward_model.py
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.new_year.notifications.ny_reward_notification_model import NyRewardNotificationModel
from gui.impl.gen.view_models.views.lobby.notifications.notification_model import NotificationModel

class GpStyleRewardModel(NotificationModel):
    __slots__ = ('onStylePreview',)

    def __init__(self, properties=3, commands=1):
        super(GpStyleRewardModel, self).__init__(properties=properties, commands=commands)

    @property
    def hugeRewards(self):
        return self._getViewModel(1)

    @staticmethod
    def getHugeRewardsType():
        return NyRewardNotificationModel

    def getIsButtonDisabled(self):
        return self._getBool(2)

    def setIsButtonDisabled(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(GpStyleRewardModel, self)._initialize()
        self._addViewModelProperty('hugeRewards', UserListModel())
        self._addBoolProperty('isButtonDisabled', False)
        self.onStylePreview = self._addCommand('onStylePreview')
