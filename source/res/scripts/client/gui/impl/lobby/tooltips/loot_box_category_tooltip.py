# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tooltips/loot_box_category_tooltip.py
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.views.loot_box_category_tooltip_model import LootBoxCategoryTooltipModel
from gui.impl.gen.resources import R
from frameworks.wulf import ViewFlags

class LootBoxCategoryTooltipContent(ViewImpl):
    __slots__ = ()

    def __init__(self, category):
        super(LootBoxCategoryTooltipContent, self).__init__(R.views.lootBoxCategoryTooltipContent, ViewFlags.VIEW, LootBoxCategoryTooltipModel, category)

    @property
    def viewModel(self):
        return super(LootBoxCategoryTooltipContent, self).getViewModel()

    def _initialize(self, category):
        super(LootBoxCategoryTooltipContent, self)._initialize()
        self.viewModel.setCategory(category)
