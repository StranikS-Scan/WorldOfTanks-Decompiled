# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/tooltips/convertation_vehicle_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.convertation_vehicle_tooltip_model import ConvertationVehicleTooltipModel
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.Vehicle import getIconResourceName
from uilogging.detachment.loggers import DynamicGroupTooltipLogger

class ConvertationVehicleTooltipView(ViewImpl):
    __slots__ = ('__state', '__vehicle')
    uiLogger = DynamicGroupTooltipLogger()

    def __init__(self, layoutID, vehicle, state=ConvertationVehicleTooltipModel.DEFAULT, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.model = ConvertationVehicleTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__state = state
        self.__vehicle = vehicle
        super(ConvertationVehicleTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ConvertationVehicleTooltipView, self).getViewModel()

    def _onLoading(self):
        super(ConvertationVehicleTooltipView, self)._onLoading()
        self.__fillModel()

    def _initialize(self, *args, **kwargs):
        super(ConvertationVehicleTooltipView, self)._initialize()
        self.uiLogger.tooltipOpened()

    def _finalize(self):
        self.uiLogger.tooltipClosed(self.__class__.__name__)
        self.uiLogger.reset()
        super(ConvertationVehicleTooltipView, self)._finalize()

    def __fillModel(self):
        vehicle = self.__vehicle
        with self.viewModel.transaction() as vm:
            vm.setState(self.__state)
            vehicleIcon = getIconResourceName(vehicle.name)
            vm.setIcon(vehicleIcon)
            vm.setType(vehicle.type)
            vm.setLevel(vehicle.level)
            vm.setIsPremium(vehicle.isPremium)
            if not vehicle.isPremium:
                vm.setName(vehicle.shortUserName)
            nation = backport.text(R.strings.nations.dyn(vehicle.nationName).genetiveCase())
            vm.setPremiumVehicle(backport.text(R.strings.detachment.convert.premiumTank.dyn(vehicle.uiType)(), nation=nation))
