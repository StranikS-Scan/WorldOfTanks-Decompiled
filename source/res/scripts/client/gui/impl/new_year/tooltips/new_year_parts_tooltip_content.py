# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/tooltips/new_year_parts_tooltip_content.py
from frameworks.wulf.gui_constants import ViewFlags
from frameworks.wulf.view.view import View
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.new_year.tooltips.new_year_parts_tooltip_content_model import NewYearPartsTooltipContentModel
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class NewYearPartsTooltipContent(View):

    def __init__(self):
        super(NewYearPartsTooltipContent, self).__init__(R.views.newYearPartsTooltipContent, ViewFlags.COMPONENT, NewYearPartsTooltipContentModel)

    @property
    def viewModel(self):
        return super(NewYearPartsTooltipContent, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(NewYearPartsTooltipContent, self)._initialize()
        self.viewModel.setShardsCount(dependency.instance(IItemsCache).items.festivity.getShardsCount())
