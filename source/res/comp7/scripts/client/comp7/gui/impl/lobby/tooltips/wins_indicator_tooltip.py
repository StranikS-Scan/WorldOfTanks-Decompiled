# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/tooltips/wins_indicator_tooltip.py
from comp7.gui.impl.gen.view_models.views.lobby.tooltips.wins_indicator_tooltip_model import WinsIndicatorTooltipModel
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class WinsIndicatorTooltip(ViewImpl):
    __slots__ = ('__params',)

    def __init__(self, layoutID=R.views.comp7.mono.lobby.tooltips.wins_indicator_tooltip(), params=None):
        settings = ViewSettings(layoutID)
        settings.model = WinsIndicatorTooltipModel()
        super(WinsIndicatorTooltip, self).__init__(settings)
        self.__params = params

    @property
    def viewModel(self):
        return super(WinsIndicatorTooltip, self).getViewModel()

    def _onLoading(self):
        super(WinsIndicatorTooltip, self)._onLoading()
        with self.viewModel.transaction() as vm:
            vm.setStatisticsMode(self.__params['statisticsMode'])
            vm.setWinRate(self.__params['winRate'])
            vm.setWinsCount(self.__params['winsCount'])
            vm.setLossCount(self.__params['lossCount'])
            vm.setDrawCount(self.__params['drawCount'])
