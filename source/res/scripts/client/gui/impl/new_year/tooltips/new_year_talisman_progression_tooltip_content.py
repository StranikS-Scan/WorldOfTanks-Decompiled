# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/tooltips/new_year_talisman_progression_tooltip_content.py
from frameworks.wulf.view.view import View, ViewSettings
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.new_year_talisman_progression_tooltip_content_model import NewYearTalismanProgressionTooltipContentModel
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class NewYearTalismanProgressionTooltipContent(View):
    __slots__ = ()
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.new_year_talisman_progression_tooltip_content.NewYearTalismanProgressionTooltipContent())
        settings.model = NewYearTalismanProgressionTooltipContentModel()
        super(NewYearTalismanProgressionTooltipContent, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NewYearTalismanProgressionTooltipContent, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(NewYearTalismanProgressionTooltipContent, self)._initialize()
        _, currentStage = self._itemsCache.items.festivity.getTalismansStage()
        self.viewModel.setCurrentStage(currentStage)
