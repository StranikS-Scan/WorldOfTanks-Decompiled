# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/daily/session_progress_rewards_notification_view_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.impl.gen.view_models.views.lobby.notifications.notification_model import NotificationModel

class SessionProgressRewardsNotificationViewModel(NotificationModel):
    __slots__ = ('goToProgression', 'onShown')

    def __init__(self, properties=5, commands=2):
        super(SessionProgressRewardsNotificationViewModel, self).__init__(properties=properties, commands=commands)

    def getStep(self):
        return self._getNumber(1)

    def setStep(self, value):
        self._setNumber(1, value)

    def getShowButton(self):
        return self._getBool(2)

    def setShowButton(self, value):
        self._setBool(2, value)

    def getIsDisabled(self):
        return self._getBool(3)

    def setIsDisabled(self, value):
        self._setBool(3, value)

    def getRewards(self):
        return self._getArray(4)

    def setRewards(self, value):
        self._setArray(4, value)

    @staticmethod
    def getRewardsType():
        return IconBonusModel

    def _initialize(self):
        super(SessionProgressRewardsNotificationViewModel, self)._initialize()
        self._addNumberProperty('step', 1)
        self._addBoolProperty('showButton', False)
        self._addBoolProperty('isDisabled', False)
        self._addArrayProperty('rewards', Array())
        self.goToProgression = self._addCommand('goToProgression')
        self.onShown = self._addCommand('onShown')
