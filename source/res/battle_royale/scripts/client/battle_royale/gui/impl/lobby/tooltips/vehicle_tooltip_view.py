# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/tooltips/vehicle_tooltip_view.py
from battle_royale.gui.impl.gen.view_models.views.lobby.tooltips.vehicle_tooltip_view_model import VehicleTooltipViewModel
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle_royale.equipment_panel_cmp_rent_states import EquipmentPanelCmpRentStates
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.user_compound_price_model import PriceModelBuilder
from gui.shared.tooltips.vehicle import StatusBlockConstructor
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleRentVehiclesController

class VehicleTooltipView(ViewImpl):
    __rentVehiclesController = dependency.descriptor(IBattleRoyaleRentVehiclesController)

    def __init__(self, intCD, context):
        settings = ViewSettings(R.views.battle_royale.lobby.tooltips.VehicleTooltipView())
        settings.model = VehicleTooltipViewModel()
        self.__context = context
        self.__vehicle = context.buildItem(intCD)
        self.__rentState = self.__rentVehiclesController.getRentState(self.__vehicle.intCD)
        super(VehicleTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(VehicleTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(VehicleTooltipView, self)._onLoading(args, kwargs)
        with self.getViewModel().transaction() as model:
            self._fillModel(model)

    def _fillModel(self, model):
        title = self.__vehicle.userName
        nationName = self.__vehicle.nationName
        model.setVehicleName(title)
        model.setVehicleNation(nationName)
        model.setRentState(self.__rentState)
        self.__fillPrice(model.rentPrice)
        self.__fillStatus(self.__vehicle, model)
        model.setRentTimeLeft(self.__rentVehiclesController.getFormatedRentTimeLeft(self.__vehicle.intCD))

    def __fillPrice(self, model):
        testDriveDays = self.__rentVehiclesController.getNextTestDriveDaysTotal(self.__vehicle.intCD)
        rentDays = self.__rentVehiclesController.getNextRentDaysTotal(self.__vehicle.intCD)
        rentPrice = self.__rentVehiclesController.getRentPrice(self.__vehicle.intCD)
        testDrivePrice = self.__rentVehiclesController.getTestDrivePrice(self.__vehicle.intCD)
        showTestDrivePrice = self.__rentState in (EquipmentPanelCmpRentStates.STATE_TEST_DRIVE_ACTIVE, EquipmentPanelCmpRentStates.STATE_TEST_DRIVE_AVAILABLE)
        model.setTestDriveLabel(backport.text(R.strings.battle_royale.tooltips.testDriveInfo.leftLabel()).format(days=testDriveDays))
        model.setRentLabel(backport.text(R.strings.battle_royale.tooltips.testDriveInfo.dyn('rightLabel' if showTestDrivePrice else 'rentFor')()).format(days=rentDays))
        PriceModelBuilder.fillPriceModel(model.testDrivePrice, testDrivePrice)
        PriceModelBuilder.fillPriceModel(model.rentPrice, rentPrice)

    def __fillStatus(self, vehicle, model):
        statusConfig = self.__context.getStatusConfiguration(vehicle)
        _, __, status = StatusBlockConstructor(vehicle, statusConfig).construct()
        model.setStatusText(status['header'])
        model.setStatusLevel(status['level'])
