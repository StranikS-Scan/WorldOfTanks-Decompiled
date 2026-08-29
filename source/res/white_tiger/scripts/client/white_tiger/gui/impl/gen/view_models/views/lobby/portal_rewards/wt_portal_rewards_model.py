# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/portal_rewards/wt_portal_rewards_model.py
from frameworks.wulf import Array
from white_tiger.gui.impl.gen.view_models.views.lobby.common.wt_guaranteed_reward_model import WtGuaranteedRewardModel
from white_tiger.gui.impl.gen.view_models.views.lobby.portal_rewards.wt_currency_balance_model import WtCurrencyBalanceModel
from white_tiger.gui.impl.gen.view_models.views.lobby.portal_rewards.wt_portal_rewards_base_model import WtPortalRewardsBaseModel
from white_tiger.gui.impl.gen.view_models.views.lobby.portal_rewards.wt_reroll_model import WtRerollModel

class WtPortalRewardsModel(WtPortalRewardsBaseModel):
    __slots__ = ('onClaimReward', 'onReroll', 'onAnimationSettingChange')

    def __init__(self, properties=13, commands=7):
        super(WtPortalRewardsModel, self).__init__(properties=properties, commands=commands)

    @property
    def guaranteedReward(self):
        return self._getViewModel(4)

    @staticmethod
    def getGuaranteedRewardType():
        return WtGuaranteedRewardModel

    @property
    def currencyBalance(self):
        return self._getViewModel(5)

    @staticmethod
    def getCurrencyBalanceType():
        return WtCurrencyBalanceModel

    @property
    def reroll(self):
        return self._getViewModel(6)

    @staticmethod
    def getRerollType():
        return WtRerollModel

    def getLootBoxesCount(self):
        return self._getNumber(7)

    def setLootBoxesCount(self, value):
        self._setNumber(7, value)

    def getSelectedLootBoxesCount(self):
        return self._getNumber(8)

    def setSelectedLootBoxesCount(self, value):
        self._setNumber(8, value)

    def getOpenLootBoxesCount(self):
        return self._getArray(9)

    def setOpenLootBoxesCount(self, value):
        self._setArray(9, value)

    @staticmethod
    def getOpenLootBoxesCountType():
        return int

    def getIsBossLootBox(self):
        return self._getBool(10)

    def setIsBossLootBox(self, value):
        self._setBool(10, value)

    def getIsLaunchAnimated(self):
        return self._getBool(11)

    def setIsLaunchAnimated(self, value):
        self._setBool(11, value)

    def getIsViewActive(self):
        return self._getBool(12)

    def setIsViewActive(self, value):
        self._setBool(12, value)

    def _initialize(self):
        super(WtPortalRewardsModel, self)._initialize()
        self._addViewModelProperty('guaranteedReward', WtGuaranteedRewardModel())
        self._addViewModelProperty('currencyBalance', WtCurrencyBalanceModel())
        self._addViewModelProperty('reroll', WtRerollModel())
        self._addNumberProperty('lootBoxesCount', 0)
        self._addNumberProperty('selectedLootBoxesCount', 1)
        self._addArrayProperty('openLootBoxesCount', Array())
        self._addBoolProperty('isBossLootBox', False)
        self._addBoolProperty('isLaunchAnimated', False)
        self._addBoolProperty('isViewActive', True)
        self.onClaimReward = self._addCommand('onClaimReward')
        self.onReroll = self._addCommand('onReroll')
        self.onAnimationSettingChange = self._addCommand('onAnimationSettingChange')
