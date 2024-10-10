# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/tooltips/main_prize_discount_tooltip_view.py
from frameworks.wulf import ViewSettings
from white_tiger.gui.impl.gen.view_models.views.lobby.tooltips.main_prize_discount_tooltip_view_model import MainPrizeDiscountTooltipViewModel
from gui.impl.pub import ViewImpl
from white_tiger_common.wt_helpers import getTankPortalDiscount, getTankPortalActualPrice
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.game_control import IWhiteTigerController

class MainPrizeDiscountTooltipView(ViewImpl):
    __slots__ = ()
    __eventController = dependency.descriptor(IWhiteTigerController)

    def __init__(self):
        settings = ViewSettings(R.views.white_tiger.lobby.tooltips.MainPrizeDiscountTooltipView())
        settings.model = MainPrizeDiscountTooltipViewModel()
        super(MainPrizeDiscountTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(MainPrizeDiscountTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(MainPrizeDiscountTooltipView, self)._onLoading(*args, **kwargs)
        tankPortalPrice = self.__eventController.getConfig().tankPortalPrice
        maxTokenCount = self.__eventController.getConfig().mainPrizeMaxDiscountTokenCount
        discountPerToken = self.__eventController.getMainPrizeDiscountPerToken()
        discountTokenCount = self.__eventController.getCurrentMainPrizeDiscountTokensCount()
        with self.viewModel.transaction() as model:
            model.setMaxAmount(maxTokenCount)
            model.setCurrentAmount(discountTokenCount)
            model.setCurrentCost(getTankPortalActualPrice(tankPortalPrice, discountPerToken, discountTokenCount))
            model.setTotalCost(tankPortalPrice)
            model.setDiscount(getTankPortalDiscount(tankPortalPrice, discountPerToken, discountTokenCount))
