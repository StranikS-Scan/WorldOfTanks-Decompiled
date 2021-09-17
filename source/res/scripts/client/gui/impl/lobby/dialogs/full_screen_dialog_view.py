# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/full_screen_dialog_view.py
import logging
import typing
from PlayerEvents import g_playerEvents
from async import AsyncScope, AsyncEvent, await, async, BrokenPromiseError, AsyncReturn
from gui.impl.backport.backport_tooltip import BackportTooltipWindow, createTooltipData
from gui.impl.dialogs.dialog_template_utils import getCurrencyTooltipAlias
from gui.impl.gen import R
from gui.impl.gen.view_models.common.format_resource_string_arg_model import FormatResourceStringArgModel
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.dialog_window import DialogResult, DialogButtons, DialogFlags
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.money import Currency
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from frameworks import wulf
TViewModel = typing.TypeVar('TViewModel', bound=FullScreenDialogWindowModel)
_logger = logging.getLogger(__name__)

class FullScreenDialogBaseView(ViewImpl):
    __slots__ = ('__scope', '__event', '__result')
    BLUEPRINTS_CONVERSION = 'blueprintsConversion'

    def __init__(self, *args, **kwargs):
        super(FullScreenDialogBaseView, self).__init__(*args, **kwargs)
        self.__scope = AsyncScope()
        self.__event = AsyncEvent(scope=self.__scope)
        self.__result = DialogButtons.CANCEL

    @async
    def wait(self):
        try:
            yield await(self.__event.wait())
        except BrokenPromiseError:
            _logger.debug('%s has been destroyed without user decision', self)

        raise AsyncReturn(DialogResult(self.__result, self._getAdditionalData()))

    def _getAdditionalData(self):
        return None

    def _finalize(self):
        super(FullScreenDialogBaseView, self)._finalize()
        self.__scope.destroy()

    def _setResult(self, result):
        self.__result = result
        self.__event.set()


class FullScreenDialogView(FullScreenDialogBaseView, typing.Generic[TViewModel]):
    __slots__ = ('_stats',)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, settings):
        super(FullScreenDialogView, self).__init__(settings)
        self._stats = self._itemsCache.items.stats

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.dialogs.common.DialogTemplateGenericTooltip():
            currency = event.getArgument('currency')
            if currency is not None:
                window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=getCurrencyTooltipAlias(currency), specialArgs=[]), self.getParentWindow())
                window.load()
                return window
        return super(FullScreenDialogView, self).createToolTip(event)

    def _initialize(self):
        super(FullScreenDialogView, self)._initialize()
        self._addListeners()

    def _onInventoryResync(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            self.__setStats(model)

    def _setBaseParams(self, model):
        self.__setStats(model)

    def _onLoading(self, *args, **kwargs):
        super(FullScreenDialogView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self._setBaseParams(model)

    def _finalize(self):
        super(FullScreenDialogView, self)._finalize()
        self._removeListeners()

    def _addListeners(self):
        self.viewModel.onAcceptClicked += self._onAcceptClicked
        self.viewModel.onCancelClicked += self._onCancelClicked
        self.viewModel.onExit += self._onExitClicked
        self._itemsCache.onSyncCompleted += self._onInventoryResync
        g_playerEvents.onAccountBecomeNonPlayer += self.destroyWindow

    def _removeListeners(self):
        self.viewModel.onAcceptClicked -= self._onAcceptClicked
        self.viewModel.onCancelClicked -= self._onCancelClicked
        self.viewModel.onExit -= self._onExitClicked
        self._itemsCache.onSyncCompleted -= self._onInventoryResync
        g_playerEvents.onAccountBecomeNonPlayer -= self.destroyWindow

    def _onAcceptClicked(self):
        self._onAccept()

    def _onAccept(self):
        self._setResult(DialogButtons.SUBMIT)

    def _onCancelClicked(self):
        self._onCancel()

    def _onCancel(self):
        self._setResult(DialogButtons.CANCEL)

    def _onExitClicked(self):
        self._onCancel()

    def _setTitleArgs(self, arrModel, frmtArgs):
        for name, resource in frmtArgs:
            frmtModel = FormatResourceStringArgModel()
            frmtModel.setName(name)
            frmtModel.setValue(resource)
            arrModel.addViewModel(frmtModel)

        arrModel.invalidate()

    def __setStats(self, model):
        model.setCredits(int(self._stats.money.getSignValue(Currency.CREDITS)))
        model.setGolds(int(self._stats.money.getSignValue(Currency.GOLD)))
        model.setCrystals(int(self._stats.money.getSignValue(Currency.CRYSTAL)))
        model.setFreexp(self._stats.freeXP)
        model.setIsWalletAvailable(self._stats.mayConsumeWalletResources)


class FullScreenDialogWindowWrapper(LobbyWindow):
    __slots__ = ('_wrappedView', '_blur', '_doBlur')
    __gui = dependency.descriptor(IGuiLoader)

    def __init__(self, wrappedView, parent=None, doBlur=True):
        super(FullScreenDialogWindowWrapper, self).__init__(DialogFlags.TOP_FULLSCREEN_WINDOW, content=wrappedView, parent=parent)
        self._wrappedView = wrappedView
        self._blur = None
        self._doBlur = doBlur
        return

    def _initialize(self):
        super(FullScreenDialogWindowWrapper, self)._initialize()
        if self._doBlur:
            self._blur = CachedBlur(enabled=True, ownLayer=self.layer - 1)

    def wait(self):
        return self._wrappedView.wait()

    @classmethod
    def createIfNotExist(cls, layoutID, wrappedViewClass, parent=None, *args, **kwargs):
        currentView = cls.__gui.windowsManager.getViewByLayoutID(layoutID)
        return FullScreenDialogWindowWrapper(wrappedViewClass(*args, **kwargs), parent) if currentView is None else None

    def _finalize(self):
        if self._blur:
            self._blur.fini()
        super(FullScreenDialogWindowWrapper, self)._finalize()
