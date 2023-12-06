# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tooltips/loot_box_category_tooltip.py
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.views.loot_box_category_tooltip_model import LootBoxCategoryTooltipModel
from gui.impl.gen.resources import R
from frameworks.wulf import ViewSettings

class LootBoxCategoryTooltipContent(ViewImpl):
    __slots__ = ()

    def __init__(self, *args):
        settings = ViewSettings(R.views.lobby.tooltips.loot_box_category_tooltip.LootBoxCategoryTooltipContent())
        settings.model = LootBoxCategoryTooltipModel()
        settings.args = args
        super(LootBoxCategoryTooltipContent, self).__init__(settings)

    @property
    def viewModel(self):
        return super(LootBoxCategoryTooltipContent, self).getViewModel()

    def _initialize(self, category):
        super(LootBoxCategoryTooltipContent, self)._initialize()
        self.viewModel.setCategory(category)
