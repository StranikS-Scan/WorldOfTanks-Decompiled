# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/mission_tooltip.py
from frameworks.wulf.view.view import ViewSettings
from gui.impl.gen import R
from story_mode.gui.impl.gen.view_models.views.lobby.mission_selection_tooltip_model import MissionSelectionTooltipModel
from gui.impl.pub import ViewImpl

class MissionTooltip(ViewImpl):

    def __init__(self):
        settings = ViewSettings(R.views.story_mode.lobby.MissionTooltip(), model=MissionSelectionTooltipModel())
        super(MissionTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(MissionTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(MissionTooltip, self)._onLoading(*args, **kwargs)
        self.viewModel.setVehicleName(R.strings.usa_vehicles.M4A3E8_Sherman())
        self.viewModel.setVehicleIcon(R.images.story_mode.gui.maps.icons.missionSelection.tooltip.vehicle())
        self.viewModel.setVehicleDescription(R.strings.usa_vehicles.M4A3E8_Sherman_descr())
