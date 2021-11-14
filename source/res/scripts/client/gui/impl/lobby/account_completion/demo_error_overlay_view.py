# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/demo_error_overlay_view.py
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.account_completion.error_model import ErrorModel
from gui.impl.lobby.account_completion.common.base_overlay_view import BaseOverlayView
from gui.impl.lobby.account_completion.utils.common import DISABLE_BUTTON_TIME
from gui.platform.base.statuses.constants import StatusTypes
from gui.shared.event_dispatcher import showDemoCompleteOverlay
from helpers import dependency
from skeletons.gui.game_control import IDemoAccCompletionController
from skeletons.gui.platform.wgnp_controllers import IWGNPDemoAccRequestController

class DemoErrorOverlayView(BaseOverlayView):
    __slots__ = ()
    _IS_CLOSE_BUTTON_VISIBLE = False
    _LAYOUT_DYN_ACCESSOR = R.views.lobby.account_completion.ErrorView
    _VIEW_MODEL_CLASS = ErrorModel
    _demoAccController = dependency.descriptor(IDemoAccCompletionController)
    _wgnpDemoAccCtrl = dependency.descriptor(IWGNPDemoAccRequestController)

    @property
    def viewModel(self):
        return super(DemoErrorOverlayView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(DemoErrorOverlayView, self)._onLoading(*args, **kwargs)
        self.viewModel.setMessage(backport.text(R.strings.dialogs.accountCompletion.error.notAvailable()))
        self.viewModel.setButtonLabel(R.strings.dialogs.accountCompletion.error.button.tryAgain())

    def activate(self, *args, **kwargs):
        super(DemoErrorOverlayView, self).activate(*args, **kwargs)
        self.viewModel.onButtonClicked += self._buttonClickHandler
        self._wgnpDemoAccCtrl.statusEvents.subscribe(StatusTypes.CONFIRMED, self.__confirmedHandler)

    def deactivate(self):
        self._wgnpDemoAccCtrl.statusEvents.unsubscribe(StatusTypes.CONFIRMED, self.__confirmedHandler)
        self.viewModel.onButtonClicked -= self._buttonClickHandler
        super(DemoErrorOverlayView, self).deactivate()

    def _buttonClickHandler(self):
        self._setWaiting(True)
        self.viewModel.setTimer(0)
        self._demoAccController.updateOverlayState(onComplete=self._onRequestCompleted)

    def _onRequestCompleted(self):
        if not self.isActive:
            return
        self.viewModel.setTimer(DISABLE_BUTTON_TIME)
        self._setWaiting(False)

    def __confirmedHandler(self, *_):
        showDemoCompleteOverlay()
