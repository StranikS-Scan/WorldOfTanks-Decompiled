# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/resource_well/tooltips/progress_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.resource_well.tooltips.progress_tooltip_model import ProgressTooltipModel
from gui.impl.pub import ViewImpl

class ProgressTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.resource_well.tooltips.ProgressTooltip())
        settings.model = ProgressTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(ProgressTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ProgressTooltip, self).getViewModel()

    def _onLoading(self, progress, diff=None, *args, **kwargs):
        super(ProgressTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setCurrentProgress(progress)
            if diff is not None:
                model.setNeedShowDiff(True)
                model.setProgressDiff(diff)
        return
