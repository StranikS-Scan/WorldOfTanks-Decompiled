# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/dialogs/sub_views/money_balance_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.dialogs.dialog_template_generic_tooltip_view_model import DialogTemplateGenericTooltipViewModel

class MoneyBalanceViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(MoneyBalanceViewModel, self).__init__(properties=properties, commands=commands)

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

    @property
    def equipCoinTooltip(self):
        return self._getViewModel(4)

    @staticmethod
    def getEquipCoinTooltipType():
        return DialogTemplateGenericTooltipViewModel

    def getGold(self):
        return self._getNumber(5)

    def setGold(self, value):
        self._setNumber(5, value)

    def getCredits(self):
        return self._getNumber(6)

    def setCredits(self, value):
        self._setNumber(6, value)

    def getCrystals(self):
        return self._getNumber(7)

    def setCrystals(self, value):
        self._setNumber(7, value)

    def getFreeExp(self):
        return self._getNumber(8)

    def setFreeExp(self, value):
        self._setNumber(8, value)

    def getEquipCoin(self):
        return self._getNumber(9)

    def setEquipCoin(self, value):
        self._setNumber(9, value)

    def getIsWGMAvailable(self):
        return self._getBool(10)

    def setIsWGMAvailable(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(MoneyBalanceViewModel, self)._initialize()
        self._addViewModelProperty('goldTooltip', DialogTemplateGenericTooltipViewModel())
        self._addViewModelProperty('creditsTooltip', DialogTemplateGenericTooltipViewModel())
        self._addViewModelProperty('crystalsTooltip', DialogTemplateGenericTooltipViewModel())
        self._addViewModelProperty('freeExpTooltip', DialogTemplateGenericTooltipViewModel())
        self._addViewModelProperty('equipCoinTooltip', DialogTemplateGenericTooltipViewModel())
        self._addNumberProperty('gold', -1)
        self._addNumberProperty('credits', -1)
        self._addNumberProperty('crystals', -1)
        self._addNumberProperty('freeExp', -1)
        self._addNumberProperty('equipCoin', -1)
        self._addBoolProperty('isWGMAvailable', False)
