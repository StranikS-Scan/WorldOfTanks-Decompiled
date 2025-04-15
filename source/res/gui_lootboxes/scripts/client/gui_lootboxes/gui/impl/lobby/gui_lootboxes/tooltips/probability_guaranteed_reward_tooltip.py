# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/tooltips/probability_guaranteed_reward_tooltip.py
from gui.impl.gen import R
from frameworks.wulf import ViewSettings
from gui.impl.pub import ViewImpl
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.tooltips.probability_guaranteed_reward_tooltip_model import ProbabilityGuaranteedRewardTooltipModel
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class ProbabilityGuaranteedRewardTooltip(ViewImpl):
    __slots__ = ('__lootBox',)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, lootBox):
        settings = ViewSettings(R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.ProbabilityGuaranteedRewardTooltip())
        settings.model = ProbabilityGuaranteedRewardTooltipModel()
        super(ProbabilityGuaranteedRewardTooltip, self).__init__(settings)
        self.__lootBox = lootBox

    @property
    def viewModel(self):
        return super(ProbabilityGuaranteedRewardTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as vm:
            attemptsAfterGuaranteed = self.__itemsCache.items.tokens.getAttemptsAfterGuaranteedRewards(self.__lootBox)
            vm.setGuaranteedFrequency(self.__lootBox.getGuaranteedFrequency() - attemptsAfterGuaranteed)
