# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/tooltips/rent_icon_tooltip_view.py
from frameworks.wulf import ViewSettings
from battle_royale.gui.impl.gen.view_models.views.lobby.tooltips.rent_icon_tooltip_view_model import RentIconTooltipViewModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.user_compound_price_model import PriceModelBuilder
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleRentVehiclesController

class RentIconTooltipView(ViewImpl):
    __rentVehiclesController = dependency.descriptor(IBattleRoyaleRentVehiclesController)

    def __init__(self):
        settings = ViewSettings(R.views.battle_royale.lobby.tooltips.RentIconTooltipView())
        settings.model = RentIconTooltipViewModel()
        super(RentIconTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RentIconTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(RentIconTooltipView, self)._onLoading(args, kwargs)
        with self.getViewModel().transaction() as model:
            self._fillModel(model)

    def _fillModel(self, model):
        model.setRentDays(self.__rentVehiclesController.getPendingRentDays())
        model.setTimeLeft(self.__rentVehiclesController.getFormatedRentTimeLeft())
        model.setDaysTotal(self.__rentVehiclesController.getNextRentDaysTotal())
        model.setIsTestDriveMode(self.__rentVehiclesController.isInTestDriveRent())
        PriceModelBuilder.fillPriceModel(model.price, self.__rentVehiclesController.getRentPrice())
