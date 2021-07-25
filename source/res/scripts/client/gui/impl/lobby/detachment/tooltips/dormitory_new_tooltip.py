# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/tooltips/dormitory_new_tooltip.py
from frameworks.wulf.view.view import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.dormitory_new_tooltip_model import DormitoryNewTooltipModel
from gui.impl.pub import ViewImpl
from gui.shared.items_cache import getTotalDormsRooms

class DormitoryNewTooltip(ViewImpl):

    def __init__(self):
        settings = ViewSettings(R.views.lobby.detachment.tooltips.DormitoryNewTooltip())
        settings.model = DormitoryNewTooltipModel()
        super(DormitoryNewTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(DormitoryNewTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            model.setAmount(getTotalDormsRooms())
