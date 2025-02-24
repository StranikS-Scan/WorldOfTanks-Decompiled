# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/tooltips/division_tooltip.py
from comp7.gui.impl.gen.view_models.views.lobby.tooltips.division_tooltip_model import DivisionTooltipModel
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class DivisionTooltip(ViewImpl):
    __slots__ = ('__params',)

    def __init__(self, layoutID=R.views.comp7.lobby.tooltips.DivisionTooltip(), params=None):
        settings = ViewSettings(layoutID)
        settings.model = DivisionTooltipModel()
        super(DivisionTooltip, self).__init__(settings)
        self.__params = params

    @property
    def viewModel(self):
        return super(DivisionTooltip, self).getViewModel()

    def _onLoading(self):
        super(DivisionTooltip, self)._onLoading()
        with self.viewModel.transaction() as vm:
            vm.setRank(self.__params['rank'])
            vm.setDivision(self.__params['division'])
            vm.setFrom(self.__params['from'])
            vm.setTo(self.__params['to'])
