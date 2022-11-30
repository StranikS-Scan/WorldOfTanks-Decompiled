# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_resource_collector_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_resource_collector_tooltip_model import NyResourceCollectorTooltipModel
from gui.impl.pub import ViewImpl
from gui.shared.money import Currency
from helpers import dependency
from new_year.ny_constants import NyResourceCollectingStats
from new_year.ny_resource_collecting_helper import getAutoCollectingResourcesPrice, getFirstCollectingCooldownTime, getCollectingCooldownTime, getCollectingStats
from skeletons.gui.shared import IItemsCache

class NyResourceCollectorTooltip(ViewImpl):
    __slots__ = ()
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyResourceCollectorTooltip())
        settings.model = NyResourceCollectorTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyResourceCollectorTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyResourceCollectorTooltip, self).getViewModel()

    def _onLoading(self, collectorTooltipType, *args, **kwargs):
        super(NyResourceCollectorTooltip, self)._onLoading()
        stats = getCollectingStats()
        with self.viewModel.transaction() as model:
            model.setType(collectorTooltipType)
            model.setPrice(getAutoCollectingResourcesPrice())
            model.setCredits(int(self.__itemsCache.items.stats.money.getSignValue(Currency.CREDITS)))
            model.setCooldown(getCollectingCooldownTime())
            model.setSecondCollectCooldown(getFirstCollectingCooldownTime())
            model.setCollectedAmount(sum(stats.get(NyResourceCollectingStats.RESOURCES, {}).values()))
            model.setCreditsSpent(stats.get(NyResourceCollectingStats.SPENT_MONEY, {}).get(Currency.CREDITS, 0))

    def _finalize(self):
        pass
