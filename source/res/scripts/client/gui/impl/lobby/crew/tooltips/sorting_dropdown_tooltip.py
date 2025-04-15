# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/sorting_dropdown_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.crew.tooltips import sorting_dropdown_tooltip_model as tt_model
from gui.impl.pub import ViewImpl

class SortingDropdownTooltip(ViewImpl):

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.model = tt_model.SortingDropdownTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(SortingDropdownTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SortingDropdownTooltip, self).getViewModel()

    def _onLoading(self, isWarningShown, isSortingDisabled, *args, **kwargs):
        super(SortingDropdownTooltip, self)._onLoading(*args, **kwargs)
        self.viewModel.setShowSortingSelectionWarning(isWarningShown)
        self.viewModel.setIsSortingDisabled(isSortingDisabled)
