# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/tooltips/dormitory_info_tooltip.py
from frameworks.wulf.view.view import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.dormitory_info_tooltip_model import DormitoryInfoTooltipModel
from gui.impl.pub import ViewImpl
from gui.shared.items_cache import getBarrackDormRooms, getVehicleDormRooms

class DormitoryInfoTooltip(ViewImpl):

    def __init__(self):
        settings = ViewSettings(R.views.lobby.detachment.tooltips.DormitoryInfoTooltip())
        settings.model = DormitoryInfoTooltipModel()
        super(DormitoryInfoTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(DormitoryInfoTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            model.setHangarDorms(getVehicleDormRooms())
            model.setExtraDorms(getBarrackDormRooms())
