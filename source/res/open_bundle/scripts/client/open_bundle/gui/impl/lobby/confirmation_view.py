# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/gui/impl/lobby/confirmation_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.common.price_item_model import PriceItemModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.money import Currency
from helpers import dependency
from open_bundle.gui.impl.gen.view_models.views.lobby.confirmation_model import ConfirmationModel
from open_bundle.skeletons.open_bundle_controller import IOpenBundleController
from shared_utils import first
from skeletons.gui.shared import IItemsCache

class ConfirmationView(FullScreenDialogBaseView):
    __itemsCache = dependency.descriptor(IItemsCache)
    __openBundle = dependency.descriptor(IOpenBundleController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.open_bundle.mono.lobby.confirmation())
        settings.model = ConfirmationModel()
        settings.args = args
        settings.kwargs = kwargs
        super(ConfirmationView, self).__init__(settings)
        self.__additionalData = {}

    @property
    def viewModel(self):
        return super(ConfirmationView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.confirm, self.__confirm), (self.viewModel.cancel, self.__cancel))

    def _getCallbacks(self):
        return (('stats.{}'.format(c), self.__setBalance) for c in Currency.ALL)

    def _onLoading(self, bundleID, stepNumber, *args, **kwargs):
        super(ConfirmationView, self)._onLoading(*args, **kwargs)
        bundle = self.__openBundle.getBundle(bundleID=bundleID)
        with self.viewModel.transaction() as model:
            model.setBundleType(bundle.type)
            currency, value = first(bundle.steps[stepNumber].price.items())
            model.price.setName(currency)
            model.price.setValue(value)
            self.__setBalance(model=model)

    def _getAdditionalData(self):
        return self.__additionalData

    def __confirm(self):
        self._setResult(DialogButtons.SUBMIT)

    def __cancel(self):
        self.__additionalData['isUserCancelAction'] = True
        self._setResult(DialogButtons.CANCEL)

    @replaceNoneKwargsModel
    def __setBalance(self, value=None, model=None):
        statsModels = model.getBalance()
        statsModels.clear()
        for name in Currency.GUI_ALL:
            model = PriceItemModel()
            model.setName(name)
            model.setValue(int(self.__itemsCache.items.stats.money.getSignValue(name)))
            statsModels.addViewModel(model)

        model = PriceItemModel()
        model.setName(Currency.FREE_XP)
        model.setValue(self.__itemsCache.items.stats.freeXP)
        statsModels.addViewModel(model)
        statsModels.invalidate()
