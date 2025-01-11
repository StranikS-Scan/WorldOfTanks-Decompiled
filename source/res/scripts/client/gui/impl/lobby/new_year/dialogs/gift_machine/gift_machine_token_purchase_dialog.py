# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/dialogs/gift_machine/gift_machine_token_purchase_dialog.py
from adisp import adisp_process
from frameworks.wulf import ViewSettings
from gui import SystemMessages
from gui.game_control.wallet import WalletController
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resource_model import NyResourceModel
from gui.impl.gen.view_models.views.lobby.new_year.dialogs.gift_machine.gift_machine_coin_purchase_dialog_model import GiftMachineCoinPurchaseDialogModel, DialogState
from gui.impl.lobby.new_year.tooltips.ny_resource_tooltip import NyResourceTooltip
from gui.impl.pub import ViewImpl
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from new_year.gift_machine_helper import getCoinPrice
from new_year.ny_constants import RESOURCES_ORDER
from new_year.ny_processor import BuyNyCoinProcessor
from skeletons.gui.game_control import IWalletController
from skeletons.new_year import INewYearController

class GiftMachineCoinPurchaseDialogView(ViewImpl):
    __nyController = dependency.descriptor(INewYearController)
    _wallet = dependency.descriptor(IWalletController)

    def __init__(self, layoutID, resourceType, amount, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.args = args
        settings.kwargs = kwargs
        settings.model = GiftMachineCoinPurchaseDialogModel()
        self.__blur = None
        self.__resourceType = resourceType
        self.__amount = amount
        super(GiftMachineCoinPurchaseDialogView, self).__init__(settings)
        return

    def _initialize(self, *args, **kwargs):
        super(GiftMachineCoinPurchaseDialogView, self)._initialize(*args, **kwargs)
        window = self.getParentWindow()
        self.__blur = CachedBlur(enabled=True, ownLayer=window.layer - 1)

    @property
    def viewModel(self):
        return super(GiftMachineCoinPurchaseDialogView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.NyResourceTooltip():
            resourceType = event.getArgument('type')
            return NyResourceTooltip(resourceType)
        return super(GiftMachineCoinPurchaseDialogView, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        events = super(GiftMachineCoinPurchaseDialogView, self)._getEvents()
        return events + ((self.viewModel.onAccept, self._onAccept),
         (self.viewModel.onCancel, self._onCancel),
         (self._wallet.onWalletStatusChanged, self.__updateWalletStatus),
         (self.__nyController.currencies.onBalanceUpdated, self.__onBalanceUpdated))

    def _onLoading(self, *args, **kwargs):
        super(GiftMachineCoinPurchaseDialogView, self)._onLoading(args, kwargs)
        with self.viewModel.transaction() as model:
            model.setDialogState(DialogState.DEFAULT)
            model.setTokenAmount(self.__amount)
            model.price.setType(self.__resourceType)
            model.price.setValue(getCoinPrice() * self.__amount)
            self.__updateBalance(model.getResources())
            self.__updateWalletStatus()

    def _finalize(self):
        self.__blur.fini()
        super(GiftMachineCoinPurchaseDialogView, self)._finalize()

    def _onAccept(self):
        self.viewModel.setDialogState(DialogState.PURCHASING)
        self.__buyCoins()

    def _onCancel(self):
        self.destroyWindow()

    def __onBalanceUpdated(self):
        self.__updateBalance(self.viewModel.getResources())

    def __updateBalance(self, model):
        model.clear()
        for res in RESOURCES_ORDER:
            amount = self.__nyController.currencies.getResouceBalance(res.value)
            resourceModel = NyResourceModel()
            resourceModel.setType(res.value)
            resourceModel.setValue(amount)
            model.addViewModel(resourceModel)

        model.invalidate()

    def __updateWalletStatus(self, *args):
        currencyStatus = self._wallet.dynamicComponentsStatuses.get(self.__resourceType)
        self.viewModel.setIsWalletAvailable(currencyStatus == WalletController.STATUS.AVAILABLE)

    @adisp_process
    def __buyCoins(self):
        result = yield BuyNyCoinProcessor(self.__resourceType, self.__amount).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType, priority=NotificationPriorityLevel.MEDIUM)
        if result.success:
            self.destroyWindow()
        else:
            self.viewModel.setDialogState(DialogState.ERROR)
