# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/tooltips/guaranteed_reward_tooltip.py
from frameworks.wulf.view.array import fillStringsArray, fillIntsArray
from gui.impl.gen import R
from frameworks.wulf import ViewSettings
from gui.impl.pub import ViewImpl
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.tooltips.guaranteed_reward_tooltip_model import GuaranteedRewardTooltipModel
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class GuaranteedRewardTooltip(ViewImpl):
    __slots__ = ('__lootBox',)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, lootBox):
        settings = ViewSettings(R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.GuaranteedRewardTooltip())
        settings.model = GuaranteedRewardTooltipModel()
        super(GuaranteedRewardTooltip, self).__init__(settings)
        self.__lootBox = lootBox

    @property
    def viewModel(self):
        return super(GuaranteedRewardTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as vm:
            fillIntsArray(self.__lootBox.getGuaranteedVehicleLevelsRange(), vm.getLevelsRange())
            vm.setGuaranteedFrequency(self.__lootBox.getGuaranteedFrequency())
            lootBoxes = self.__itemsCache.items.tokens.getLootBoxes().values()
            boxesWithSameHistoryName = [ lb.getUserNameKey() for lb in lootBoxes if lb.getHistoryName() == self.__lootBox.getHistoryName() ]
            if len(boxesWithSameHistoryName) > 1:
                fillStringsArray(boxesWithSameHistoryName, vm.getGuaranteedBoxNameKeys())
