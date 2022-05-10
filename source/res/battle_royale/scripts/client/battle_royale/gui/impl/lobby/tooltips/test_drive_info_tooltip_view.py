# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/tooltips/test_drive_info_tooltip_view.py
from battle_royale.gui.impl.gen.view_models.views.lobby.tooltips.test_drive_info_tooltip_view_model import TestDriveInfoTooltipViewModel
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.user_compound_price_model import PriceModelBuilder
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleRentVehiclesController

class TestDriveInfoTooltipView(ViewImpl):
    __rentVehiclesController = dependency.descriptor(IBattleRoyaleRentVehiclesController)

    def __init__(self):
        settings = ViewSettings(R.views.battle_royale.lobby.tooltips.TestDriveInfoTooltipView())
        settings.model = TestDriveInfoTooltipViewModel()
        super(TestDriveInfoTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(TestDriveInfoTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(TestDriveInfoTooltipView, self)._onLoading(args, kwargs)
        with self.viewModel.transaction() as model:
            self._fillModel(model)

    def _fillModel(self, model):
        model.setTestDriveDays(self.__rentVehiclesController.getPendingRentDays())
        self.__fillPrice(model.price)

    def __fillPrice(self, model):
        testDriveDays = self.__rentVehiclesController.getNextTestDriveDaysTotal()
        rentDays = self.__rentVehiclesController.getNextRentDaysTotal()
        rentPrice = self.__rentVehiclesController.getRentPrice()
        testDrivePrice = self.__rentVehiclesController.getTestDrivePrice()
        model.setTestDriveLabel(backport.text(R.strings.battle_royale.tooltips.testDriveInfo.leftLabel()).format(days=int(testDriveDays)))
        model.setRentLabel(backport.text(R.strings.battle_royale.tooltips.testDriveInfo.rightLabel()).format(days=rentDays))
        PriceModelBuilder.fillPriceModel(model.testDrivePrice, testDrivePrice)
        PriceModelBuilder.fillPriceModel(model.rentPrice, rentPrice)
