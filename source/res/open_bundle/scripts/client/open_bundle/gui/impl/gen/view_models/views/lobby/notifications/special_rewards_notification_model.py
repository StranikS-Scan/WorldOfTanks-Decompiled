# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/gui/impl/gen/view_models/views/lobby/notifications/special_rewards_notification_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.notification_base_model import NotificationBaseModel
from open_bundle.gui.impl.gen.view_models.views.lobby.bonus_model import BonusModel

class SpecialRewardsNotificationModel(NotificationBaseModel):
    __slots__ = ('onShowReward',)

    def __init__(self, properties=4, commands=1):
        super(SpecialRewardsNotificationModel, self).__init__(properties=properties, commands=commands)

    def getBundleType(self):
        return self._getString(1)

    def setBundleType(self, value):
        self._setString(1, value)

    def getIsButtonDisabled(self):
        return self._getBool(2)

    def setIsButtonDisabled(self, value):
        self._setBool(2, value)

    def getBonuses(self):
        return self._getArray(3)

    def setBonuses(self, value):
        self._setArray(3, value)

    @staticmethod
    def getBonusesType():
        return BonusModel

    def _initialize(self):
        super(SpecialRewardsNotificationModel, self)._initialize()
        self._addStringProperty('bundleType', '')
        self._addBoolProperty('isButtonDisabled', False)
        self._addArrayProperty('bonuses', Array())
        self.onShowReward = self._addCommand('onShowReward')
