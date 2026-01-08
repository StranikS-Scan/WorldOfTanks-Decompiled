# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/tooltips/damage_indicator_tooltip.py
from comp7.gui.impl.gen.view_models.views.lobby.tooltips.damage_indicator_tooltip_model import DamageIndicatorTooltipModel
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class DamageIndicatorTooltip(ViewImpl):
    __slots__ = ('__params',)

    def __init__(self, layoutID=R.views.comp7.mono.lobby.tooltips.damage_indicator_tooltip(), params=None):
        settings = ViewSettings(layoutID)
        settings.model = DamageIndicatorTooltipModel()
        super(DamageIndicatorTooltip, self).__init__(settings)
        self.__params = params

    @property
    def viewModel(self):
        return super(DamageIndicatorTooltip, self).getViewModel()

    def _onLoading(self):
        super(DamageIndicatorTooltip, self)._onLoading()
        with self.viewModel.transaction() as vm:
            vm.setStatisticsMode(self.__params['statisticsMode'])
            vm.setAverageDamageDealt(self.__params['averageDamageDealt'])
            vm.setRecordDamageDealt(self.__params['recordDamageDealt'])
            vm.setRecordDamageDealtVehicleName(self.__params['recordDamageDealtVehicleName'])
