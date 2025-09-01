# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/mission_tooltip.py
import typing
from debug_utils import LOG_ERROR
from frameworks.wulf.view.view import ViewSettings
from gui.impl.gen import R
from gui.impl.gen_utils import INVALID_RES_ID
from story_mode.gui.impl.gen.view_models.views.lobby.mission_selection_tooltip_model import MissionSelectionTooltipModel
from gui.impl.pub import ViewImpl
if typing.TYPE_CHECKING:
    from gui.shared.gui_items import Vehicle

class MissionTooltip(ViewImpl):

    def __init__(self, vehicle):
        settings = ViewSettings(R.views.story_mode.lobby.MissionTooltip(), model=MissionSelectionTooltipModel())
        super(MissionTooltip, self).__init__(settings)
        self._vehicle = vehicle

    @property
    def viewModel(self):
        return super(MissionTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(MissionTooltip, self)._onLoading(*args, **kwargs)
        self.viewModel.setVehicleName(self._vehicle.userName)
        self.viewModel.setVehicleDescription(self._vehicle.fullDescription)
        vehicleName = self._vehicle.name.split(':', 1)[-1].lower()
        iconRes = R.images.story_mode.gui.maps.icons.missionSelection.tooltip.vehicle.dyn(vehicleName)()
        if iconRes != INVALID_RES_ID:
            self.viewModel.setVehicleIcon(iconRes)
        else:
            LOG_ERROR('Tooltip icon not found for vehicle %s.' % vehicleName)

    def _finalize(self):
        super(MissionTooltip, self)._finalize()
        self._vehicle = None
        return
