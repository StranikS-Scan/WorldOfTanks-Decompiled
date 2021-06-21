# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/veh_post_progression/tooltip/setup_tooltip_view.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.post_progression.tooltip.setup_tooltip_view_model import SetupTooltipViewModel, SetupFeatureType
from gui.impl.lobby.veh_post_progression.tooltip.base_feature_tooltip_view import BaseFeatureTooltipView

class SetupTooltipView(BaseFeatureTooltipView):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(SetupTooltipView, self).__init__(R.views.lobby.veh_post_progression.tooltip.SetupTooltipView(), SetupTooltipViewModel(), *args, **kwargs)

    @property
    def viewModel(self):
        return super(SetupTooltipView, self).getViewModel()

    def _onLoading(self, step, *args, **kwargs):
        super(SetupTooltipView, self)._onLoading(step, *args, **kwargs)
        feature = step.action
        with self.viewModel.transaction() as model:
            model.setIconName(feature.getImageName())
            model.setType(SetupFeatureType(feature.getTechName()))
