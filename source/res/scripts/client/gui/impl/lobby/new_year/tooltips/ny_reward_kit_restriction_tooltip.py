# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_reward_kit_restriction_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_reward_kit_restriction_tooltip_model import NyRewardKitRestrictionTooltipModel
from gui.impl.pub import ViewImpl

class NyRewardKitRestrictionTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyRewardKitRestrictionTooltip())
        settings.model = NyRewardKitRestrictionTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyRewardKitRestrictionTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyRewardKitRestrictionTooltip, self).getViewModel()

    def _onLoading(self, count, maxCount, isLastDay, countdownTimestamp):
        super(NyRewardKitRestrictionTooltip, self)._onLoading()
        with self.viewModel.transaction() as model:
            model.setCount(count)
            model.setMaxCount(maxCount)
            model.setIsLastDay(isLastDay)
            model.setCountdownTimestamp(countdownTimestamp)
