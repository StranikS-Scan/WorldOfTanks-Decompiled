# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/tooltips/shop_button_tooltip_view.py
from battle_royale.gui.impl.gen.view_models.views.lobby.tooltips.shop_button_tooltip_view_model import ShopButtonTooltipViewModel
from frameworks.wulf import ViewFlags, ViewSettings
from battle_royale.gui.impl.lobby.br_helpers.utils import setEventInfo
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class ShopButtonTooltipView(ViewImpl):

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.battle_royale.mono.lobby.tooltips.shop_button())
        settings.flags = ViewFlags.VIEW
        settings.model = ShopButtonTooltipViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(ShopButtonTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ShopButtonTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ShopButtonTooltipView, self)._onLoading(args, kwargs)
        with self.viewModel.transaction() as tx:
            setEventInfo(tx.eventInfo)
