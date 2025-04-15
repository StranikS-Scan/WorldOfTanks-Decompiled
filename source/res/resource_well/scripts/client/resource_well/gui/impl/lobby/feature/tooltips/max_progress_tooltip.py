# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/lobby/feature/tooltips/max_progress_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from resource_well.gui.impl.gen.view_models.views.lobby.tooltips.max_progress_tooltip_model import MaxProgressTooltipModel

class MaxProgressTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.resource_well.lobby.feature.tooltips.MaxProgressTooltip())
        settings.model = MaxProgressTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(MaxProgressTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(MaxProgressTooltip, self).getViewModel()

    def _onLoading(self, currentValue, maxValue, resourceType, *args, **kwargs):
        super(MaxProgressTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setCurrentValue(currentValue)
            model.setMaxValue(maxValue)
            model.setResourceType(resourceType)
