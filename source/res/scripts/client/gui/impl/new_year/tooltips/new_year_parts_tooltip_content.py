# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/tooltips/new_year_parts_tooltip_content.py
from frameworks.wulf.view.view import View, ViewSettings
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.new_year_parts_tooltip_content_model import NewYearPartsTooltipContentModel
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class NewYearPartsTooltipContent(View):

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.new_year_parts_tooltip_content.NewYearPartsTooltipContent())
        settings.model = NewYearPartsTooltipContentModel()
        super(NewYearPartsTooltipContent, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NewYearPartsTooltipContent, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(NewYearPartsTooltipContent, self)._initialize()
        self.viewModel.setShardsCount(dependency.instance(IItemsCache).items.festivity.getShardsCount())
