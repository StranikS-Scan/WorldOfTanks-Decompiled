# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/gen/view_models/views/lobby/reward_available_notification_view_model.py
from gui.impl.gen.view_models.common.notification_base_model import NotificationBaseModel

class RewardAvailableNotificationViewModel(NotificationBaseModel):
    __slots__ = ('onClose', 'onClaimReward')

    def __init__(self, properties=3, commands=2):
        super(RewardAvailableNotificationViewModel, self).__init__(properties=properties, commands=commands)

    def getTimeLeft(self):
        return self._getNumber(1)

    def setTimeLeft(self, value):
        self._setNumber(1, value)

    def getIsDisabled(self):
        return self._getBool(2)

    def setIsDisabled(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(RewardAvailableNotificationViewModel, self)._initialize()
        self._addNumberProperty('timeLeft', 0)
        self._addBoolProperty('isDisabled', False)
        self.onClose = self._addCommand('onClose')
        self.onClaimReward = self._addCommand('onClaimReward')
