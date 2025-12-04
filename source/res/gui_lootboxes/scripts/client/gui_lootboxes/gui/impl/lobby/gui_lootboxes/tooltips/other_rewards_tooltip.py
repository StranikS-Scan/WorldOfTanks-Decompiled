# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/tooltips/other_rewards_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.tooltips.other_rewards_tooltip_model import OtherRewardsTooltipModel, OtherRewardType

class OtherRewardsTooltip(ViewImpl):
    __slots__ = ('__type',)

    def __init__(self, type_):
        settings = ViewSettings(R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.OtherRewardsTooltip())
        settings.model = OtherRewardsTooltipModel()
        super(OtherRewardsTooltip, self).__init__(settings)
        self.__type = type_

    @property
    def viewModel(self):
        return super(OtherRewardsTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(OtherRewardsTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as vm:
            vm.setType(OtherRewardType(self.__type))
