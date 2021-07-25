# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/full_screen_dialog_view.py
import logging
from abc import abstractproperty
import typing
import constants
from PlayerEvents import g_playerEvents
from async import AsyncScope, AsyncEvent, await, async, BrokenPromiseError, AsyncReturn
from frameworks.wulf import WindowLayer
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.impl.backport import BackportTooltipWindow, createTooltipData
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
_logger = logging.getLogger(__name__)

class DIALOG_TYPES(object):
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    SIMPLE = 'simple'
    BLUEPRINTS_CONVERSION = 'blueprintsConversion'


class FullScreenDialogView(ViewImpl):
    __slots__ = ('__scope', '__event', '__result', '_stats')
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, settings):
        super(FullScreenDialogView, self).__init__(settings)
        self.__scope = AsyncScope()
        self.__event = AsyncEvent(scope=self.__scope)
        self.__result = DialogButtons.CANCEL
        self._stats = self._itemsCache.items.stats

    @abstractproperty
    def viewModel(self):
        pass

    def _getAdditionalData(self):
        return None

    @async
    def wait(self):
        try:
            yield await(self.__event.wait())
        except BrokenPromiseError:
            _logger.debug('%s has been destroyed without user decision', self)

        raise AsyncReturn(DialogResult(self.__result, self._getAdditionalData()))

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId in CURRENCIES_CONSTANTS.CURRENCIES_SET:
                specialAlias = tooltipId + 'StatsFullScreen' if constants.IS_SINGAPORE and tooltipId in CURRENCIES_CONSTANTS.SINGAPORE_ALTERNATIVE_CURRENCIES_SET else tooltipId + 'InfoFullScreen'
                window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=specialAlias, specialArgs=[]), self.getParentWindow())
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

    def _onLoaded(self, *args, **kwargs):
        super(FullScreenDialogView, self)._onLoaded()

    def _finalize(self):
        super(FullScreenDialogView, self)._finalize()
        self._removeListeners()
        self.__scope.destroy()

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
        self.__result = DialogButtons.SUBMIT
        self.__event.set()

    def _onCancelClicked(self):
        self._onCancel()

    def _onCancel(self):
        self.__result = DialogButtons.CANCEL
        self.__event.set()

    def _onExitClicked(self):
        self.__result = DialogButtons.EXIT
        self.__event.set()

    def _setTitleArgs(self, arrModel, frmtArgs):
        for name, resource in frmtArgs:
            frmtModel = FormatResourceStringArgModel()
            frmtModel.setName(name)
            frmtModel.setValue(resource)
            arrModel.addViewModel(frmtModel)

        arrModel.invalidate()

    def __setStats(self, model):
        model.setIsWGMAvailable(bool(self._stats.mayConsumeWalletResources))
        model.setCredits(int(self._stats.money.getSignValue(Currency.CREDITS)))
        model.setGolds(int(self._stats.money.getSignValue(Currency.GOLD)))
        model.setCrystals(int(self._stats.money.getSignValue(Currency.CRYSTAL)))
        model.setFreexp(self._stats.freeXP)


class FullScreenDialogWindowWrapper(LobbyWindow):
    __slots__ = ('_wrappedView', '_blur', '__blurLayers')
    __gui = dependency.descriptor(IGuiLoader)

    def __init__(self, wrappedView, parent=None, blurLayers=True, layer=WindowLayer.UNDEFINED):
        super(FullScreenDialogWindowWrapper, self).__init__(DialogFlags.TOP_FULLSCREEN_WINDOW, content=wrappedView, parent=parent, layer=layer)
        self._wrappedView = wrappedView
        self._blur = None
        self.__blurLayers = blurLayers
        return

    def _initialize(self):
        super(FullScreenDialogWindowWrapper, self)._initialize()
        if self.__blurLayers:
            self._blur = CachedBlur(enabled=True, ownLayer=self.layer - 1)

    def wait(self):
        return self._wrappedView.wait()

    @classmethod
    def createIfNotExist(cls, layoutID, wrappedViewClass, parent=None, blurLayers=True, layer=WindowLayer.UNDEFINED, *args, **kwargs):
        currentView = cls.__gui.windowsManager.getViewByLayoutID(layoutID)
        return FullScreenDialogWindowWrapper(wrappedViewClass(*args, **kwargs), parent, blurLayers, layer) if currentView is None else None

    def _finalize(self):
        if self._blur:
            self._blur.fini()
        super(FullScreenDialogWindowWrapper, self)._finalize()
