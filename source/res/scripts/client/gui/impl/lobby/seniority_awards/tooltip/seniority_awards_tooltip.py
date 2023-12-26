# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/seniority_awards/tooltip/seniority_awards_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.seniority_awards.seniority_awards_tooltip_model import SeniorityAwardsTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.game_control import ISeniorityAwardsController

class SeniorityAwardsTooltip(ViewImpl):
    __slots__ = ()
    __seniorityAwardsCtrl = dependency.descriptor(ISeniorityAwardsController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.seniority_awards.SeniorityAwardsTooltip())
        settings.model = SeniorityAwardsTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(SeniorityAwardsTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SeniorityAwardsTooltip, self).getViewModel()

    def _onLoading(self, category, years):
        categories = [ (k, v) for k, v in self.__seniorityAwardsCtrl.categories.items() ]
        categories = sorted(categories, key=lambda item: item[1][0])
        with self.viewModel.transaction() as vm:
            vm.setCategory(category)
            vm.setYears(years)
            for ctgId, _ in categories:
                vm.getCategories().addString(ctgId.lower())
