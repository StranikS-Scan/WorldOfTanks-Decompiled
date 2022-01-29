# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lunar_ny/tooltips/buy_loot_box_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lunar_ny.tooltips.buy_loot_box_tooltip_model import BuyLootBoxTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from lunar_ny import ILunarNYController

class BuyLootBoxTooltip(ViewImpl):
    __slots__ = ('__count',)
    __lunarNYController = dependency.descriptor(ILunarNYController)

    def __init__(self, count=None):
        settings = ViewSettings(R.views.lobby.lunar_ny.tooltips.BuyLootBoxTooltip())
        settings.model = BuyLootBoxTooltipModel()
        super(BuyLootBoxTooltip, self).__init__(settings)
        if count is not None:
            self.__count = count
        else:
            self.__count = self.__lunarNYController.giftSystem.getAmountOfPurchasedEnvelopes()
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BuyLootBoxTooltip, self)._onLoading(*args, **kwargs)
        maxCount = self.__lunarNYController.getEnvelopePurchasesLimit()
        with self.viewModel.transaction() as model:
            model.setAmountMax(maxCount)
            model.setAmountLeft(max(0, maxCount - self.__count))
