# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/veh_post_progression/tooltips/base_feature_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.post_progression.tooltip.feature_tooltip_view_model import FeatureTooltipViewModel
from gui.impl.pub import ViewImpl

class BaseFeatureTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID, model, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.model = model
        settings.args = args
        settings.kwargs = kwargs
        super(BaseFeatureTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BaseFeatureTooltipView, self).getViewModel()

    def _onLoading(self, step, *args, **kwargs):
        super(BaseFeatureTooltipView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setLevel(step.getLevel())
            model.setIsUnlocked(step.isReceived())
            model.setIsDisabled(step.action.isDisabled())
