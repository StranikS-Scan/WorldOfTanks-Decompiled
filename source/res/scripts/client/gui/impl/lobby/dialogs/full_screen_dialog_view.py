# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/full_screen_dialog_view.py
import logging
import typing
from abc import abstractproperty
from PlayerEvents import g_playerEvents
from async import AsyncScope, AsyncEvent, await, async, BrokenPromiseError, AsyncReturn
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.dialog_window import DialogResult, DialogButtons, DialogFlags
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.money import Currency
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
        self._onCancel()

    def __setStats(self, model):
        model.setCredits(int(self._stats.money.getSignValue(Currency.CREDITS)))
        model.setGolds(int(self._stats.money.getSignValue(Currency.GOLD)))
        model.setCrystals(int(self._stats.money.getSignValue(Currency.CRYSTAL)))
        model.setFreexp(self._stats.freeXP)


class FullScreenDialogWindowWrapper(LobbyWindow):
    __slots__ = ('__wrappedView', '__blur', '__enableBlur')
    __gui = dependency.descriptor(IGuiLoader)

    def __init__(self, wrappedView, parent=None, enableBlur=True):
        super(FullScreenDialogWindowWrapper, self).__init__(DialogFlags.TOP_FULLSCREEN_WINDOW, None, content=wrappedView, parent=parent)
        self.__wrappedView = wrappedView
        self.__enableBlur = enableBlur
        self.__blur = None
        return

    def _initialize(self):
        super(FullScreenDialogWindowWrapper, self)._initialize()
        self.__blur = CachedBlur(enabled=self.__enableBlur, ownLayer=self.layer - 1)

    def wait(self):
        return self.__wrappedView.wait()

    @classmethod
    def createIfNotExist(cls, layoutID, wrappedViewClass, parent=None, *args, **kwargs):
        currentView = cls.__gui.windowsManager.getViewByLayoutID(layoutID)
        return FullScreenDialogWindowWrapper(wrappedViewClass(*args, **kwargs), parent) if currentView is None else None

    def _finalize(self):
        self.__blur.fini()
        super(FullScreenDialogWindowWrapper, self)._finalize()
