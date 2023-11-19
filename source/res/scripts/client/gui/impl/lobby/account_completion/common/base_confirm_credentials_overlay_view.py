# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/common/base_confirm_credentials_overlay_view.py
import time
from abc import abstractmethod
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.account_completion.confirm_credentials_model import ConfirmCredentialsModel
from gui.impl.lobby.account_completion.common.base_wgnp_overlay_view import BaseWGNPOverlayView
from gui.impl.lobby.account_completion.common.field_presenters import CodePresenter
from gui.impl.lobby.account_completion.utils.common import DISABLE_BUTTON_TIME
if typing.TYPE_CHECKING:
    from typing import Optional
res = R.strings.dialogs.accountCompletion

class BaseConfirmCredentialsOverlayView(BaseWGNPOverlayView):
    __slots__ = ('_email', '_code')
    _TITLE = res.activate.title()
    _LAYOUT_DYN_ACCESSOR = R.views.lobby.account_completion.ConfirmCredentialsView
    _VIEW_MODEL_CLASS = ConfirmCredentialsModel

    def __init__(self):
        super(BaseConfirmCredentialsOverlayView, self).__init__()
        self._code = CodePresenter(self.viewModel.field)
        self._email = ''

    @property
    def viewModel(self):
        return super(BaseConfirmCredentialsOverlayView, self).getViewModel()

    def activate(self, email='', *args, **kwargs):
        super(BaseConfirmCredentialsOverlayView, self).activate(*args, **kwargs)
        self._email = email
        with self.viewModel.transaction() as model:
            model.setEmail(email)
            model.setTimer(max(0, DISABLE_BUTTON_TIME - int(time.time()) + self._getEmailAddedTime()))
            model.setIsConfirmVisible(True)
            self._code.clear()
        self._updateConfirmButtonAvailability()
        self._code.onValueChanged += self._cleanNoTimerWarning
        self.viewModel.onResendClicked += self._onResend

    def deactivate(self):
        self._code.onValueChanged -= self._cleanNoTimerWarning
        self.viewModel.onResendClicked -= self._onResend
        super(BaseConfirmCredentialsOverlayView, self).deactivate()

    def _doFinalize(self):
        self._code.dispose()
        super(BaseConfirmCredentialsOverlayView, self)._doFinalize()

    def _updateConfirmButtonAvailability(self):
        self.viewModel.setIsConfirmEnabled(self._code.isValid)

    def _onLoading(self, *args, **kwargs):
        super(BaseConfirmCredentialsOverlayView, self)._onLoading(*args, **kwargs)
        self.viewModel.setResendButtonLabel(res.activate.button())

    def _cleanNoTimerWarning(self):
        self.viewModel.hold()
        if not self.viewModel.getWarningCountdown():
            self._setWarning()
        self._updateConfirmButtonAvailability()
        self.viewModel.commit()

    @abstractmethod
    def _getEmailAddedTime(self):
        raise NotImplementedError

    def _validateInput(self):
        return self._code.validate()

    def _updateErrorModel(self, errorMessage, buttonTimer=None, isButtonVisible=True, isButtonEnabled=True, resendButtonLabelResID=res.activate.button()):
        with self.viewModel.transaction() as model:
            if buttonTimer is not None:
                model.setTimer(buttonTimer)
            model.setResendButtonLabel(resendButtonLabelResID)
            model.setIsConfirmVisible(isButtonVisible)
            model.setIsConfirmEnabled(isButtonEnabled and not buttonTimer)
            model.field.setValue(self._code.value)
            model.field.setErrorMessage(backport.text(errorMessage))
        return

    @abstractmethod
    def _onResend(self):
        raise NotImplementedError
