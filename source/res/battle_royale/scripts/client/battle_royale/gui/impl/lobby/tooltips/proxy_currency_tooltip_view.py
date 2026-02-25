# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/tooltips/proxy_currency_tooltip_view.py
from battle_royale.gui.impl.gen.view_models.views.lobby.enums import CoinType
from battle_royale.gui.impl.gen.view_models.views.lobby.tooltips.proxy_currency_tooltip_view_model import ProxyCurrencyTooltipViewModel
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class ProxyCurrencyTooltipView(ViewImpl):

    def __init__(self):
        settings = ViewSettings(R.views.battle_royale.mono.lobby.tooltips.proxy_currency_tooltip())
        settings.model = ProxyCurrencyTooltipViewModel()
        super(ProxyCurrencyTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ProxyCurrencyTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ProxyCurrencyTooltipView, self)._onLoading(args, kwargs)
        with self.viewModel.transaction() as tx:
            tx.setCoinType(CoinType.STPCOIN)
