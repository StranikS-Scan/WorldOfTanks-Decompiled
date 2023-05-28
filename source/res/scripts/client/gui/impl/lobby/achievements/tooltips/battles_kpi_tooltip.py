# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/achievements/tooltips/battles_kpi_tooltip.py
from helpers import dependency
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.achievements.tooltips.battles_kpi_tooltip_view_model import BattlesKpiTooltipViewModel
from gui.impl.lobby.achievements.profile_utils import formatPercent, getFormattedValue, getNormalizedValue
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from skeletons.gui.shared import IItemsCache

class BattlesKPITooltip(ViewImpl):
    __slots__ = ('__userId',)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, userId):
        settings = ViewSettings(R.views.lobby.achievements.tooltips.BattlesKPITooltip(), model=BattlesKpiTooltipViewModel())
        self.__userId = userId
        super(BattlesKPITooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattlesKPITooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattlesKPITooltip, self)._onLoading(*args, **kwargs)
        randomStats = self.__itemsCache.items.getAccountDossier(self.__userId).getRandomStats()
        with self.viewModel.transaction() as model:
            model.setWins(getFormattedValue(randomStats.getWinsCount()))
            model.setCountOfBattles(getFormattedValue(randomStats.getBattlesCount()))
            model.setDefeat(getFormattedValue(randomStats.getLossesCount()))
            model.setDraws(getFormattedValue(randomStats.getDrawsCount()))
            model.setWinsPercent(formatPercent(getNormalizedValue(randomStats.getWinsEfficiency()) * 100))
