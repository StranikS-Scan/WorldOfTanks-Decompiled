# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/dialogs/marketplace/market_purchase_dialog.py
from frameworks.wulf import ViewSettings
from gui.game_control.wallet import WalletController
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resource_model import NyResourceModel
from gui.impl.gen.view_models.views.lobby.new_year.dialogs.marketplace.market_purchase_dialog_model import MarketPurchaseDialogModel
from gui.impl.gen.view_models.views.lobby.new_year.ny_constants import Resource
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.lobby.new_year.marketplace import getMarketRewards, getSettingsName, bonusChecker
from gui.impl.new_year.new_year_helper import backportTooltipDecorator
from gui.impl.pub.dialog_window import DialogButtons
from helpers import dependency
from new_year.ny_marketplace_helper import getNYMarketplaceConfig
from skeletons.gui.game_control import IWalletController
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController

class MarketPurchaseDialogView(FullScreenDialogBaseView):
    __slots__ = ('_tooltips', '__yearName', '__resource', '__kitId')
    _itemsCache = dependency.descriptor(IItemsCache)
    _nyController = dependency.descriptor(INewYearController)
    _wallet = dependency.descriptor(IWalletController)

    def __init__(self, yearName, kitId, resource, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.dialogs.marketplace.MarketPurchaseDialog())
        settings.args = args
        settings.kwargs = kwargs
        settings.model = MarketPurchaseDialogModel()
        self._tooltips = {}
        self.__yearName = yearName
        self.__resource = resource
        self.__kitId = kitId
        super(MarketPurchaseDialogView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(MarketPurchaseDialogView, self).getViewModel()

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(MarketPurchaseDialogView, self).createToolTip(event)

    def _onLoading(self, *args, **kwargs):
        super(MarketPurchaseDialogView, self)._onLoading(args, kwargs)
        collectionDistributions = self._itemsCache.items.festivity.getCollectionDistributions()
        config = getNYMarketplaceConfig()
        item = config.getCategoryItem(self.__yearName, self.__kitId)
        if item is None:
            return
        else:
            kitRewards = getMarketRewards(item, isMerge=True)
            self.__updateBalance()
            with self.viewModel.transaction() as model:
                rewards = model.getRewards()
                rewards.clear()
                for index, (bonus, tooltip) in enumerate(kitRewards):
                    tooltipId = str(index)
                    bonus.setTooltipId(tooltipId)
                    bonus.setIndex(index)
                    self._tooltips[tooltipId] = tooltip
                    rewards.addViewModel(bonus)

                rewards.invalidate()
                model.setCollectionNameAndYear('{}_{}'.format(getSettingsName(item), self.__yearName))
                model.setPrice(item.getPrice())
                model.setPriceWithDiscount(item.getTotalPrice(collectionDistributions, bonusChecker))
                model.setResourceType(self.__resource.value)
                currencyStatus = self._wallet.dynamicComponentsStatuses.get(self.__resource.value)
                model.setIsWalletAvailable(currencyStatus == WalletController.STATUS.AVAILABLE)
            return

    def _finalize(self):
        self._tooltips.clear()
        super(MarketPurchaseDialogView, self)._finalize()

    def _subscribe(self):
        super(MarketPurchaseDialogView, self)._subscribe()
        self.viewModel.onAccept += self._onAccept
        self.viewModel.onCancel += self._onCancel
        self._nyController.currencies.onBalanceUpdated += self.__onBalanceUpdated
        self._wallet.onWalletStatusChanged += self.__onWalletStatusChanged

    def _unsubscribe(self):
        self.viewModel.onAccept -= self._onAccept
        self.viewModel.onCancel -= self._onCancel
        self._nyController.currencies.onBalanceUpdated -= self.__onBalanceUpdated
        self._wallet.onWalletStatusChanged -= self.__onWalletStatusChanged
        super(MarketPurchaseDialogView, self)._unsubscribe()

    def __updateBalance(self):
        with self.viewModel.transaction() as model:
            resources = model.getResources()
            resources.clear()
            for res in Resource:
                resourceViewModel = NyResourceModel()
                resourceViewModel.setType(res.value)
                resourceViewModel.setValue(self._nyController.currencies.getResouceBalance(res.value))
                resources.addViewModel(resourceViewModel)

            resources.invalidate()

    def __onBalanceUpdated(self):
        self.__updateBalance()

    def __onWalletStatusChanged(self, _):
        with self.viewModel.transaction() as model:
            currencyStatus = self._wallet.dynamicComponentsStatuses.get(self.__resource.value)
            model.setIsWalletAvailable(currencyStatus == WalletController.STATUS.AVAILABLE)

    def _onAccept(self):
        self._setResult(DialogButtons.SUBMIT)

    def _onCancel(self):
        self._setResult(DialogButtons.CANCEL)
