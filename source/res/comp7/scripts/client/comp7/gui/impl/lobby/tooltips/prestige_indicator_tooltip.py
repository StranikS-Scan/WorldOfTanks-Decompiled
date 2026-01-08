# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/tooltips/prestige_indicator_tooltip.py
from comp7.gui.impl.gen.view_models.views.lobby.tooltips.prestige_indicator_tooltip_model import PrestigeIndicatorTooltipModel
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class PrestigeIndicatorTooltip(ViewImpl):
    __slots__ = ('__params',)

    def __init__(self, layoutID=R.views.comp7.mono.lobby.tooltips.prestige_indicator_tooltip(), params=None):
        settings = ViewSettings(layoutID)
        settings.model = PrestigeIndicatorTooltipModel()
        super(PrestigeIndicatorTooltip, self).__init__(settings)
        self.__params = params

    @property
    def viewModel(self):
        return super(PrestigeIndicatorTooltip, self).getViewModel()

    def _onLoading(self):
        super(PrestigeIndicatorTooltip, self)._onLoading()
        with self.viewModel.transaction() as vm:
            vm.setStatisticsMode(self.__params['statisticsMode'])
            vm.setAveragePrestige(self.__params['averagePrestige'])
            vm.setRecordPrestige(self.__params['recordPrestige'])
            vm.setRecordPrestigeVehicleName(self.__params['recordPrestigeVehicleName'])
