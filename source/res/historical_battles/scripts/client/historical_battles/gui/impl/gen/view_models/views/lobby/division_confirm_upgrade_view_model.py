# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/division_confirm_upgrade_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.dialogs.dialog_template_generic_tooltip_view_model import DialogTemplateGenericTooltipViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel

class DivisionConfirmUpgradeViewModel(ViewModel):
    __slots__ = ('onClose', 'onBuy')

    def __init__(self, properties=14, commands=2):
        super(DivisionConfirmUpgradeViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def goldTooltip(self):
        return self._getViewModel(0)

    @staticmethod
    def getGoldTooltipType():
        return DialogTemplateGenericTooltipViewModel

    @property
    def creditsTooltip(self):
        return self._getViewModel(1)

    @staticmethod
    def getCreditsTooltipType():
        return DialogTemplateGenericTooltipViewModel

    @property
    def crystalsTooltip(self):
        return self._getViewModel(2)

    @staticmethod
    def getCrystalsTooltipType():
        return DialogTemplateGenericTooltipViewModel

    @property
    def freeExpTooltip(self):
        return self._getViewModel(3)

    @staticmethod
    def getFreeExpTooltipType():
        return DialogTemplateGenericTooltipViewModel

    def getFrontName(self):
        return self._getString(4)

    def setFrontName(self, value):
        self._setString(4, value)

    def getSubDivisionIndex(self):
        return self._getNumber(5)

    def setSubDivisionIndex(self, value):
        self._setNumber(5, value)

    def getPrice(self):
        return self._getNumber(6)

    def setPrice(self, value):
        self._setNumber(6, value)

    def getIsMoneyBalanceAvailable(self):
        return self._getBool(7)

    def setIsMoneyBalanceAvailable(self, value):
        self._setBool(7, value)

    def getFreeExp(self):
        return self._getNumber(8)

    def setFreeExp(self, value):
        self._setNumber(8, value)

    def getCredits(self):
        return self._getNumber(9)

    def setCredits(self, value):
        self._setNumber(9, value)

    def getGold(self):
        return self._getNumber(10)

    def setGold(self, value):
        self._setNumber(10, value)

    def getCrystals(self):
        return self._getNumber(11)

    def setCrystals(self, value):
        self._setNumber(11, value)

    def getRewards(self):
        return self._getArray(12)

    def setRewards(self, value):
        self._setArray(12, value)

    @staticmethod
    def getRewardsType():
        return RewardItemModel

    def getIsEnoughMoney(self):
        return self._getBool(13)

    def setIsEnoughMoney(self, value):
        self._setBool(13, value)

    def _initialize(self):
        super(DivisionConfirmUpgradeViewModel, self)._initialize()
        self._addViewModelProperty('goldTooltip', DialogTemplateGenericTooltipViewModel())
        self._addViewModelProperty('creditsTooltip', DialogTemplateGenericTooltipViewModel())
        self._addViewModelProperty('crystalsTooltip', DialogTemplateGenericTooltipViewModel())
        self._addViewModelProperty('freeExpTooltip', DialogTemplateGenericTooltipViewModel())
        self._addStringProperty('frontName', '')
        self._addNumberProperty('subDivisionIndex', 0)
        self._addNumberProperty('price', -1)
        self._addBoolProperty('isMoneyBalanceAvailable', False)
        self._addNumberProperty('freeExp', -1)
        self._addNumberProperty('credits', -1)
        self._addNumberProperty('gold', -1)
        self._addNumberProperty('crystals', -1)
        self._addArrayProperty('rewards', Array())
        self._addBoolProperty('isEnoughMoney', False)
        self.onClose = self._addCommand('onClose')
        self.onBuy = self._addCommand('onBuy')
