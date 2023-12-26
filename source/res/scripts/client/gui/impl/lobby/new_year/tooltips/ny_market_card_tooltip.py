# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_market_card_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_market_card_tooltip_model import NyMarketCardTooltipModel
from gui.impl.lobby.new_year.marketplace import bonusChecker
from gui.impl.pub import ViewImpl
from helpers import dependency
from new_year.ny_marketplace_helper import getNYMarketplaceConfig
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController

class NyMarketCardTooltip(ViewImpl):
    __slots__ = ()
    __itemsCache = dependency.descriptor(IItemsCache)
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyMarketCardTooltip())
        settings.model = NyMarketCardTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyMarketCardTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyMarketCardTooltip, self).getViewModel()

    def _onLoading(self, kitState, kitName, yearName, kitIdx, resourceType, prevNYLevel, currentToysCount, totalToysCount):
        config = getNYMarketplaceConfig()
        item = config.getCategoryItem(yearName, kitIdx)
        with self.viewModel.transaction() as model:
            model.setKitState(kitState)
            model.setKitName(kitName)
            model.setCurrentTabName(yearName)
            collectionDistributions = self.__itemsCache.items.festivity.getCollectionDistributions()
            prevNYLevel = self.__itemsCache.items.festivity.getPrevNYLevel()
            priceWithDiscount = item.getTotalPrice(collectionDistributions, bonusChecker, prevNYLevel)
            balance = self.__nyController.currencies.getResouceBalance(resourceType)
            model.setPrice(item.getPrice())
            model.setPriceWithDiscount(priceWithDiscount)
            model.setDiscount(item.calculateDiscount(collectionDistributions, bonusChecker, prevNYLevel))
            model.setNotEnoughResource(priceWithDiscount > balance)
            model.setPrevNYLevel(prevNYLevel)
            model.setCurrentToysCount(currentToysCount)
            model.setTotalToysCount(totalToysCount)
