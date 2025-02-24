# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/tooltips/reward_currency_tooltip_view.py
from battle_royale.gui.impl.gen.view_models.views.lobby.tooltips.reward_currency_tooltip_view_model import RewardCurrencyTooltipViewModel
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class RewardCurrencyTooltipView(ViewImpl):
    __slots__ = ('__currencyType', '__hasBonus')

    def __init__(self, currencyType, hasBonus=False):
        settings = ViewSettings(R.views.battle_royale.lobby.tooltips.RewardCurrencyTooltipView())
        settings.model = RewardCurrencyTooltipViewModel()
        self.__currencyType = currencyType
        self.__hasBonus = hasBonus
        super(RewardCurrencyTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RewardCurrencyTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(RewardCurrencyTooltipView, self)._onLoading(args, kwargs)
        self.viewModel.setCurrencyType(self.__currencyType)
        self.viewModel.setHasBonus(self.__hasBonus)
