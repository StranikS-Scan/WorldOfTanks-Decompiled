# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/lobby/tooltips/progression_entry_point_tooltip.py
from frameworks.wulf import ViewFlags, ViewSettings
from cosmic_event.gui.impl.gen.view_models.views.lobby.tooltips.progression_entry_point_tooltip_model import ProgressionEntryPointTooltipModel
from gui.impl.pub import ViewImpl

class ProgressionEntryPointTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = ProgressionEntryPointTooltipModel()
        super(ProgressionEntryPointTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ProgressionEntryPointTooltip, self).getViewModel()
