# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/player_subscriptions/subscription_reward_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.player_subscriptions.main_reward_model import MainRewardModel

class SubscriptionRewardViewModel(ViewModel):
    __slots__ = ('onCloseButtonClick', 'onChooseButtonClick')

    def __init__(self, properties=5, commands=2):
        super(SubscriptionRewardViewModel, self).__init__(properties=properties, commands=commands)

    def getSubscriptionTitle(self):
        return self._getString(0)

    def setSubscriptionTitle(self, value):
        self._setString(0, value)

    def getDescText(self):
        return self._getString(1)

    def setDescText(self, value):
        self._setString(1, value)

    def getMainRewards(self):
        return self._getArray(2)

    def setMainRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getMainRewardsType():
        return MainRewardModel

    def getHasSelectiveRewards(self):
        return self._getBool(3)

    def setHasSelectiveRewards(self, value):
        self._setBool(3, value)

    def getRewards(self):
        return self._getArray(4)

    def setRewards(self, value):
        self._setArray(4, value)

    @staticmethod
    def getRewardsType():
        return BonusModel

    def _initialize(self):
        super(SubscriptionRewardViewModel, self)._initialize()
        self._addStringProperty('subscriptionTitle', '')
        self._addStringProperty('descText', '')
        self._addArrayProperty('mainRewards', Array())
        self._addBoolProperty('hasSelectiveRewards', True)
        self._addArrayProperty('rewards', Array())
        self.onCloseButtonClick = self._addCommand('onCloseButtonClick')
        self.onChooseButtonClick = self._addCommand('onChooseButtonClick')
