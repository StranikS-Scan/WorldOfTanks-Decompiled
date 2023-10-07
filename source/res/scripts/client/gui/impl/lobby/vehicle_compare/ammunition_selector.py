# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_compare/ammunition_selector.py
from frameworks.wulf import ViewSettings, ViewFlags
from gui.Scaleform.daapi.view.lobby.vehicle_compare import cmp_helpers
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tank_setup.tooltips.warning_tooltip_view_model import WarningDescription
from gui.impl.gen.view_models.views.lobby.tank_setup.vehicle_compare_ammunition_setup_model import VehicleCompareAmmunitionSetupModel
from gui.impl.lobby.tank_setup.main_tank_setup.base import MainTankSetupView
from gui.impl.lobby.tank_setup.tooltips.warning_tooltip_view import WarningTooltipView
from gui.impl.lobby.vehicle_compare.builder import CompareTankSetupBuilder
from gui.impl.lobby.vehicle_compare.tooltips import getCmpSlotTooltipData
from gui.impl.lobby.tank_setup.tooltips.setup_tab_tooltip_view import SetupTabTooltipView
from gui.impl.pub import ViewImpl

class CompareAmmunitionSelectorView(ViewImpl):
    __slots__ = ('_vehItem', '_selectedSlotID', '_tankSetup')

    def __init__(self, layoutID, **kwargs):
        settings = ViewSettings(layoutID)
        settings.model = VehicleCompareAmmunitionSetupModel()
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.kwargs = kwargs.get('ctx', {})
        super(CompareAmmunitionSelectorView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CompareAmmunitionSelectorView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = getCmpSlotTooltipData(event, self._vehItem.getItem(), self._selectedSlotID, self._tankSetup.getSelectedSetup())
            if tooltipData is not None:
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
        return super(CompareAmmunitionSelectorView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tanksetup.tooltips.SetupTabTooltipView():
            return SetupTabTooltipView(event.getArgument('name', ''))
        elif event.contentID == R.views.lobby.tanksetup.tooltips.WarningTooltipView():
            reason = WarningDescription(event.getArgument('reason'))
            isCritical = event.getArgument('isCritical')
            return WarningTooltipView(reason, isCritical)
        else:
            return None

    def _onLoading(self, selectedSection='', selectedSlot=None):
        super(CompareAmmunitionSelectorView, self)._onLoading()
        self._vehItem = cmp_helpers.getCmpConfiguratorMainView().getCurrentVehicleItem()
        self._selectedSlotID = int(selectedSlot)
        self._tankSetup = MainTankSetupView(self.viewModel.tankSetup, CompareTankSetupBuilder(self._vehItem))
        self.viewModel.setSelectedSlot(self._selectedSlotID)
        self._tankSetup.onLoading(selectedSection, selectedSlot)
        fillVehicleInfo(self.viewModel.vehicleInfo, self._vehItem.getItem())

    def _initialize(self, *args, **kwargs):
        super(CompareAmmunitionSelectorView, self)._initialize(*args, **kwargs)
        self._vehItem.onSelected += self.__onItemSelected
        self.viewModel.onClose += self.__onClose
        self.viewModel.onViewRendered += self.__onViewRendered
        self.viewModel.onAnimationEnd += self.__onAnimationEnd
        self._tankSetup.initialize()

    def _finalize(self):
        self._vehItem.onSelected -= self.__onItemSelected
        self.viewModel.onClose -= self.__onClose
        self.viewModel.onViewRendered -= self.__onViewRendered
        self.viewModel.onAnimationEnd -= self.__onAnimationEnd
        self._tankSetup.finalize()
        self._tankSetup = None
        self._vehItem = None
        super(CompareAmmunitionSelectorView, self)._finalize()
        return

    def __onViewRendered(self):
        if not self.viewModel.getShow():
            self.viewModel.setShow(True)

    def __onAnimationEnd(self):
        if not self.viewModel.getShow():
            self.destroyWindow()

    def __onClose(self):
        self.viewModel.setShow(False)

    def __onItemSelected(self, *_):
        self.viewModel.setShow(False)
