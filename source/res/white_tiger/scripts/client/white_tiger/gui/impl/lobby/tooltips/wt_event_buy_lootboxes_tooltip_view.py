# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/tooltips/wt_event_buy_lootboxes_tooltip_view.py
from frameworks.wulf import ViewSettings
from white_tiger.gui.impl.gen.view_models.views.lobby.tooltips.wt_event_buy_lootboxes_tooltip_view_model import WtEventBuyLootboxesTooltipViewModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.game_control import IWhiteTigerController, ILootBoxesController

class WtEventBuyLootBoxesTooltipView(ViewImpl):
    __slots__ = ()
    __eventController = dependency.descriptor(IWhiteTigerController)
    __lootBoxesCtrl = dependency.descriptor(ILootBoxesController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.white_tiger.lobby.tooltips.BattlesEndTooltipView(), model=WtEventBuyLootboxesTooltipViewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(WtEventBuyLootBoxesTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WtEventBuyLootBoxesTooltipView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setAmountLeft(self.__lootBoxesCtrl.getAvailableForPurchaseLootBoxesCount())
            model.setAmountMax(self.__lootBoxesCtrl.getLootBoxDailyPurchaseLimit())
