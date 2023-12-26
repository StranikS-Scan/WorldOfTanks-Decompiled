# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/dialogs/resources_converter/resources_convert_dialog.py
from frameworks.wulf import ViewSettings
from gui.game_control.wallet import WalletController
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resource_model import NyResourceModel
from gui.impl.gen.view_models.views.lobby.new_year.dialogs.resources_converter.resources_convert_dialog_model import ResourcesConvertDialogModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.lobby.new_year.tooltips.ny_resource_tooltip import NyResourceTooltip
from gui.impl.lobby.new_year.tooltips.ny_market_lack_the_res_tooltip import NyMarketLackTheResTooltip
from helpers import dependency
from new_year.ny_constants import RESOURCES_ORDER
from skeletons.gui.game_control import IWalletController
from skeletons.new_year import INewYearController
from gui.impl.pub.dialog_window import DialogButtons

class ResourcesConvertDialogView(FullScreenDialogBaseView):
    __nyController = dependency.descriptor(INewYearController)
    __wallet = dependency.descriptor(IWalletController)
    __slots__ = ('__fromResourceType',)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.dialogs.converter.ResourcesConvertDialog())
        settings.args = args
        settings.kwargs = kwargs
        settings.model = ResourcesConvertDialogModel()
        self.__fromResourceType = ''
        super(ResourcesConvertDialogView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ResourcesConvertDialogView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.NyResourceTooltip():
            resourceType = event.getArgument('type')
            return NyResourceTooltip(resourceType)
        return NyMarketLackTheResTooltip(str(event.getArgument('resourceType')), int(event.getArgument('price'))) if contentID == R.views.lobby.new_year.tooltips.NyMarketLackTheResTooltip() else super(ResourcesConvertDialogView, self).createToolTipContent(event, contentID)

    def _onLoading(self, fromResourceType, fromValue, toResourceType, toValue, *args, **kwargs):
        super(ResourcesConvertDialogView, self)._onLoaded(args, kwargs)
        self.__fromResourceType = fromResourceType
        self.viewModel.onAccept += self._onAccept
        self.viewModel.onCancel += self._onCancel
        self.__nyController.currencies.onBalanceUpdated += self.__onBalanceUpdated
        self.__wallet.onWalletStatusChanged += self.__onWalletChanged
        self.__updateBalance()
        with self.viewModel.transaction() as model:
            model.resourceFrom.setType(fromResourceType)
            model.resourceFrom.setValue(fromValue)
            model.resourceTo.setType(toResourceType)
            model.resourceTo.setValue(toValue)
            currencyStatus = self.__wallet.dynamicComponentsStatuses.get(fromResourceType)
            model.setIsWalletAvailable(currencyStatus == WalletController.STATUS.AVAILABLE)

    def _finalize(self):
        self.viewModel.onAccept -= self._onAccept
        self.viewModel.onCancel -= self._onCancel
        self.__wallet.onWalletStatusChanged -= self.__onWalletChanged
        self.__nyController.currencies.onBalanceUpdated -= self.__onBalanceUpdated
        super(ResourcesConvertDialogView, self)._finalize()

    def _onAccept(self):
        self._setResult(DialogButtons.SUBMIT)

    def _onCancel(self):
        self._setResult(DialogButtons.CANCEL)

    def __onBalanceUpdated(self):
        self.__updateBalance()

    def __updateBalance(self):
        with self.viewModel.transaction() as model:
            resources = model.getResources()
            resources.clear()
            for resource in RESOURCES_ORDER:
                amount = self.__nyController.currencies.getResouceBalance(resource.value)
                resourceModel = NyResourceModel()
                resourceModel.setType(resource.value)
                resourceModel.setValue(amount)
                resources.addViewModel(resourceModel)

            resources.invalidate()

    def __onWalletChanged(self, _):
        if self.__fromResourceType:
            currencyStatus = self.__wallet.dynamicComponentsStatuses.get(self.__fromResourceType)
            self.viewModel.setIsWalletAvailable(currencyStatus == WalletController.STATUS.AVAILABLE)
