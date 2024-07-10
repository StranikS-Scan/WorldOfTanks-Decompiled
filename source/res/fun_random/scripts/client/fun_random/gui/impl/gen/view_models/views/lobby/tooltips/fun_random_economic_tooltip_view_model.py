# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/tooltips/fun_random_economic_tooltip_view_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.battle_results.financial_details_model import FinancialDetailsModel

class CurrencyType(Enum):
    CREDITS = 'credits'
    GOLD = 'gold'
    CRYSTALS = 'crystal'
    XP = 'xp'
    FREE_XP = 'freeXP'
    TANKMEN_XP = 'tankmenXP'


class FunRandomEconomicTooltipViewModel(FinancialDetailsModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(FunRandomEconomicTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getCurrencyType(self):
        return CurrencyType(self._getString(4))

    def setCurrencyType(self, value):
        self._setString(4, value.value)

    def getPremiumAdvertising(self):
        return self._getString(5)

    def setPremiumAdvertising(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(FunRandomEconomicTooltipViewModel, self)._initialize()
        self._addStringProperty('currencyType')
        self._addStringProperty('premiumAdvertising', '')
