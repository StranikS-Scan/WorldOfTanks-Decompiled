# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/research/buy_module_dialog_view.py
import logging
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.common.format_resource_string_arg_model import FormatResourceStringArgModel
from gui.impl.gen.view_models.views.lobby.research.buy_module_dialog_view_model import BuyModuleDialogViewModel, MountDisabledReason, ModuleType
from gui.impl.gen.view_models.views.lobby.research.sold_module_info_tooltip_model import SoldModuleInfoTooltipModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.impl.pub import ViewImpl
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from gui.shared.gui_items.items_actions.actions import BuyAndInstallWithOptionalSellItemAction as BuyModuleAction
from gui.shared.items_parameters.params_cache import g_paramsCache
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from gui.impl.gen.view_models.views.lobby.research.insufficient_credits_tooltip_model import InsufficientCreditsTooltipModel
_logger = logging.getLogger(__name__)

class BuyModuleDialogView(FullScreenDialogView):
    __slots__ = ('_module', '_previousModule', '_returnedData', '_currency', '_isAutoSellEnabled', '_mountDisabledReason')
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, module, previousModule, currency, mountDisabledReason):
        self._module = module
        self._previousModule = previousModule
        self._returnedData = {BuyModuleAction.AUTO_SELL_KEY: False}
        self._currency = currency
        self._mountDisabledReason = mountDisabledReason
        self._isAutoSellEnabled = self.lobbyContext.getServerSettings().isAutoSellCheckBoxEnabled() and self._mayInstall()
        settings = ViewSettings(layoutID=R.views.lobby.research.BuyModuleDialogView(), model=BuyModuleDialogViewModel())
        super(BuyModuleDialogView, self).__init__(settings)

    def createToolTipContent(self, event, contentID):
        _logger.debug('BuyModule::createToolTipContent')
        if contentID == R.views.lobby.research.InsufficientCreditsTooltip():
            missingAmount = event.getArgument('missingAmount')
            model = InsufficientCreditsTooltipModel()
            model.setMissingAmount(missingAmount)
            return ViewImpl(ViewSettings(contentID, model=model))
        if contentID == R.views.lobby.research.SoldModuleInfoTooltip():
            model = SoldModuleInfoTooltipModel()
            array = model.getCompatibleTanks()
            compatibleVehicles = set(g_paramsCache.getComponentVehiclesNames(self._previousModule.descriptor.compactDescr))
            _logger.debug('[BuyModuleView] Compatible vehicles: %s', compatibleVehicles)
            array.reserve(len(compatibleVehicles))
            for name in compatibleVehicles:
                array.addString(name)

            return ViewImpl(ViewSettings(contentID, model=model))
        return super(BuyModuleDialogView, self).createToolTipContent(event=event, contentID=contentID)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _mayInstall(self):
        return self._mountDisabledReason is None

    def _setItemPrices(self, model):
        moduleBuyPrice = self._module.getBuyPrice(preferred=False).price.get(self._currency)
        moduleSellPrice = self._previousModule.getSellPrice().price.get(self._currency)
        model.setModulePrice(moduleBuyPrice)
        if moduleSellPrice is not None:
            model.setPreviousModulePrice(moduleSellPrice)
        return

    def _setItemType(self, model):
        moduleTypeName = self._module.itemTypeName
        if moduleTypeName == FITTING_TYPES.VEHICLE_CHASSIS and self._module.isWheeledChassis():
            moduleTypeName = FITTING_TYPES.VEHICLE_WHEELED_CHASSIS
        moduleTypeEnum = ModuleType(moduleTypeName)
        model.setModuleType(moduleTypeEnum)

    def _setTitleArgs(self, arrModel, frmtArgs):
        for name, resource in frmtArgs:
            frmtModel = FormatResourceStringArgModel()
            frmtModel.setName(name)
            frmtModel.setValue(resource)
            arrModel.addViewModel(frmtModel)

    def _setTitleBody(self, model):
        label = 'confirmBuyAndInstall' if self._mayInstall() else 'confirmBuy'
        model.setTitleBody(R.strings.dialogs.dyn(label).title())

    def _setTitle(self, model):
        self._setTitleBody(model)
        self._setTitleArgs(model.getTitleArgs(), (('moduleName', self._module.userName),))

    def _setMountDisabledReason(self, model):
        reason = 'none' if self._mayInstall() else self._mountDisabledReason
        reasonEnum = MountDisabledReason('invalid')
        try:
            reasonEnum = MountDisabledReason(reason)
        except ValueError as e:
            _logger.error('[BuyModuleView] Unexpected string received for "reason" why module cannot be installed. ViewModel property will be set to MountDisabledReason.Invalid: %s', e)

        model.setMountDisabledReason(reasonEnum)

    def _setBaseParams(self, model):
        super(BuyModuleDialogView, self)._setBaseParams(model)
        self._setItemType(model)
        self._setItemPrices(model)
        model.setPreviousModuleName(self._previousModule.userName)
        model.setAutoSellEnabled(self._isAutoSellEnabled)
        self._setTitle(model)
        self._setMountDisabledReason(model)
        model.setAcceptButtonText(R.strings.dialogs.confirmBuyAndInstall.submit())
        model.setCancelButtonText(R.strings.dialogs.confirmBuyAndInstall.cancel())

    @args2params(bool)
    def _onAcceptClicked(self, sellPreviousModule):
        _logger.debug('[BuyModuleView] in _onAcceptClicked - sellPreviousModule %s', sellPreviousModule)
        if self._isAutoSellEnabled:
            self._returnedData = {BuyModuleAction.AUTO_SELL_KEY: sellPreviousModule}
        super(BuyModuleDialogView, self)._onAcceptClicked()

    def _getAdditionalData(self):
        return self._returnedData
