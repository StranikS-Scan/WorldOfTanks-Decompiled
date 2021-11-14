# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/common/base_wgnp_overlay_view.py
from abc import ABCMeta, abstractmethod
import typing
import async
from gui.impl.gen import R
from gui.impl.lobby.account_completion.common.base_overlay_view import BaseOverlayView
from gui.impl.lobby.account_completion.curtain.curtain_view import CurtainWindow
if typing.TYPE_CHECKING:
    from async import _Future
    from gui.impl.gen.view_models.views.lobby.account_completion.common.base_wgnp_overlay_view_model import BaseWgnpOverlayViewModel

class BaseWGNPOverlayView(BaseOverlayView):
    __metaclass__ = ABCMeta
    __slots__ = ()
    _TITLE = R.invalid()
    _SUBTITLE = R.invalid()

    @property
    def viewModel(self):
        return super(BaseWGNPOverlayView, self).getViewModel()

    def activate(self, *args, **kwargs):
        super(BaseWGNPOverlayView, self).activate(*args, **kwargs)
        self.viewModel.onConfirmClicked += self._confirmClickedHandler
        self.viewModel.onWarningTimer += self._warningTimerHandler

    def deactivate(self):
        self.viewModel.onConfirmClicked -= self._confirmClickedHandler
        self.viewModel.onWarningTimer -= self._warningTimerHandler
        super(BaseWGNPOverlayView, self).deactivate()

    def _onLoading(self, *args, **kwargs):
        super(BaseWGNPOverlayView, self)._onLoading(*args, **kwargs)
        self.viewModel.setTitle(self._TITLE)
        self.viewModel.setSubTitle(self._SUBTITLE)

    @async.async
    def _confirmClickedHandler(self):
        if not self.isActive:
            return
        self.viewModel.setIsConfirmEnabled(False)
        if not self._validateInput():
            return
        self._setWaiting(True)
        response = yield async.await(self._doRequest())
        if not self.isActive:
            return
        self._setWaiting(False)
        self._updateConfirmButtonAvailability()
        if response.isSuccess():
            self._handleSuccess(response)
        else:
            self._handleError(response)

    def _warningTimerHandler(self):
        self._setWarning()
        self._updateConfirmButtonAvailability()

    @abstractmethod
    def _updateConfirmButtonAvailability(self):
        raise NotImplementedError

    @abstractmethod
    def _validateInput(self):
        raise NotImplementedError

    @abstractmethod
    def _doRequest(self):
        raise NotImplementedError

    def _handleSuccess(self, response):
        CurtainWindow.getInstance().close()

    @abstractmethod
    def _handleError(self, response):
        raise NotImplementedError

    def _setWarning(self, text='', countDown=0):
        with self.viewModel.transaction() as model:
            model.setWarningText(text)
            model.setWarningCountdown(countDown)
            model.setIsConfirmEnabled(not countDown)
