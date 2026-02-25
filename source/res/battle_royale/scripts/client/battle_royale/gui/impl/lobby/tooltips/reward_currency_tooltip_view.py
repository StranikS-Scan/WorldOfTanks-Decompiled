# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/tooltips/reward_currency_tooltip_view.py
from battle_royale.gui.impl.gen.view_models.views.lobby.tooltips.reward_currency_tooltip_view_model import RewardCurrencyTooltipViewModel
from battle_royale.gui.impl.lobby.br_helpers.utils import setEventInfo
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.server_events.battle_royale_formatters import BRSections
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService
from battle_royale.gui.impl.gen.view_models.views.lobby.enums import CoinType
_PREMIUM_BONUS_CURRENCIES = (Currency.BRCOIN, Currency.CREDITS, 'xp')
_DAILY_BONUS_CURRENCIES = (Currency.STPCOIN,)

class RewardCurrencyTooltipView(ViewImpl):
    __battleResults = dependency.descriptor(IBattleResultsService)

    def __init__(self, currencyType, arenaUniqueID):
        settings = ViewSettings(R.views.battle_royale.mono.lobby.tooltips.reward_currency_tooltip())
        settings.model = RewardCurrencyTooltipViewModel()
        self.__currencyType = currencyType
        self.__arenaUniqueID = arenaUniqueID
        super(RewardCurrencyTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RewardCurrencyTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(RewardCurrencyTooltipView, self)._onLoading(args, kwargs)
        with self.viewModel.transaction() as tx:
            tx.setCurrencyType(self.__currencyType)
            tx.setHasPremiumBonus(self.__currencyType in _PREMIUM_BONUS_CURRENCIES)
            if self.__currencyType in _DAILY_BONUS_CURRENCIES:
                data = self.__battleResults.getResultsVO(self.__arenaUniqueID)
                dailyBonusFactor = data[BRSections.PERSONAL]['dailyBonusFactor']
                if dailyBonusFactor > 0:
                    tx.dailyBonus.setHasDailyBonus(True)
                    tx.dailyBonus.setDailyBonusFactor(dailyBonusFactor)
                    tx.dailyBonus.setCoinType(CoinType.STPCOIN)
            setEventInfo(tx.eventInfo)
