# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/dialogs/sub_views/money_balance_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.dialogs.dialog_template_generic_tooltip_view_model import DialogTemplateGenericTooltipViewModel

class MoneyBalanceViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
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

    def getGold(self):
        return self._getNumber(4)

    def setGold(self, value):
        self._setNumber(4, value)

    def getCredits(self):
        return self._getNumber(5)

    def setCredits(self, value):
        self._setNumber(5, value)

    def getCrystals(self):
        return self._getNumber(6)

    def setCrystals(self, value):
        self._setNumber(6, value)

    def getFreeExp(self):
        return self._getNumber(7)

    def setFreeExp(self, value):
        self._setNumber(7, value)

    def getIsWGMAvailable(self):
        return self._getBool(8)

    def setIsWGMAvailable(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(MoneyBalanceViewModel, self)._initialize()
        self._addViewModelProperty('goldTooltip', DialogTemplateGenericTooltipViewModel())
        self._addViewModelProperty('creditsTooltip', DialogTemplateGenericTooltipViewModel())
        self._addViewModelProperty('crystalsTooltip', DialogTemplateGenericTooltipViewModel())
        self._addViewModelProperty('freeExpTooltip', DialogTemplateGenericTooltipViewModel())
        self._addNumberProperty('gold', 0)
        self._addNumberProperty('credits', 0)
        self._addNumberProperty('crystals', 0)
        self._addNumberProperty('freeExp', 0)
        self._addBoolProperty('isWGMAvailable', False)
