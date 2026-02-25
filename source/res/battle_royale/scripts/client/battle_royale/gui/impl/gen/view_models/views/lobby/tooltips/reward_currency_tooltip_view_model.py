# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/tooltips/reward_currency_tooltip_view_model.py
from frameworks.wulf import ViewModel
from battle_royale.gui.impl.gen.view_models.views.lobby.daily_bonus_model import DailyBonusModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.battle_royale_event_model import BattleRoyaleEventModel

class RewardCurrencyTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(RewardCurrencyTooltipViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def eventInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getEventInfoType():
        return BattleRoyaleEventModel

    @property
    def dailyBonus(self):
        return self._getViewModel(1)

    @staticmethod
    def getDailyBonusType():
        return DailyBonusModel

    def getCurrencyType(self):
        return self._getString(2)

    def setCurrencyType(self, value):
        self._setString(2, value)

    def getHasPremiumBonus(self):
        return self._getBool(3)

    def setHasPremiumBonus(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(RewardCurrencyTooltipViewModel, self)._initialize()
        self._addViewModelProperty('eventInfo', BattleRoyaleEventModel())
        self._addViewModelProperty('dailyBonus', DailyBonusModel())
        self._addStringProperty('currencyType', '')
        self._addBoolProperty('hasPremiumBonus', False)
