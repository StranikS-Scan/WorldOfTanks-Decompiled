# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/tooltips/ny_block_activities_tooltip.py
from frameworks.wulf import ViewSettings
from new_year.gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_block_activities_tooltip_model import NyBlockActivitiesTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from new_year.helpers.server_settings import getNewYearGeneralConfig

class NyBlockActivitiesTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.new_year.lobby.new_year.tooltips.NyBlockActivitiesTooltip())
        settings.model = NyBlockActivitiesTooltipModel()
        super(NyBlockActivitiesTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyBlockActivitiesTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        self.viewModel.setLevel(getNewYearGeneralConfig().getRaccoonLevelOpen())
        super(NyBlockActivitiesTooltip, self)._onLoading(*args, **kwargs)
