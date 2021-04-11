# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/email_overlay_view.py
from abc import ABCMeta, abstractmethod
import typing
import async
from frameworks.wulf import ViewStatus
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.account_completion.email_confirmation_curtain_model import EmailConfirmationCurtainModel
from gui.impl.lobby.account_completion.base_overlay_view import BaseOverlayView
from gui.platform.wgnp.controller import isAccountAlreadyHasEmail
from helpers import dependency
from skeletons.gui.platform.wgnp_controller import IWGNPRequestController
if typing.TYPE_CHECKING:
    from async import _Future

class EmailOverlayView(BaseOverlayView):
    __metaclass__ = ABCMeta
    _wgnpCtrl = dependency.descriptor(IWGNPRequestController)

    @property
    def viewModel(self):
        return super(EmailOverlayView, self).getViewModel()

    def _addListeners(self):
        super(EmailOverlayView, self)._addListeners()
        self.viewModel.field.onCleanError += self._onCleanError

    def _removeListeners(self):
        self.viewModel.field.onCleanError -= self._onCleanError
        super(EmailOverlayView, self)._removeListeners()

    def _fillModel(self, model):
        super(EmailOverlayView, self)._fillModel(model)
        model.setType(EmailConfirmationCurtainModel.NOTHING)

    @async.async
    def _onAccept(self, event):
        value = event.get('value', '')
        self.viewModel.setIsWaiting(True)
        response = yield async.await(self._doRequest(value))
        destroyed = self.viewStatus in (ViewStatus.DESTROYED, ViewStatus.DESTROYING)
        if destroyed or self.viewModel is None:
            return
        else:
            self.viewModel.setIsWaiting(False)
            if response.isSuccess():
                self._handleSuccess(value)
            else:
                self._handleError(value, response)
            return

    @abstractmethod
    def _doRequest(self, value):
        raise NotImplementedError

    def _handleSuccess(self, value):
        self._onCancel()

    def _handleError(self, value, response):
        if isAccountAlreadyHasEmail(response):
            self._showAccountAlreadyHasEmail()
        else:
            message = self._getErrorMessage(response)
            isUnavailable = message == R.invalid()
            with self.viewModel.transaction() as model:
                self._updateModel(model, value=value, isUnavailable=isUnavailable, errorMessage=message)

    def _getErrorMessage(self, response):
        return R.invalid()

    def _showAccountAlreadyHasEmail(self):
        with self.viewModel.transaction() as model:
            model.setType(EmailConfirmationCurtainModel.MESSAGE)
            model.setTitle(R.strings.dialogs.accountCompletion.emailOverlay.alreadyConfirmed.title())
            model.setSubTitle(R.strings.dialogs.accountCompletion.emailOverlay.alreadyConfirmed.subTitle())

    def _updateModel(self, model, value=None, isUnavailable=False, errorMessage=None):
        if value is not None:
            model.field.setValue(value)
        model.setIsServerUnavailable(isUnavailable)
        model.field.setErrorMessage(errorMessage or R.invalid())
        return

    def _onCleanError(self):
        with self.viewModel.transaction() as model:
            self._updateModel(model)
