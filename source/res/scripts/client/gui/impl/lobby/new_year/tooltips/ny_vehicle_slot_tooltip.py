# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_vehicle_slot_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_vehicle_slot_tooltip_model import NyVehicleSlotTooltipModel
from gui.impl.lobby.new_year.ny_views_helpers import setSlotTooltipBonuses
from gui.impl.pub import ViewImpl
from ny_common.settings import NYVehBranchConsts

class NyVehicleSlotTooltip(ViewImpl):
    __slots__ = ('__slotType',)

    def __init__(self, slotType):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyVehicleSlotTooltip())
        settings.model = NyVehicleSlotTooltipModel()
        super(NyVehicleSlotTooltip, self).__init__(settings)
        self.__slotType = slotType

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(NyVehicleSlotTooltip, self)._onLoading()
        with self.viewModel.transaction() as vm:
            vm.setIsExtraSlot(self.__slotType == NYVehBranchConsts.TOKEN)
            setSlotTooltipBonuses(vm)
