# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_royale/dialogs/sub_views/br_money_balance_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.dialogs.dialog_template_generic_tooltip_view_model import DialogTemplateGenericTooltipViewModel

class BrMoneyBalanceViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(BrMoneyBalanceViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def creditsTooltip(self):
        return self._getViewModel(0)

    @property
    def brcoinsTooltip(self):
        return self._getViewModel(1)

    def getCredits(self):
        return self._getNumber(2)

    def setCredits(self, value):
        self._setNumber(2, value)

    def getBrcoins(self):
        return self._getNumber(3)

    def setBrcoins(self, value):
        self._setNumber(3, value)

    def getIsWGMAvailable(self):
        return self._getBool(4)

    def setIsWGMAvailable(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(BrMoneyBalanceViewModel, self)._initialize()
        self._addViewModelProperty('creditsTooltip', DialogTemplateGenericTooltipViewModel())
        self._addViewModelProperty('brcoinsTooltip', DialogTemplateGenericTooltipViewModel())
        self._addNumberProperty('credits', 0)
        self._addNumberProperty('brcoins', 0)
        self._addBoolProperty('isWGMAvailable', False)
