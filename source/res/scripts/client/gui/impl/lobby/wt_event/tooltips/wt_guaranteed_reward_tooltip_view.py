# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/tooltips/wt_guaranteed_reward_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.tooltips.wt_guaranteed_reward_tooltip_view_model import WtGuaranteedRewardTooltipViewModel
from gui.impl.pub import ViewImpl
from gui.wt_event.wt_event_models_helper import setBonusVehicles, setGuaranteedAward

class WtGuaranteedRewardTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.wt_event.tooltips.WtGuaranteedRewardTooltipView())
        settings.model = WtGuaranteedRewardTooltipViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(WtGuaranteedRewardTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WtGuaranteedRewardTooltipView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            setBonusVehicles(model.tanks, withoutSpecialTank=False, isShortName=True)
            setGuaranteedAward(model.guaranteedAward)
