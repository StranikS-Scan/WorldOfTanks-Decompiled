# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/tooltips/compensation_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui_lootboxes.gui.bonuses.bonuses_packers import getRewardsBonusPacker
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.tooltips.compensation_tooltip_model import CompensationTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData

class LootBoxesCompensationTooltip(ViewImpl):
    __slots__ = ('__bonusBefore', '__bonusAfter')

    def __init__(self, itemBefore, itemAfter):
        settings = ViewSettings(R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.CompensationTooltip())
        settings.model = CompensationTooltipModel()
        self.__bonusBefore = [itemBefore]
        self.__bonusAfter = [itemAfter]
        super(LootBoxesCompensationTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(LootBoxesCompensationTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        packer = getRewardsBonusPacker()
        with self.viewModel.transaction() as model:
            self.__fillItem(model.getItemBefore(), self.__bonusBefore, packer)
            self.__fillItem(model.getItemAfter(), self.__bonusAfter, packer)

    def __fillItem(self, bonusModelsList, bonuses, packer):
        packBonusModelAndTooltipData(bonuses, bonusModelsList, None, packer)
        bonusModelsList.invalidate()
        return
