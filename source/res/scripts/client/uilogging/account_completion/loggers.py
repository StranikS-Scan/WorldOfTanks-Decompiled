# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/account_completion/loggers.py
import typing
from frameworks.wulf import Window, WindowLayer
from gui.impl.gen.view_models.views.dialogs.dialog_template_view_model import DialogTemplateViewModel
from gui.impl.lobby.account_completion.curtain.curtain_view import CurtainWindow
from gui.impl.pub.dialog_window import DialogButtons
from helpers import dependency
from skeletons.gui.game_control import IBootcampController, IDemoAccCompletionController
from skeletons.gui.impl import IGuiLoader
from uilogging.account_completion.constants import FEATURE, LogActions, LogGroup, ViewClosingResult
from uilogging.base.logger import BaseLogger, ifUILoggingEnabled
from uilogging.base.mixins import TimedActionMixin
from uilogging.core.core_constants import LogLevels
from wotdecorators import noexcept
if typing.TYPE_CHECKING:
    from typing import Callable, Optional
    from frameworks.wulf.windows_system.windows_manager import WindowsManager
_TOOLTIP_TIME_LIMIT = 2.0
_DIALOG_ACTIONS = {DialogButtons.SUBMIT: LogActions.CONFIRM_CLICKED,
 DialogButtons.CANCEL: LogActions.CANCEL_CLICKED,
 DialogTemplateViewModel.ESCAPE: LogActions.ESCAPE_PRESSED,
 DialogTemplateViewModel.DEFAULT: LogActions.CLOSE_CLICKED}

def windowPredicate(parentWindow):

    def func(wnd):
        return wnd.layer in (WindowLayer.WINDOW, WindowLayer.TOP_WINDOW) and wnd != parentWindow

    return func


class AccountCompletionBaseLogger(BaseLogger):

    def __init__(self, group):
        super(AccountCompletionBaseLogger, self).__init__(FEATURE, group.value)

    @noexcept
    @ifUILoggingEnabled()
    def log(self, action, loglevel=LogLevels.INFO, **params):
        super(AccountCompletionBaseLogger, self).log(action.value, loglevel, **params)


class AccountCompletionViewLogger(TimedActionMixin, AccountCompletionBaseLogger):
    _guiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self, group):
        super(AccountCompletionViewLogger, self).__init__(group)
        self._parentWindow = None
        self._isViewOpened = False
        self._params = {}
        return

    @property
    def windowsManager(self):
        return self._guiLoader.windowsManager

    @noexcept
    @ifUILoggingEnabled()
    def viewOpened(self, parentWindow=None, result=ViewClosingResult.CLOSED, **params):
        if self._isViewOpened:
            return
        params.update(result=result)
        self.setParams(**params)
        self._isViewOpened = True
        self._parentWindow = parentWindow
        self.windowsManager.onWindowStatusChanged += self._windowStatusChangeHandler
        self.startAction(LogActions.CLOSED)

    @noexcept
    def viewClosed(self, **kwargs):
        if not self._isViewOpened:
            return
        else:
            self._isViewOpened = False
            self.windowsManager.onWindowStatusChanged -= self._windowStatusChangeHandler
            params = dict(self._params)
            params.update(kwargs)
            self.stopAction(LogActions.CLOSED, **params)
            self.reset()
            self._params = {}
            self._parentWindow = None
            return

    @noexcept
    def _windowStatusChangeHandler(self, *_):
        if self._parentWindow is None:
            return
        else:
            windows = self.windowsManager.findWindows(windowPredicate(self._parentWindow))
            if windows:
                self.suspend(LogActions.CLOSED)
            else:
                self.resume(LogActions.CLOSED)
            return

    def setParams(self, **kwargs):
        self._params.update(kwargs)


class AccountCompletionRenamingLogger(AccountCompletionViewLogger):
    _bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self):
        super(AccountCompletionRenamingLogger, self).__init__(LogGroup.NICKNAME)

    @noexcept
    @ifUILoggingEnabled()
    def log(self, action, **params):
        super(AccountCompletionRenamingLogger, self).log(action, is_bootcamp=self._bootcampController.isInBootcamp(), **params)


class AccountCompletionSkipRenamingLogger(AccountCompletionBaseLogger):

    def __init__(self):
        super(AccountCompletionSkipRenamingLogger, self).__init__(LogGroup.SKIP_NICKNAME_DIALOG)

    @noexcept
    @ifUILoggingEnabled()
    def logDialogResult(self, result):
        action = _DIALOG_ACTIONS.get(result)
        if action:
            self.log(action)


class AccountCompletionMenuLogger(AccountCompletionBaseLogger):
    demoAccController = dependency.descriptor(IDemoAccCompletionController)

    def __init__(self):
        super(AccountCompletionMenuLogger, self).__init__(LogGroup.MENU)

    @property
    def curtainKey(self):
        from gui.impl.lobby.account_completion.demo_add_credentials_overlay_view import DemoAddCredentialsOverlayView
        from gui.impl.lobby.account_completion.demo_complete_overlay_view import DemoCompleteOverlayView
        from gui.impl.lobby.account_completion.demo_confirm_credentials_overlay_view import DemoConfirmCredentialsOverlayView
        curtainActiveSubView = CurtainWindow.getInstance().getActiveSubView()
        if isinstance(curtainActiveSubView, DemoAddCredentialsOverlayView):
            return LogGroup.CREDENTIALS
        elif isinstance(curtainActiveSubView, DemoConfirmCredentialsOverlayView):
            return LogGroup.CONFIRM
        else:
            return LogGroup.COMPLETE if isinstance(curtainActiveSubView, DemoCompleteOverlayView) else None

    @noexcept
    @ifUILoggingEnabled()
    def log(self, action, loglevel=LogLevels.INFO, **params):
        if self.demoAccController.isDemoAccount and self.curtainKey:
            super(AccountCompletionMenuLogger, self).log(action, loglevel, curtain=self.curtainKey, **params)


class AccountCompletionLobbyHeaderLogger(AccountCompletionBaseLogger):

    def __init__(self):
        super(AccountCompletionLobbyHeaderLogger, self).__init__(LogGroup.PLAYER_NAME)
        self.canRename = False

    def logShowDashboard(self):
        if self.canRename:
            self.log(LogActions.CLICKED)
