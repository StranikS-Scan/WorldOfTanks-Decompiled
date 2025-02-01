# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions/tooltips/rest_rewards_tooltip_view.py
from frameworks.wulf import ViewSettings
from frameworks.wulf.view.array import fillViewModelsArray
from gui.impl.gen.view_models.views.lobby.personal_missions.tooltips.rest_rewards_tooltip_view_model import RestRewardsTooltipViewModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class RestRewardsTooltipView(ViewImpl):
    __slots__ = ('__rewards',)

    def __init__(self, rewards=None):
        settings = ViewSettings(R.views.lobby.personal_missions.tooltips.RestRewardsTooltipView())
        settings.model = RestRewardsTooltipViewModel()
        self.__rewards = rewards or []
        super(RestRewardsTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RestRewardsTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(RestRewardsTooltipView, self)._onLoading()
        with self.viewModel.transaction() as vm:
            rewardsModel = vm.getRewards()
            rewardsModel.clear()
            fillViewModelsArray(self.__rewards, rewardsModel)
